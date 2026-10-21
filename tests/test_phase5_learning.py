import time
import sqlite3
from src.engine.storage import StorageManager
from src.engine.learner_model import LearnerModelManager
from src.engine.recommender import RecommendationEngine
from src.curriculum.curriculum import CurriculumManager
from src.engine.demo_seed import seed_demo_history

def setup(tmp_path):
    store=StorageManager(str(tmp_path/'phase5.db'))
    rec=RecommendationEngine();rec.storage=store;rec.curriculum=CurriculumManager()
    learner=LearnerModelManager();learner.storage=store
    return store,rec,learner

def attempt(store, label='1', outcome='correct', source='learner', prediction=None, timestamp=None, session='test-session'):
    sign=CurriculumManager().get_sign_by_label(label)
    store.record_attempt({'sign_id':sign['id'],'label':label,'model_prediction':prediction or label,
        'model_status':'test','is_correct':int(outcome=='correct'),'is_uncertain':int(outcome in {'almost','not_seen'}),
        'discrepancy':int(prediction is not None and prediction!=label),'feedback_message':'test evidence',
        'assessment_json':'{}','timestamp':timestamp or time.time(),'outcome':outcome,
        'failure_source':source,'mode':'check','session_id':session})

def test_recommendation_rule_1_system_failures_are_separate(tmp_path):
    store,rec,_=setup(tmp_path)
    attempt(store,outcome='not_seen',source='system');attempt(store,label='2',outcome='not_seen',source='system')
    top=rec.get_recommendations()[0]
    assert (top['rule_id'],top['title'],top['reason'])==('SETUP_RECOVERY','Check your setup',"We couldn't see your hand clearly.")

def test_recommendation_rule_2_due_sign(tmp_path):
    store,rec,_=setup(tmp_path);sign=rec.curriculum.get_sign_by_label('1')
    store.save_sign_mastery({'sign_id':sign['id'],'level':'familiar','next_due':time.time()-86400})
    assert rec.get_recommendations()[0]['rule_id']=='SPACED_REVISION'

def test_recommendation_rule_3_repeated_miss(tmp_path):
    store,rec,_=setup(tmp_path);attempt(store,outcome='incorrect');attempt(store,outcome='almost')
    assert rec.get_recommendations()[0]['rule_id']=='REPEATED_DIFFICULTY'

def test_recommendation_rule_4_confusable_pair(tmp_path):
    store,rec,_=setup(tmp_path);attempt(store,label='6',outcome='incorrect',prediction='9');attempt(store,label='9',outcome='incorrect',prediction='6')
    assert rec.get_recommendations()[0]['rule_id']=='CONTRAST_DRILL'

def test_recommendation_rule_5_stage_unlock(tmp_path):
    store,rec,_=setup(tmp_path)
    for label in '1234': store.save_sign_mastery({'sign_id':rec.curriculum.get_sign_by_label(label)['id'],'level':'mastered'})
    assert rec.get_recommendations()[0]['rule_id']=='STAGE_UNLOCK'

def test_recommendation_rule_6_next_new(tmp_path):
    _,rec,_=setup(tmp_path)
    top=rec.get_recommendations()[0]
    assert (top['rule_id'],top['title'],top['reason'])==('NEXT_NEW_SIGN','Learn the next new sign','Next in your plan.')

def test_recommendation_rule_7_return_warmup(tmp_path):
    store,rec,_=setup(tmp_path);store.save_sign_mastery({'sign_id':'isl_num_1','level':'familiar'})
    attempt(store,timestamp=time.time()-4*86400)
    assert rec.get_recommendations()[0]['rule_id']=='RETURN_WARMUP'

def test_recommendation_rule_8_break(tmp_path):
    store,rec,_=setup(tmp_path)
    for index in range(10): attempt(store,label=str(index%5+1),session='ten-attempts')
    assert rec.get_recommendations()[0]['rule_id']=='SESSION_BREAK'

def test_mastery_transitions_and_different_day_check_requirement(tmp_path):
    store,_,learner=setup(tmp_path)
    def save(outcome,mode='practise'):
        assessment={'target_sign':'1','outcome':outcome,'is_correct':outcome=='correct','is_uncertain':False,
                    'can_update_mastery':True,'failure_source':'learner','feedback_message':'Test','mode':mode}
        return learner.update_with_attempt(assessment,{'status':'recognized','predicted_sign':'1'})
    save('correct')
    assert store.get_sign_mastery()['isl_num_1']['level']=='learning'
    save('correct')
    assert store.get_sign_mastery()['isl_num_1']['level']=='familiar'
    record=store.get_sign_mastery()['isl_num_1'];record['check_streak']=1;record['last_check_day']='2000-01-01';store.save_sign_mastery(record)
    save('correct','check')
    assert store.get_sign_mastery()['isl_num_1']['level']=='mastered'

def test_system_failure_does_not_change_mastery_or_count_as_miss(tmp_path):
    store,_,learner=setup(tmp_path)
    assessment={'target_sign':'1','outcome':'not_assessed','is_uncertain':True,'is_correct':False,
                'can_update_mastery':False,'failure_source':'system','feedback_message':'No tracking'}
    result=learner.update_with_attempt(assessment,{'status':'error'})
    assert result['mastery_unchanged'] is True
    assert store.get_sign_mastery()=={}
    assert store.get_sign_progress('isl_num_1') is None
    assert store.get_recent_attempts()[0]['failure_source']=='system'

def test_not_now_snoozes_and_dismiss_hides(tmp_path):
    store,rec,_=setup(tmp_path)
    top=rec.get_recommendations()[0];store.dismiss_recommendation(top['dismissal_key'],snooze_seconds=3600)
    assert top['dismissal_key'] in store.get_dismissed_recommendations()
    store.clear_dismissed_recommendations();store.dismiss_recommendation(top['dismissal_key'])
    assert top['dismissal_key'] in store.get_dismissed_recommendations()

def test_additive_migration_preserves_old_attempt_rows(tmp_path):
    path=str(tmp_path/'old-signsense.db')
    conn=sqlite3.connect(path)
    conn.execute('CREATE TABLE practice_attempts(id INTEGER PRIMARY KEY, sign_id TEXT NOT NULL, label TEXT NOT NULL, timestamp REAL NOT NULL)')
    conn.execute('INSERT INTO practice_attempts(id,sign_id,label,timestamp) VALUES(41,?,?,?)',('isl_num_1','1',1234.5))
    conn.commit();conn.close()
    store=StorageManager(path)
    with sqlite3.connect(path) as migrated:
        columns={row[1] for row in migrated.execute('PRAGMA table_info(practice_attempts)')}
    row=store.get_recent_attempts()[0]
    assert row['id']==41 and row['timestamp']==1234.5
    assert {'outcome','hint_given','failure_source','mode','session_id'} <= columns
    assert store.get_sign_mastery()=={}

def test_demo_history_isolated_and_covers_priority_rules(tmp_path):
    store,rec,_=setup(tmp_path)
    result=seed_demo_history(store)
    assert result['sessions']==22
    assert result['attempts']==17
    assert store.get_recent_attempts(100)==[]
    assert len(store.get_recent_attempts(100,demo=True))==17
    demo_recs=rec.get_recommendations(demo=True)
    assert [item['rule_id'] for item in demo_recs]==['SETUP_RECOVERY','SPACED_REVISION','REPEATED_DIFFICULTY']
    assert [item['reason'] for item in demo_recs]==[
        "We couldn't see your hand clearly.",
        'It has been 7 days since you practised it.',
        "Sign 6 has been tricky. Let's slow down."]
    assert rec.get_recommendations()[0]['rule_id']=='NEXT_NEW_SIGN'
