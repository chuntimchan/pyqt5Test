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

# #model = webcam_pose_head_tracking.load_model()

#Load in a MAT file
mat = scipy.io.loadmat('model_research\mpii_human_pose_v1_u12_1.mat')
#images_df = pd.DataFrame(mat['RELEASE'])

count = 0
x = 0
missing = 0

#Make a new dictionary with no keys
new_dict = {}
x_coord_list = []
y_coord_list = []
label_list = []
for i in range(0,24987):
    x = i
    #Count the number for each activity
    
    try:
        if mat['RELEASE']['act'][0][0][i][0][2][0][0] != -1: #Check if act_id is -1
            # #print()
            # # Check if the dictionary has a key that is equal to the activity
            # if mat['RELEASE']['act'][0][0][i][0][0][0] + " - " + mat['RELEASE']['act'][0][0][i][0][1][0] in new_dict:
            #     new_dict[mat['RELEASE']['act'][0][0][i][0][0][0] + " - " + mat['RELEASE']['act'][0][0][i][0][1][0]] += 1
            # else:
            #     new_dict[mat['RELEASE']['act'][0][0][i][0][0][0] + " - " + mat['RELEASE']['act'][0][0][i][0][1][0]] = 1
            # count += 1
            #If the image name is equal to the one we are looking for
            if (mat['RELEASE']['annolist'][0][0][0][i][0][0][0][0][0] == "000033016.jpg"):
                for j in range(0, 16):
                    #X Coordinate
                    sample = mat['RELEASE']['annolist'][0][0][0][i][1][0][0][4][0][0][0][0][j]
                    x_coord_list.append(sample[0][0][0])
                    y_coord_list.append(sample[1][0][0])
                    label_list.append(sample[2][0][0])
                    
    except:
        # print(mat['RELEASE']['act'][0][0][i][0][0])
        # missing += 1
        pass

# pprint.pprint(new_dict)
path = "model_research/000033016.jpg"
frame = cv2.imread(path)

model = webcam_pose_head_tracking.load_model()

output_x, output_y = webcam_pose_head_tracking.get_pose(frame,model)

# print(output_x)
# print(output_y)
#Unpack tensor to numpy array
print(output_x.detach().numpy())
print(output_y.detach().numpy())
print("Ground Truth")
mapping_x = dict(zip(label_list, x_coord_list))
mapping_y = dict(zip(label_list, y_coord_list))
sorted_mapping_x = dict(sorted(mapping_x.items()))
sorted_mapping_y = dict(sorted(mapping_y.items()))

error_x = 0
error_y = 0
total = 0
#Calculate distance between x ground truth and x prediction
for k in sorted_mapping_x:     
    error_x += abs(sorted_mapping_x[k] - output_x.detach().numpy()[k])
    error_y += abs(sorted_mapping_y[k] - output_y.detach().numpy()[k])
    total += 1

print(sorted_mapping_x)
print(sorted_mapping_y)
#Order the mapping by the label
print("Average Error: ", ((error_x/total) + (error_y/total)) / 2)


#new_image = webcam_pose_head_tracking.add_pose(frame,model)
#Display image
# cv2.imshow("Output", new_image)
# cv2.waitKey(0)

