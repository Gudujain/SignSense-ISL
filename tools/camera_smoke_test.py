"""Probe camera indices without showing or saving any camera frames."""
import argparse
import sys
import time

try:
    import cv2
except ImportError as exc:
    raise SystemExit("OpenCV is missing. Activate the project .venv and run `python -m pip install -r requirements.txt`.") from exc


def probe(index, frames, warmup_seconds):
    camera = cv2.VideoCapture(index)
    captured = 0
    dimensions = None
    try:
        if not camera.isOpened():
            return {"index": index, "opened": False, "frames": 0, "error": "device could not be opened"}
        deadline = time.monotonic() + warmup_seconds
        while time.monotonic() < deadline or captured < frames:
            ok, frame = camera.read()
            if ok and frame is not None and frame.size:
                captured += 1
                dimensions = [int(frame.shape[1]), int(frame.shape[0])]
            elif time.monotonic() >= deadline:
                break
        return {"index": index, "opened": True, "frames": captured,
                "dimensions": dimensions,
                "error": None if captured else "opened but returned no usable frames"}
    finally:
        camera.release()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--indices", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--frames", type=int, default=5)
    parser.add_argument("--warmup-seconds", type=float, default=2.0)
    args = parser.parse_args()
    results = [probe(i, args.frames, args.warmup_seconds) for i in args.indices]
    for result in results:
        print(result)
    if not any(r["opened"] and r["frames"] for r in results):
        print("No working camera was found. Check Windows camera privacy permissions, device connection, and whether another app owns the camera.")
        return 2
    print("Camera opened, returned frames, and each handle was released. No images were displayed or saved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
