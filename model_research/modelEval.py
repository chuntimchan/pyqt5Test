#import something outside of current folder
#pip install torch

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pose_estimator import webcam_pose_head_tracking

model = webcam_pose_head_tracking.load_model()

image = None

for i in range(10):
    model.forward(image)

