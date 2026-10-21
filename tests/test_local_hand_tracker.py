import base64

import cv2
import numpy as np
import pytest

from src.server.app import app
from src.recognition.local_hand_tracker import close


@pytest.fixture(scope="module", autouse=True)
def close_local_tracker_after_tests():
    yield
    close()


def test_local_hand_tracker_rejects_missing_frame():
    response = app.test_client().post("/api/hand-tracker/frame", json={})
    assert response.status_code == 400
    assert "JPEG" in response.get_json()["error"]


def test_local_hand_tracker_processes_blank_frame_without_finding_hands():
    ok, encoded = cv2.imencode(".jpg", np.zeros((120, 160, 3), dtype=np.uint8))
    assert ok
    data_url = "data:image/jpeg;base64," + base64.b64encode(encoded).decode("ascii")
    response = app.test_client().post("/api/hand-tracker/frame", json={"image": data_url})
    assert response.status_code == 200
    assert response.get_json()["hands"] == []
