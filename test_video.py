import cv2
from pathlib import Path


VIDEO_PATHS = [
    r"C:\Users\GrokDrones\Downloads\2024-04-26 10-38-50.mp4",
    r"C:\Users\GrokDrones\Downloads\2024-04-23 10-31-54.mp4",
    r"C:\Users\GrokDrones\Downloads\2024-04-24 10-35-00.mp4",
    r"C:\Users\GrokDrones\Downloads\2024-04-30 15-59-50.mp4",
]


for i, path in enumerate(VIDEO_PATHS):

    print("\n" + "=" * 50)
    print(f"Camera {i}")
    print("File:", path)

    if not Path(path).exists():
        print("ERROR: File does not exist")
        continue

    cap = cv2.VideoCapture(
        path,
        cv2.CAP_FFMPEG
    )

    if not cap.isOpened():
        print("ERROR: Could not open video")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    print("Opened: True")
    print("FPS:", fps)
    print(
        "Resolution:",
        int(width),
        "x",
        int(height)
    )
    print("Frames:", int(total_frames))

    good = 0
    failed = 0

    frames_to_test = min(
        100,
        int(total_frames)
    )

    for _ in range(frames_to_test):

        ok, frame = cap.read()

        if ok:
            good += 1
        else:
            failed += 1

    print("Good frames:", good)
    print("Failed frames:", failed)

    cap.release()


print("\nAll videos tested.")