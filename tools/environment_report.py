"""Report interpreter/package/model readiness without capturing camera data."""
import argparse
import importlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


MODULES = {
    "flask": "flask", "numpy": "numpy", "opencv-contrib-python": "cv2",
    "mediapipe": "mediapipe", "scikit-learn": "sklearn", "scipy": "scipy",
    "pytest": "pytest",
}


def inspect_environment():
    report = {"python": sys.version, "executable": sys.executable,
              "platform": platform.platform(), "architecture": platform.machine(),
              "packages": {}, "opencv_distribution_conflict": False}
    for distribution, module in MODULES.items():
        try:
            version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            version = None
        try:
            imported = importlib.import_module(module)
            import_error = None
            runtime_version = version
        except Exception as exc:  # Include DLL-load and ABI errors, not just missing modules.
            imported = None
            import_error = f"{type(exc).__name__}: {exc}"
            runtime_version = None
        report["packages"][distribution] = {"installed_version": version,
                                            "runtime_version": runtime_version,
                                            "import_ok": import_error is None,
                                            "import_error": import_error}
    installed = {d.metadata.get("Name", "").lower().replace("_", "-")
                 for d in importlib.metadata.distributions()}
    opencv_names = {"opencv-python", "opencv-contrib-python",
                    "opencv-python-headless", "opencv-contrib-python-headless"}
    report["opencv_distributions"] = sorted(installed & opencv_names)
    report["opencv_distribution_conflict"] = len(report["opencv_distributions"]) > 1

    try:
        from src.recognition.pose_analyzer import pose_analyzer as analyzer
        report["hand_landmarker"] = {"available": analyzer.available,
                                     "model_path": getattr(analyzer, "model_path", None),
                                     "initialization_error": analyzer.initialization_error}
    except Exception as exc:
        report["hand_landmarker"] = {"available": False,
                                     "initialization_error": f"{type(exc).__name__}: {exc}"}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", action="store_true", help="also probe camera indices 0, 1, and 2 (no frames saved)")
    args = parser.parse_args()
    report = inspect_environment()
    if args.camera and report["packages"]["opencv-contrib-python"]["import_ok"]:
        from camera_smoke_test import probe
        report["camera_probe"] = [probe(index, frames=5, warmup_seconds=2.0)
                                  for index in (0, 1, 2)]
    print(json.dumps(report, indent=2))
    if args.camera and not any(r.get("opened") and r.get("frames")
                               for r in report.get("camera_probe", [])):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
