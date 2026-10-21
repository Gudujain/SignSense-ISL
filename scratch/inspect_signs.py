import sys, os
sys.path.insert(0, os.path.abspath("."))
import cv2
from src.curriculum.curriculum import curriculum
from src.recognition.pose_analyzer import pose_analyzer

ref_dir = 'src/static/references'
signs = curriculum.get_all_signs()

for sign in signs:
    lbl = sign['label']
    img_path = os.path.join(ref_dir, f'{lbl}.jpg')
    img = cv2.imread(img_path)
    res = pose_analyzer.analyze_frame(img)
    hands = res.get('hands_count', 0)
    pri = res.get('primary_hand', {})
    ext = pri.get('extended_fingers', []) if pri else []
    print(f"Sign '{lbl}': type={sign['hand_type']}, hands={hands}, ext={ext}")
