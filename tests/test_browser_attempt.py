"""Contract checks for the browser-landmark endpoint and unverified templates."""
import json
from pathlib import Path

from src.server.app import app


def test_landmark_endpoint_rejects_camera_image_payload():
    with app.test_client() as client:
        response = client.post('/api/attempt', json={'target_sign': '1', 'frame': 'data:image/jpeg;base64,abc'})
    assert response.status_code == 400


def test_empty_landmark_window_is_logged_as_system_without_mastery(tmp_path, monkeypatch):
    from src.engine.storage import StorageManager
    from src.engine.learner_model import learner_manager
    from src.engine.recommender import recommender
    isolated = StorageManager(str(tmp_path / 'empty-window.db'))
    monkeypatch.setattr(learner_manager, 'storage', isolated)
    monkeypatch.setattr(recommender, 'storage', isolated)
    with app.test_client() as client:
        response = client.post('/api/attempt', json={
            'target_sign': '1', 'mode': 'practise', 'frames': [{'hands': []}]
        })
    payload = response.get_json()
    assert response.status_code == 200
    assert payload['outcome'] == 'not_seen'
    assert payload['failure_source'] == 'system'
    assert payload['learner_update']['saved'] is True
    assert payload['learner_update']['mastery_unchanged'] is True
    assert isolated.get_sign_mastery() == {}
    assert isolated.get_recent_attempts()[0]['failure_source'] == 'system'


def test_curriculum_pose_templates_cover_35_labels_and_are_unverified():
    path = Path(__file__).parents[1] / 'src' / 'static' / 'data' / 'signs.json'
    templates = json.loads(path.read_text(encoding='utf-8'))['signs']
    assert len(templates) == 35
    assert {item['label'] for item in templates} == set('123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert all(item['verified'] is False for item in templates)
    assert all(item['handCount'] in (1, 2) and len(item['hands']) == item['handCount'] for item in templates)
