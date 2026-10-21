from src.engine.storage import StorageManager
from src.engine.learner_model import learner_manager
from src.engine.recommender import recommender
from src.server import app as server_module

def test_demo_seed_reset_is_developer_only_and_not_in_normal_progress(tmp_path, monkeypatch):
    store=StorageManager(str(tmp_path/'demo-api.db'))
    monkeypatch.setattr(server_module,'storage',store)
    monkeypatch.setattr(learner_manager,'storage',store)
    monkeypatch.setattr(recommender,'storage',store)
    with server_module.app.test_client() as client:
        denied=client.post('/api/dev/demo-data',json={'developer_mode':False,'action':'seed'})
        seeded=client.post('/api/dev/demo-data',json={'developer_mode':True,'action':'seed'})
        normal=client.get('/api/learner/progress').get_json()
        demo=client.get('/api/learner/progress?demo=1').get_json()
        recommendations=client.get('/api/recommendations').get_json()
        reset=client.post('/api/dev/demo-data',json={'developer_mode':True,'action':'reset'})
    assert denied.status_code==403
    assert seeded.status_code==200 and seeded.get_json()['demo_data'] is True
    assert normal['recent_attempts']==[]
    assert demo['demo_data'] is True and demo['total_attempts']==17
    assert 'latency_ms' not in recommendations
    assert reset.status_code==200
    assert store.get_recent_attempts(100,demo=True)==[]
