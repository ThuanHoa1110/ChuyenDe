"""
FastAPI Inference Serving Application for Hanoi Multi-Station Weather Forecasting (Phase 4).
Exposes production-ready REST endpoints:
- GET  /health   : Service health check, model/scaler status, and uptime.
- GET  /metadata : Model architecture, station list, feature order, and evaluation metrics.
- POST /predict  : Validates 72-step multi-station meteorological inputs and serves 60-min temperature forecasts.
"""

import os
import sys
import time
import pickle
import datetime
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, Tuple

import numpy as np
import yaml
import torch
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.weather.data.image import (
    get_canonical_feature_order,
    window_to_3channel_matrix,
    resize_matrix_bilinear,
    STATION_ORDER,
    VARIABLE_ORDER
)
from src.weather.data.window import StandardFeatureScaler
from src.weather.models.dinov3_forecaster import DINOv3Forecaster

# Resolve base directories
DEFAULT_CHECKPOINT_PATH = os.path.join(BASE_DIR, "checkpoints", "dinov3_forecaster_best.pt")
DEFAULT_SCALER_PATH = os.path.join(BASE_DIR, "artifacts", "scaler.pkl")
DEFAULT_CONFIG_PATH = os.path.join(BASE_DIR, "configs", "dinov3.yaml")

CANONICAL_STATIONS = ["st01", "st02", "st03", "st04", "st05", "st06"]
LOOKBACK_STEPS = 72
HORIZON_STEPS = 12
HORIZON_MINUTES = 60
STEP_INTERVAL_SECONDS = 300  # 5 minutes


# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    uptime_seconds: float = Field(..., examples=[42.5])
    model_loaded: bool = Field(..., examples=[True])
    model_name: str = Field(..., examples=["DINOv3Forecaster"])
    model_checkpoint: str = Field(..., examples=["dinov3_forecaster_best.pt"])
    scaler_loaded: bool = Field(..., examples=[True])
    device: str = Field(..., examples=["cpu"])
    timestamp: str = Field(..., examples=["2026-11-06T06:30:00Z"])


class StationMetadata(BaseModel):
    id: str
    name: str
    target_variable: str
    district: str


class MetadataResponse(BaseModel):
    model_name: str
    model_version: str
    data_version: str
    task: str
    stations: List[StationMetadata]
    lookback_steps: int
    lookback_hours: int
    horizon_steps: int
    horizon_minutes: int
    step_interval_minutes: int
    num_features: int
    feature_order: List[str]
    units: Dict[str, str]
    metrics_summary: Dict[str, float]


class PredictRequest(BaseModel):
    end_timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp marking the end of the 6-hour lookback window.",
        examples=["2024-01-03T18:00:00Z"]
    )
    station_ids: List[str] = Field(
        ...,
        description="List of exactly 6 canonical stations in order: ['st01', 'st02', 'st03', 'st04', 'st05', 'st06'].",
        examples=[["st01", "st02", "st03", "st04", "st05", "st06"]]
    )
    timestamps: List[str] = Field(
        ...,
        description="List of exactly 72 ISO 8601 timestamps with consistent 5-minute intervals.",
        examples=[["2024-01-03T12:05:00Z", "2024-01-03T12:10:00Z"]]
    )
    units: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional dictionary specifying variable units."
    )
    data: Union[Dict[str, List[Optional[float]]], List[List[Optional[float]]]] = Field(
        ...,
        description="Either a dict of 66 features with 72 values each, or a 2D matrix (72 rows x 66 columns)."
    )
    missing_mask: Optional[Union[Dict[str, List[Union[int, bool]]], List[List[Union[int, bool]]]]] = Field(
        default=None,
        description="Optional mask (0/False = valid observation, 1/True = missing/imputed)."
    )


class PredictResponse(BaseModel):
    status: str = Field(..., examples=["success"])
    model_version: str = Field(..., examples=["v1.0.0"])
    data_version: str = Field(..., examples=["v1.0.0"])
    end_timestamp: str = Field(..., examples=["2024-01-03T18:00:00Z"])
    horizon_steps: int = Field(..., examples=[12])
    horizon_minutes: int = Field(..., examples=[60])
    target_timestamp: str = Field(..., examples=["2024-01-03T19:00:00Z"])
    predictions: Dict[str, float] = Field(
        ...,
        examples=[{
            "st01_hoankiem": 21.45,
            "st02_badinh": 21.32,
            "st03_caugiay": 21.58,
            "st04_hadong": 21.65,
            "st05_donganh": 21.10,
            "st06_socson": 20.95
        }]
    )
    units: str = Field(..., examples=["°C"])
    latency_ms: float = Field(..., examples=[1.25])


# ---------------------------------------------------------
# Application Lifespan & Global State
# ---------------------------------------------------------

class ServingState:
    def __init__(self):
        self.start_time: float = time.time()
        self.model: Optional[DINOv3Forecaster] = None
        self.scaler: Any = None
        self.device: torch.device = torch.device("cpu")
        self.checkpoint_path: str = ""
        self.scaler_path: str = ""
        self.config: Dict[str, Any] = {}
        self.canonical_features: List[str] = get_canonical_feature_order()


state = ServingState()


def load_resources():
    """Loads configuration, scaler, and trained model weights into global state once at startup."""
    print("⏳ [Startup] Đang khởi tạo mô hình và bộ chuẩn hóa scaler...")

    # 1. Config
    config_path = os.environ.get("CONFIG_PATH", DEFAULT_CONFIG_PATH)
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            state.config = yaml.safe_load(f)
    else:
        state.config = {
            "model": {
                "backbone": "vit_small",
                "hidden_size": 384,
                "freeze_backbone": True,
                "head": {"num_stations": 6}
            }
        }

    # 2. Device selection
    if torch.cuda.is_available():
        state.device = torch.device("cuda")
    else:
        state.device = torch.device("cpu")
    print(f"   Thiết bị phục vụ suy luận (Serving Device): {state.device}")

    # 3. Scaler
    scaler_path = os.environ.get("SCALER_PATH", DEFAULT_SCALER_PATH)
    state.scaler_path = scaler_path
    if os.path.exists(scaler_path):
        with open(scaler_path, "rb") as f:
            obj = pickle.load(f)
        if isinstance(obj, dict):
            state.scaler = StandardFeatureScaler()
            state.scaler.mean_ = obj["mean"]
            state.scaler.scale_ = obj["scale"]
            state.scaler.columns_ = obj["columns"]
        else:
            state.scaler = obj
        print(f"   Đã nạp StandardScaler thành công từ: {scaler_path}")
    else:
        print(f"⚠️ Không tìm thấy scaler tại: {scaler_path}. Tạo mock scaler cho dev/test.")
        state.scaler = StandardFeatureScaler()
        state.scaler.mean_ = np.zeros(len(state.canonical_features), dtype=np.float64)
        state.scaler.scale_ = np.ones(len(state.canonical_features), dtype=np.float64)
        state.scaler.columns_ = state.canonical_features

    # 4. Model
    checkpoint_path = os.environ.get("MODEL_CHECKPOINT_PATH", DEFAULT_CHECKPOINT_PATH)
    state.checkpoint_path = checkpoint_path
    model_cfg = state.config.get("model", {})
    state.model = DINOv3Forecaster(model_cfg).to(state.device)

    if os.path.exists(checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location=state.device)
        if "model_state_dict" in checkpoint:
            state.model.load_state_dict(checkpoint["model_state_dict"])
        else:
            state.model.load_state_dict(checkpoint)
        print(f"   Đã nạp thành công weights từ checkpoint: {checkpoint_path}")
    else:
        print(f"⚠️ Cảnh báo: Không tìm thấy checkpoint tại {checkpoint_path}. Sử dụng trọng số khởi tạo ban đầu.")

    state.model.eval()
    for param in state.model.parameters():
        param.requires_grad = False

    print("✅ [Startup] Mô hình và Scaler đã sẵn sàng phục vụ suy luận.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    state.start_time = time.time()
    load_resources()
    yield
    # Shutdown phase
    print("🛑 [Shutdown] Đang giải phóng tài nguyên phục vụ...")
    state.model = None
    state.scaler = None


app = FastAPI(
    title="Hanoi Multi-Station Weather Forecasting API",
    description=(
        "Production-ready inference service for short-term multi-station temperature forecasting "
        "in Hanoi across 6 meteorological stations using DINOv3 spatial-temporal vision backbone."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for web dashboards and clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Helper Validation Functions
# ---------------------------------------------------------

def parse_iso_timestamp(ts_str: str) -> datetime.datetime:
    """Parses ISO 8601 timestamp string robustly."""
    try:
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        return datetime.datetime.fromisoformat(ts_str)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid ISO 8601 timestamp format: '{ts_str}'. Error: {exc}"
        )


def validate_prediction_payload(payload: PredictRequest) -> Tuple[np.ndarray, np.ndarray, datetime.datetime]:
    """
    Strictly validates incoming forecast request:
    1. Station list: Exactly 6 canonical stations in correct order.
    2. Timestamps: Exactly 72 timestamps, strictly monotonic, 5-minute step, end_timestamp match.
    3. Features matrix: Shape (72, 66), reasonable missing ratio, all finite or masked.
    Returns:
        (raw_matrix (72, 66), mask_matrix (72, 66), target_datetime)
    """
    # 1. Validate station_ids
    input_stations = [s.strip().lower() for s in payload.station_ids]
    if len(input_stations) != len(CANONICAL_STATIONS):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"station_ids must contain exactly {len(CANONICAL_STATIONS)} stations, got {len(input_stations)}: {input_stations}"
        )
    for idx, expected in enumerate(CANONICAL_STATIONS):
        if not input_stations[idx].startswith(expected):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"station_ids at index {idx} must be '{expected}' (or start with it), got '{input_stations[idx]}'. Canonical order: {CANONICAL_STATIONS}"
            )

    # 2. Validate timestamps
    if len(payload.timestamps) != LOOKBACK_STEPS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"timestamps must contain exactly {LOOKBACK_STEPS} timesteps (got {len(payload.timestamps)})."
        )

    parsed_ts = [parse_iso_timestamp(ts) for ts in payload.timestamps]
    parsed_end = parse_iso_timestamp(payload.end_timestamp)

    # Verify end_timestamp matches the final timestamp
    if parsed_ts[-1] != parsed_end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"end_timestamp '{payload.end_timestamp}' does not match the final timestamp in timestamps series '{payload.timestamps[-1]}'."
        )

    # Verify monotonic increasing and regular 5-minute interval
    for i in range(1, LOOKBACK_STEPS):
        delta = (parsed_ts[i] - parsed_ts[i - 1]).total_seconds()
        if delta <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Timestamps must be strictly monotonically increasing. Step {i-1} -> {i} has non-positive delta ({delta}s)."
            )
        if abs(delta - STEP_INTERVAL_SECONDS) > 60:  # Allow max 1 min drift
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Timestamps must have consistent 5-minute (300s) intervals. Step {i-1} -> {i} has interval of {delta}s."
            )

    # 3. Validate feature data shape & completeness
    canonical_features = state.canonical_features
    num_features = len(canonical_features)

    if isinstance(payload.data, dict):
        # Column-oriented dictionary
        for col in canonical_features:
            if col not in payload.data:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Missing required meteorological feature column: '{col}'"
                )
            if len(payload.data[col]) != LOOKBACK_STEPS:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Feature '{col}' must contain exactly {LOOKBACK_STEPS} values (got {len(payload.data[col])})."
                )
        raw_matrix = np.empty((LOOKBACK_STEPS, num_features), dtype=np.float32)
        for col_idx, col in enumerate(canonical_features):
            vals = [np.nan if v is None else float(v) for v in payload.data[col]]
            raw_matrix[:, col_idx] = vals

    elif isinstance(payload.data, list):
        # 2D Row-oriented matrix: 72 rows x 66 columns
        if len(payload.data) != LOOKBACK_STEPS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"data matrix must have exactly {LOOKBACK_STEPS} rows (got {len(payload.data)})."
            )
        raw_matrix = np.empty((LOOKBACK_STEPS, num_features), dtype=np.float32)
        for row_idx, row in enumerate(payload.data):
            if len(row) != num_features:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"data matrix row {row_idx} must have exactly {num_features} columns (got {len(row)})."
                )
            vals = [np.nan if v is None else float(v) for v in row]
            raw_matrix[row_idx, :] = vals
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Payload data must be either a feature dictionary or a 2D matrix."
        )

    # Check infinite values
    if np.isinf(raw_matrix).any():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="data contains non-finite infinite (inf) values which are prohibited."
        )

    # Missing value handling & mask check
    nan_mask = np.isnan(raw_matrix)
    nan_ratio = np.sum(nan_mask) / (LOOKBACK_STEPS * num_features)
    if nan_ratio > 0.50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Missing values ratio ({nan_ratio:.1%}) exceeds maximum tolerance threshold (50%)."
        )

    # Build mask matrix (1.0 = valid, 0.0 = missing)
    mask_matrix = (~nan_mask).astype(np.float32)

    # If explicit missing_mask provided, incorporate it
    if payload.missing_mask is not None:
        if isinstance(payload.missing_mask, dict):
            for col_idx, col in enumerate(canonical_features):
                if col in payload.missing_mask:
                    user_mask = np.array([1.0 if v in (1, True, "1") else 0.0 for v in payload.missing_mask[col]])
                    # Invert if user gave 1 for missing:
                    mask_matrix[:, col_idx] = np.where(user_mask == 1.0, 0.0, mask_matrix[:, col_idx])
        elif isinstance(payload.missing_mask, list):
            if len(payload.missing_mask) == LOOKBACK_STEPS and len(payload.missing_mask[0]) == num_features:
                user_mask = np.array(payload.missing_mask, dtype=np.float32)
                mask_matrix = np.where(user_mask == 1.0, 0.0, mask_matrix)

    # Impute NaNs in raw_matrix with 0.0 or train mean for scaling
    clean_raw_matrix = np.nan_to_num(raw_matrix, nan=0.0)

    target_dt = parsed_end + datetime.timedelta(minutes=HORIZON_MINUTES)
    return clean_raw_matrix, mask_matrix, target_dt


# ---------------------------------------------------------
# REST Endpoints
# ---------------------------------------------------------

@app.get("/", summary="Root Web Dashboard", include_in_schema=False)
def root_index():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {
        "message": "Hanoi Multi-Station Weather Forecasting API (DINOv3)",
        "docs": "/docs",
        "health": "/health",
        "metadata": "/metadata"
    }


@app.get("/health", response_model=HealthResponse, summary="Service Health & Diagnostic Status")
def health_check():
    """Returns uptime, model and scaler readiness, and compute device."""
    uptime = time.time() - state.start_time
    is_model_ready = state.model is not None
    is_scaler_ready = state.scaler is not None

    return HealthResponse(
        status="healthy" if (is_model_ready and is_scaler_ready) else "degraded",
        uptime_seconds=round(uptime, 2),
        model_loaded=is_model_ready,
        model_name="DINOv3Forecaster",
        model_checkpoint=os.path.basename(state.checkpoint_path) if state.checkpoint_path else "none",
        scaler_loaded=is_scaler_ready,
        device=str(state.device),
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


@app.get("/metadata", response_model=MetadataResponse, summary="Model Architecture & Benchmark Metadata")
def get_metadata():
    """Returns detailed metadata about stations, variables, lookback/horizon, and benchmark results."""
    station_meta = [
        StationMetadata(id="st01", name="ST01_HOANKIEM", target_variable="st01_temperature", district="Hoàn Kiếm"),
        StationMetadata(id="st02", name="ST02_BADINH", target_variable="st02_temperature", district="Ba Đình"),
        StationMetadata(id="st03", name="ST03_CAUGIAY", target_variable="st03_temperature", district="Cầu Giấy"),
        StationMetadata(id="st04", name="ST04_HADONG", target_variable="st04_temperature", district="Hà Đông"),
        StationMetadata(id="st05", name="ST05_DONGANH", target_variable="st05_temperature", district="Đông Anh"),
        StationMetadata(id="st06", name="ST06_SOCSON", target_variable="st06_temperature", district="Sóc Sơn")
    ]

    units = {
        "temperature": "°C",
        "humidity": "%",
        "dew_point": "°C",
        "apparent_temperature": "°C",
        "surface_pressure": "hPa",
        "precipitation": "mm",
        "cloud_cover": "%",
        "wind_speed_10m": "m/s",
        "wind_gusts_10m": "m/s",
        "solar_radiation": "W/m²",
        "direct_radiation": "W/m²"
    }

    metrics_summary = {
        "persistence_macro_mae": 1.0025,
        "persistence_macro_rmse": 1.0689,
        "ridge_macro_mae": 0.2185,
        "ridge_macro_rmse": 0.2712,
        "lightgbm_macro_mae": 0.2357,
        "lightgbm_macro_rmse": 0.2921,
        "dinov3_macro_mae": 1.5010,
        "dinov3_macro_rmse": 1.7229
    }

    return MetadataResponse(
        model_name="DINOv3Forecaster",
        model_version="v1.0.0",
        data_version="v1.0.0",
        task="Short-term multi-station temperature forecasting in Hanoi (t + 60 mins)",
        stations=station_meta,
        lookback_steps=LOOKBACK_STEPS,
        lookback_hours=6,
        horizon_steps=HORIZON_STEPS,
        horizon_minutes=HORIZON_MINUTES,
        step_interval_minutes=5,
        num_features=len(state.canonical_features),
        feature_order=state.canonical_features,
        units=units,
        metrics_summary=metrics_summary
    )


@app.post("/predict", response_model=PredictResponse, summary="Perform Multi-Station Temperature Forecast")
def predict_weather(payload: PredictRequest):
    """
    Inference endpoint:
    - Ingests 72 steps (6 hours) of multi-station meteorological inputs.
    - Normalizes with frozen StandardScaler.
    - Encodes inputs into 3-channel spatial-temporal image tensor (224x224).
    - Runs forward inference on DINOv3 Forecaster backbone.
    - Returns finite predicted temperatures for 6 Hanoi stations at t + 60 minutes.
    """
    t_start = time.perf_counter()

    if state.model is None or state.scaler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serving engine not initialized: Model or Scaler not loaded."
        )

    # 1. Validation and matrix extraction
    raw_matrix, mask_matrix, target_dt = validate_prediction_payload(payload)

    # 2. Scale features with frozen StandardScaler
    try:
        scaled_matrix = state.scaler.transform(raw_matrix).astype(np.float32)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Scaler transformation error: {exc}"
        )

    # 3. Encode to 3-channel spatial-temporal image tensor
    # (H=66 features, W=72 timesteps) -> (3, 224, 224)
    mat_3ch = window_to_3channel_matrix(scaled_matrix, state.canonical_features)
    if mask_matrix is not None:
        mat_3ch[2] = mask_matrix.T.astype(np.float32)
    image_tensor_np = resize_matrix_bilinear(mat_3ch, target_size=(224, 224))

    image_batch = torch.from_numpy(image_tensor_np).unsqueeze(0).to(state.device)

    # 4. Forward pass through DINOv3 Forecaster
    try:
        with torch.no_grad():
            preds_tensor = state.model(image_batch)
            preds_np = preds_tensor.cpu().numpy().squeeze(0)  # Shape (6,)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model forward pass inference error: {exc}"
        )

    # 5. Sanity check: Ensure finite real numbers
    if not np.all(np.isfinite(preds_np)):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model returned non-finite predictions (NaN or Inf)."
        )

    station_names = [
        "st01_hoankiem",
        "st02_badinh",
        "st03_caugiay",
        "st04_hadong",
        "st05_donganh",
        "st06_socson"
    ]
    predictions_dict = {
        st: round(float(preds_np[i]), 2)
        for i, st in enumerate(station_names)
    }

    latency = (time.perf_counter() - t_start) * 1000.0

    return PredictResponse(
        status="success",
        model_version="v1.0.0",
        data_version="v1.0.0",
        end_timestamp=payload.end_timestamp,
        horizon_steps=HORIZON_STEPS,
        horizon_minutes=HORIZON_MINUTES,
        target_timestamp=target_dt.isoformat(),
        predictions=predictions_dict,
        units="°C",
        latency_ms=round(latency, 2)
    )
