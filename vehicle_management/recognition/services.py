"""License plate recognition from video using YOLOv8.

The two YOLO models are loaded once, lazily, on first use and reused across
requests. Model weights are resolved relative to settings.SAVED_MODELS_DIR so
the project runs on any machine.
"""

import base64

from django.conf import settings

PLATE_WEIGHTS = "plate_detection_best.pt"
CHAR_WEIGHTS = "character_recognition_yolov8s_best.pt"
MIN_PLATE_LENGTH = 6


class PlateRecognizer:
    _instance = None

    def __init__(self):
        # Imported here so importing this module doesn't require ultralytics
        # (e.g. during migrations or when recognition is unused).
        from ultralytics import YOLO

        self.plate_model = YOLO(str(settings.SAVED_MODELS_DIR / PLATE_WEIGHTS))
        self.char_model = YOLO(str(settings.SAVED_MODELS_DIR / CHAR_WEIGHTS))

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def read_plate(self, plate_img):
        """Return the plate string read from a cropped plate image."""
        chars = []
        for result in self.char_model(plate_img):
            if result.boxes is None:
                continue
            for box in result.boxes:
                x = float(box.xyxy[0][0])
                char = result.names[int(box.cls[0])]
                chars.append((x, char))
        chars.sort(key=lambda c: c[0])
        return "".join(char for _, char in chars)

    def detect_plates_in_frame(self, frame):
        """Yield plate strings detected in a single frame."""
        for result in self.plate_model(frame):
            if result.boxes is None:
                continue
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                yield self.read_plate(frame[y1:y2, x1:x2])

    def scan_video(self, video_path):
        """Scan a video, returning a list of (plate, frame_jpeg_b64, frame_time)."""
        import cv2

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        skip = max(1, int(fps / 2))

        seen = set()
        detections = []
        frame_index = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_index % skip == 0:
                for plate in self.detect_plates_in_frame(frame):
                    if len(plate) >= MIN_PLATE_LENGTH and plate not in seen:
                        seen.add(plate)
                        _, buffer = cv2.imencode(".jpg", frame)
                        detections.append(
                            (plate, base64.b64encode(buffer).decode(), frame_index / fps)
                        )
            frame_index += 1
        cap.release()
        detections.sort(key=lambda d: d[2])
        return detections
