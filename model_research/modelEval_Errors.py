#import something outside of current folder
#pip install torch
import scipy.io
import sys, os
from collections.abc import Mapping
import pandas as pd
import pprint
import cv2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pose_estimator import webcam_pose_head_tracking

# Loading Pose Estimation Model
model = webcam_pose_head_tracking.load_model()
#Load in a MAT file
mat = scipy.io.loadmat('model_research\mpii_human_pose_v1_u12_1.mat')

count = 0
x = 0

#Make a new dictionary with no keys
new_dict = {}
x_coord_list = []
y_coord_list = []
label_list = []

image_name_list = []
#Get image names from current directory
for filename in os.listdir('model_research'):
    if filename.endswith(".jpg"):
        image_name_list.append(filename)

count = 0
print(image_name_list)
for i in range(0,24987):
    x = i
    #Count the number for each activity
    error_x = 0
    error_y = 0
    try:
        count += 1
        if (mat['RELEASE']['annolist'][0][0][0][i][0][0][0][0][0] in image_name_list):
            for j in range(0, 16):
                #X Coordinate
                image_name = mat['RELEASE']['annolist'][0][0][0][i][0][0][0][0][0]
                sample = mat['RELEASE']['annolist'][0][0][0][i][1][0][0][4][0][0][0][0][j]
                x_coord_list.append(sample[0][0][0])
                y_coord_list.append(sample[1][0][0])
                label_list.append(sample[2][0][0])  

                path = ("model_research/"+image_name)
                frame = cv2.imread(path)

                #Get predictions
                output_x, output_y = webcam_pose_head_tracking.get_pose(frame,model)
                #Calculate distance between x ground truth and x prediction 
                mapping_x = dict(zip(label_list, x_coord_list))
                mapping_y = dict(zip(label_list, y_coord_list))
                sorted_mapping_x = dict(sorted(mapping_x.items()))
                sorted_mapping_y = dict(sorted(mapping_y.items()))

                error_x += abs(sorted_mapping_x[j] - output_x.detach().numpy()[j])
                error_y += abs(sorted_mapping_y[j] - output_y.detach().numpy()[j])
            print("Error: ", error_x, error_y, "Image Name: ", image_name)
    except:
        pass

print(count)
# pprint.pprint(new_dict)





#Order the mapping by the label
# print("Average Error: ", ((error_x/total) + (error_y/total)) / 2)

