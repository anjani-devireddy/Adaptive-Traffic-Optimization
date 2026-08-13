import cv2
import threading
import time

from ultralytics import YOLO

import config
from metrics import calculate_traffic_metrics


class TrafficDetector:

    def __init__(self, video_paths):

        self.video_paths = video_paths

        self.num_cameras = len(video_paths)

        self.model = YOLO(
            str(config.MODEL_PATH)
        )

        self.caps = [None] * self.num_cameras

        self.frames = [None] * self.num_cameras

        self.traffic_data = [
            {
                "vehicle_count": 0,
                "weighted_score": 0,
                "density": 0,
                "queue_score": 0,
                "vehicle_counts": {},
            }
            for _ in range(self.num_cameras)
        ]

        self.locks = [
            threading.Lock()
            for _ in range(self.num_cameras)
        ]

        self.running = False

        self.threads = []

        self.frame_numbers = [
            0
            for _ in range(self.num_cameras)
        ]

    # =====================================================
    # START
    # =====================================================

    def start(self):

        if self.running:
            return

        self.running = True

        for camera_id in range(
            self.num_cameras
        ):

            thread = threading.Thread(
                target=self._camera_loop,
                args=(camera_id,),
                daemon=True,
            )

            thread.start()

            self.threads.append(thread)

        print("YOLO detectors started.")

    # =====================================================
    # CAMERA LOOP
    # =====================================================

    def _camera_loop(self, camera_id):

        path = self.video_paths[camera_id]

        print(
            f"[Camera {camera_id}] "
            f"Opening: {path}"
        )

        cap = cv2.VideoCapture(
            path
        )

        self.caps[camera_id] = cap

        if not cap.isOpened():

            print(
                f"[Camera {camera_id}] "
                f"ERROR: Could not open video."
            )

            return

        print(
            f"[Camera {camera_id}] "
            f"Video opened successfully."
        )

        while self.running:

            ok, frame = cap.read()

            if not ok:

                print(
                    f"[Camera {camera_id}] "
                    f"Video reached end. Restarting."
                )

                cap.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )

                time.sleep(0.2)

                continue

            self.frame_numbers[
                camera_id
            ] += 1

            frame_number = (
                self.frame_numbers[
                    camera_id
                ]
            )

            # -------------------------------------------------
            # Run YOLO only every Nth frame
            # -------------------------------------------------

            if (
                frame_number
                % config.FRAME_SKIP
                == 0
            ):

                processed_frame, metrics = (
                    self.detect_frame(
                        frame
                    )
                )

                with self.locks[
                    camera_id
                ]:

                    self.frames[
                        camera_id
                    ] = processed_frame

                    self.traffic_data[
                        camera_id
                    ] = metrics

            else:

                # Keep displaying the latest
                # processed frame.
                with self.locks[
                    camera_id
                ]:

                    if (
                        self.frames[
                            camera_id
                        ] is None
                    ):

                        self.frames[
                            camera_id
                        ] = frame

            # Small delay prevents the
            # processing loop from consuming
            # the CPU unnecessarily.
            time.sleep(0.001)

        cap.release()

        print(
            f"[Camera {camera_id}] "
            f"Stopped."
        )

    # =====================================================
    # DETECT FRAME
    # =====================================================

    def detect_frame(self, frame):

        results = self.model.predict(
            source=frame,
            conf=config.MODEL_CONFIDENCE,
            imgsz=config.IMAGE_SIZE,
            device=config.DEVICE,
            verbose=False,
        )[0]

        vehicle_counts = {}

        for class_name in (
            config.VEHICLE_CLASSES.values()
        ):

            vehicle_counts[
                class_name
            ] = 0

        annotated_frame = frame.copy()

        if results.boxes is not None:

            for box in results.boxes:

                class_id = int(
                    box.cls[0]
                )

                confidence = float(
                    box.conf[0]
                )

                if (
                    class_id
                    not in config.VEHICLE_CLASSES
                ):

                    continue

                class_name = (
                    config.VEHICLE_CLASSES[
                        class_id
                    ]
                )

                vehicle_counts[
                    class_name
                ] += 1

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                label = (
                    f"{class_name} "
                    f"{confidence:.2f}"
                )

                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )

                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )

        # -------------------------------------------------
        # Calculate traffic metrics
        # -------------------------------------------------

        metrics = calculate_traffic_metrics(
            vehicle_counts
        )

        # Add a simple overlay
        # -------------------------------------------------

        cv2.putText(
            annotated_frame,
            f"Vehicles: {metrics['vehicle_count']}",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            annotated_frame,
            f"Traffic Score: {metrics['weighted_score']}",
            (15, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        return (
            annotated_frame,
            metrics
        )

    # =====================================================
    # GET TRAFFIC DATA
    # =====================================================

    def get_traffic_data(self):

        data = []

        for camera_id in range(
            self.num_cameras
        ):

            with self.locks[
                camera_id
            ]:

                item = dict(
                    self.traffic_data[
                        camera_id
                    ]
                )

            data.append(item)

        return data

    # =====================================================
    # GET FRAME
    # =====================================================

    def get_frame(self, camera_id):

        if (
            camera_id < 0
            or camera_id >= self.num_cameras
        ):

            return None

        with self.locks[
            camera_id
        ]:

            frame = self.frames[
                camera_id
            ]

            if frame is None:
                return None

            return frame.copy()

    # =====================================================
    # VIDEO RESPONSE
    # =====================================================

    def video_response(self, camera_id):

        from flask import Response

        def generate():

            while self.running:

                frame = self.get_frame(
                    camera_id
                )

                if frame is None:

                    time.sleep(0.05)

                    continue

                success, buffer = (
                    cv2.imencode(
                        ".jpg",
                        frame,
                        [
                            cv2.IMWRITE_JPEG_QUALITY,
                            80,
                        ],
                    )
                )

                if not success:

                    time.sleep(0.05)

                    continue

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + buffer.tobytes()
                    + b"\r\n"
                )

                time.sleep(0.03)

        return Response(
            generate(),
            mimetype=(
                "multipart/x-mixed-replace;"
                " boundary=frame"
            ),
        )

    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        self.running = False

        for cap in self.caps:

            if cap is not None:

                cap.release()

        for thread in self.threads:

            if thread.is_alive():

                thread.join(
                    timeout=2
                )

        print(
            "YOLO detectors stopped."
        )