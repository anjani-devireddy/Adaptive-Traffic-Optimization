import threading
import time

from flask import (
    Flask,
    render_template,
    jsonify,
)

import config
from detector import TrafficDetector
from signal_controller import SignalController
from database import (
    initialize_database,
    save_traffic_record,
)


app = Flask(__name__)

# =========================================================
# GLOBAL SYSTEM OBJECTS
# =========================================================

detector = None
signal_controller = None

system_running = False
system_lock = threading.Lock()


# =========================================================
# TRAFFIC PROCESSING LOOP
# =========================================================

def traffic_loop():

    global system_running

    print()
    print("=" * 60)
    print("ADAPTIVE TRAFFIC OPTIMIZATION")
    print("=" * 60)
    print("Starting traffic detection...")
    print()

    while system_running:

        try:

            # Get latest detection data
            traffic_data = (
                detector.get_traffic_data()
            )

            scores = []

            for data in traffic_data:

                scores.append(
                    data.get(
                        "weighted_score",
                        0
                    )
                )

            # Update adaptive signal controller
            signal_controller.update_traffic(
                scores
            )

            time.sleep(1)

        except Exception as e:

            print(
                "[Traffic Loop Error]",
                e
            )

            time.sleep(1)


# =========================================================
# START SYSTEM
# =========================================================

def start_system():

    global detector
    global signal_controller
    global system_running

    with system_lock:

        if system_running:
            return

        print("Initializing database...")

        initialize_database()

        print("Starting YOLO detectors...")

        detector = TrafficDetector(
            config.VIDEO_PATHS
        )

        detector.start()

        signal_controller = SignalController(
            config.NUM_CAMERAS
        )

        signal_controller.start()

        system_running = True

        threading.Thread(
            target=traffic_loop,
            daemon=True
        ).start()

        print()
        print("System started successfully.")
        print()


# =========================================================
# HOME / DASHBOARD
# =========================================================

@app.route("/")
def index():

    return render_template(
        "dashboard.html"
    )


# =========================================================
# LIVE TRAFFIC DATA
# =========================================================

@app.route("/traffic-data")
def traffic_data():

    if detector is None:

        return jsonify({
            "running": False,
            "cameras": [],
            "signals": {}
        })

    data = (
        detector.get_traffic_data()
    )

    signal_state = (
        signal_controller.get_state()
        if signal_controller
        else {}
    )

    cameras = []

    for i, item in enumerate(data):

        camera_info = config.CAMERAS.get(
            i,
            {}
        )

        # ---------------------------------------------
        # Current traffic measurements
        # ---------------------------------------------

        vehicle_count = item.get(
            "vehicle_count",
            0
        )

        weighted_score = item.get(
            "weighted_score",
            0
        )

        density = item.get(
            "density",
            0
        )

        # ---------------------------------------------
        # Current signal information
        # ---------------------------------------------

        signal_colors = signal_state.get(
            "signal_colors",
            ["Red"] * config.NUM_CAMERAS
        )

        signal_color = signal_colors[i]

        green_times = signal_state.get(
            "green_times",
            [0, 0]
        )

        phase = config.CAMERAS[i]["phase"]

        green_time = green_times[phase]

        # ---------------------------------------------
        # Build camera information for dashboard
        # ---------------------------------------------

        camera_data = {

            "camera_id": i,

            "name": camera_info.get(
                "name",
                f"Camera {i}"
            ),

            "vehicle_count": vehicle_count,

            "weighted_score": weighted_score,

            "density": density,

            "signal_color": signal_color,

            "green_time": green_time,
        }

        cameras.append(camera_data)

        # ---------------------------------------------
        # Save traffic information to database
        # ---------------------------------------------

        save_traffic_record(
            camera_id=i,
            vehicle_count=vehicle_count,
            weighted_score=weighted_score,
            density=density,
            green_time=green_time,
            signal_color=signal_color,
        )

    # ---------------------------------------------
    # Return dashboard data
    # ---------------------------------------------

    return jsonify({

        "running": system_running,

        "cameras": cameras,

        "signals": signal_state,

    })
    return jsonify({

        "running": system_running,

        "cameras": cameras,

        "signals": signal_state,

    })


# =========================================================
# CAMERA VIDEO STREAM
# =========================================================

@app.route("/cctv/<int:camera_id>")
def cctv(camera_id):

    if detector is None:

        return (
            "Detector not running",
            503
        )

    if (
        camera_id < 0
        or camera_id >= config.NUM_CAMERAS
    ):

        return (
            "Invalid camera",
            404
        )

    return detector.video_response(
        camera_id
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "ok",

        "system_running":
            system_running,

        "detector_running":
            detector is not None,

        "signal_controller_running":
            signal_controller is not None,

    })


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    start_system()

    print("=" * 60)
    print("DASHBOARD:")
    print("http://127.0.0.1:5000")
    print("=" * 60)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )