import time

from detector import (
    start_detectors,
    stop_event,
    data_lock,
    vehicle_counts,
)

from metrics import calculate_metrics

from signal_controller import SignalController

from config import NUM_CAMERAS


print()
print("=" * 60)
print("ADAPTIVE TRAFFIC SYSTEM TEST")
print("=" * 60)


# ---------------------------------------------------------
# Start YOLO cameras
# ---------------------------------------------------------

threads = start_detectors()

print()
print("YOLO detectors started.")
print("Collecting traffic data...")
print()


# ---------------------------------------------------------
# Create signal controller
# ---------------------------------------------------------

controller = SignalController(
    num_cameras=NUM_CAMERAS
)


try:

    # Give YOLO some time to produce detections.
    time.sleep(5)

    while True:

        traffic_scores = []

        print()
        print("=" * 60)

        # -------------------------------------------------
        # Calculate metrics for every camera
        # -------------------------------------------------

        with data_lock:

            counts_snapshot = [
                dict(count)
                for count in vehicle_counts
            ]

        for camera_id in range(NUM_CAMERAS):

            metrics = calculate_metrics(
                counts_snapshot[camera_id]
            )

            score = metrics[
                "weighted_score"
            ]

            traffic_scores.append(score)

            print(
                f"Camera {camera_id}: "
                f"{metrics['vehicle_count']} vehicles | "
                f"score={score} | "
                f"density={metrics['density']}"
            )

        # -------------------------------------------------
        # Update adaptive controller
        # -------------------------------------------------

        controller.update_traffic(
            traffic_scores
        )

        state = controller.get_state()

        print()
        print(
            "Traffic scores:",
            state["traffic_scores"]
        )

        print(
            "Green times:",
            state["green_times"]
        )

        print(
            "Current signals:",
            state["signal_colors"]
        )

        print()

        print(
            "Press Ctrl+C to stop."
        )

        time.sleep(3)


except KeyboardInterrupt:

    print()
    print("Stopping system...")


finally:

    stop_event.set()

    for thread in threads:

        thread.join(timeout=2)

    print("System stopped.")