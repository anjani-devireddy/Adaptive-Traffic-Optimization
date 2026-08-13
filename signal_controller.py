import time
import threading

from config import (
    MIN_GREEN_TIME,
    MAX_GREEN_TIME,
    YELLOW_TIME,
    TOTAL_CYCLE_TIME,
)


class SignalController:

    def __init__(self, num_cameras=4):

        self.num_cameras = num_cameras

        # 0 = North/South
        # 1 = East/West
        self.current_phase = 0

        self.signal_colors = [
            "Red"
            for _ in range(num_cameras)
        ]

        self.green_times = [
            MIN_GREEN_TIME,
            MIN_GREEN_TIME,
        ]

        self.phase_scores = [
            0,
            0,
        ]

        self.running = False

        self.lock = threading.Lock()

        self.thread = None

        self.phase_started_at = time.time()

    # =====================================================
    # CALCULATE PHASE SCORES
    # =====================================================

    def calculate_phase_scores(
        self,
        camera_scores
    ):

        # North + South
        phase_0 = (
            camera_scores[0]
            + camera_scores[2]
        )

        # East + West
        phase_1 = (
            camera_scores[1]
            + camera_scores[3]
        )

        return [
            phase_0,
            phase_1,
        ]

    # =====================================================
    # CALCULATE GREEN TIMES
    # =====================================================

    def calculate_green_times(
        self,
        phase_scores
    ):

        total_score = sum(
            max(0, score)
            for score in phase_scores
        )

        if total_score <= 0:

            return [
                30,
                30,
            ]

        available_green = (
            TOTAL_CYCLE_TIME
            - (
                2 * YELLOW_TIME
            )
        )

        # Start with minimum green.
        remaining = (
            available_green
            - (
                2 * MIN_GREEN_TIME
            )
        )

        remaining = max(
            0,
            remaining
        )

        green_times = []

        for score in phase_scores:

            proportion = (
                max(0, score)
                / total_score
            )

            green = (
                MIN_GREEN_TIME
                + proportion * remaining
            )

            green = int(
                round(green)
            )

            green = max(
                MIN_GREEN_TIME,
                min(
                    MAX_GREEN_TIME,
                    green
                )
            )

            green_times.append(
                green
            )

        return green_times

    # =====================================================
    # UPDATE TRAFFIC
    # =====================================================

    def update_traffic(
        self,
        camera_scores
    ):

        phase_scores = (
            self.calculate_phase_scores(
                camera_scores
            )
        )

        green_times = (
            self.calculate_green_times(
                phase_scores
            )
        )

        with self.lock:

            self.phase_scores = (
                phase_scores
            )

            self.green_times = (
                green_times
            )

    # =====================================================
    # SET SIGNAL PHASE
    # =====================================================

    def set_phase(self, phase):

        phase = phase % 2

        with self.lock:

            self.current_phase = phase

            self.phase_started_at = (
                time.time()
            )

            # Everyone starts RED.
            self.signal_colors = [
                "Red",
                "Red",
                "Red",
                "Red",
            ]

            if phase == 0:

                # North + South
                self.signal_colors[0] = "Green"
                self.signal_colors[2] = "Green"

            else:

                # East + West
                self.signal_colors[1] = "Green"
                self.signal_colors[3] = "Green"

    # =====================================================
    # GET STATE
    # =====================================================

    def get_state(self):

        with self.lock:

            phase = self.current_phase

            green_time = (
                self.green_times[phase]
            )

            elapsed = (
                time.time()
                - self.phase_started_at
            )

            remaining = max(
                0,
                int(
                    green_time - elapsed
                )
            )

            return {
                "current_phase": phase,
                "signal_colors": list(
                    self.signal_colors
                ),
                "green_times": list(
                    self.green_times
                ),
                "phase_scores": list(
                    self.phase_scores
                ),
                "remaining_time": remaining,
            }

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        self.running = True

        while self.running:

            with self.lock:

                phase = (
                    self.current_phase
                )

                green_time = (
                    self.green_times[phase]
                )

            self.set_phase(phase)

            print(
                f"[Signal] "
                f"Phase {phase} GREEN "
                f"for {green_time}s"
            )

            self._sleep(
                green_time
            )

            if not self.running:
                break

            # Yellow for both directions.
            with self.lock:

                self.signal_colors = [
                    "Red",
                    "Red",
                    "Red",
                    "Red",
                ]

                if phase == 0:

                    self.signal_colors[0] = "Yellow"
                    self.signal_colors[2] = "Yellow"

                else:

                    self.signal_colors[1] = "Yellow"
                    self.signal_colors[3] = "Yellow"

            print(
                f"[Signal] "
                f"Phase {phase} YELLOW "
                f"for {YELLOW_TIME}s"
            )

            self._sleep(
                YELLOW_TIME
            )

            if not self.running:
                break

            next_phase = (
                phase + 1
            ) % 2

            self.set_phase(
                next_phase
            )

    # =====================================================
    # SLEEP
    # =====================================================

    def _sleep(self, seconds):

        end = (
            time.time()
            + seconds
        )

        while (
            self.running
            and time.time() < end
        ):

            time.sleep(0.1)

    # =====================================================
    # START
    # =====================================================

    def start(self):

        if self.running:
            return

        self.thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        self.thread.start()

    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        self.running = False

        if (
            self.thread
            and self.thread.is_alive()
        ):

            self.thread.join(
                timeout=2
            )