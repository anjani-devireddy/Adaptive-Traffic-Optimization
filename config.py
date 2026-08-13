from pathlib import Path


# =========================================================
# Project paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "yolo11n.pt"


# =========================================================
# CCTV video sources
# =========================================================

VIDEO_PATHS = [
    r"C:\Users\GrokDrones\Downloads\2024-04-26 10-38-50.mp4",
    r"C:\Users\GrokDrones\Downloads\2024-04-23 10-31-54.mp4",
    r"C:\Users\GrokDrones\Downloads\2024-04-24 10-35-00.mp4",
    r"C:\Users\GrokDrones\Downloads\2024-04-30 15-59-50.mp4",
]


# =========================================================
# Camera configuration
# =========================================================

CAMERAS = {
    0: {
        "name": "North",
        "phase": 0,
    },
    1: {
        "name": "East",
        "phase": 1,
    },
    2: {
        "name": "South",
        "phase": 0,
    },
    3: {
        "name": "West",
        "phase": 1,
    },
}


# =========================================================
# YOLO configuration
# =========================================================

MODEL_CONFIDENCE = 0.35

# Image size used by YOLO.
# 640 gives better detection but is slower on CPU.
IMAGE_SIZE = 640

# 1 = process every frame
# 2 = process every second frame
FRAME_SKIP = 2

# CPU inference
DEVICE = "cpu"


# =========================================================
# Vehicle classes
# =========================================================

# COCO class IDs used by YOLO.

VEHICLE_CLASSES = {
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


# =========================================================
# Traffic weights
# =========================================================

VEHICLE_WEIGHTS = {
    "bicycle": 1,
    "motorcycle": 1,
    "car": 2,
    "bus": 5,
    "truck": 6,
}


# =========================================================
# Traffic signal configuration
# =========================================================

MIN_GREEN_TIME = 10
MAX_GREEN_TIME = 45

YELLOW_TIME = 3

TOTAL_CYCLE_TIME = 60


# =========================================================
# Runtime
# =========================================================

NUM_CAMERAS = len(VIDEO_PATHS)