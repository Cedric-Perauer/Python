# -*- coding: utf-8 -*-
"""Behavioural-Cloning

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MEpL_rHp_rt3ej0pYtH8EoL7fWUQcPZ1
"""

import numpy as np
import matplotlib.pyplot as plt
import keras
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.utils.np_utils import to_categorical
from keras.layers import Dropout, Flatten
import matplotlib.image as mpimg
from keras.layers.convolutional import Conv2D, MaxPooling2D
import pickle
import random
import pandas as pd
import cv2
import ntpath #to split path as we only want the last part
import os #imported to join driving_log and the directory
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

#!git clone https://github.com/Cedmalloc/Track_Data.git
!git clone https://github.com/rslim087a/track
!ls track

directory = 'track'  #equal to git repository name
columns = ['center','left','right','steering','throttle','reverse','speed']  #columns used below
data = pd.read_csv(os.path.join(directory, 'driving_log.csv'),names = columns)
pd.set_option('display.max_colwidth',-1) #allows us to see all columns
data.head()

#make sure to only use last part of path :
def path_end(path):
  beginning,end = ntpath.split(path)
  return end #only end is needed 

data['center'] = data['center'].apply(path_end) #applies function to all elements in center column
data['left'] = data['left'].apply(path_end) #applies function to all elements in center column
data['right'] = data['right'].apply(path_end) #applies function to all elements in center column

#data['steering'].hist()

num_of_bins = 25 #has to be odd to get middle value 
threshold = 200; 
hist, bins = np.histogram(data['steering'],num_of_bins)
#center values around 0 :
center = (bins[:-1] + bins[1:]) *0.5 #elementswise addition, appr. doubles so *0.5
plt.bar(center, hist, width = 0.05)
plt.plot([np.min(data['steering']), np.max(data['steering'])],[threshold, threshold])
#print(bins)

#as we can see it's almost symmetric due to turning around and driving the other way as well if we made a mistake generating our data we would be able to see that right here:
#model is fairly biased towards driving straight which can be changed via a threshold 
#bar plot would show a bias towards a certain steering angle
#an idea would be to only go one way and then artifically averaging the data out, in a way adding the right turn data to left turn and the other way around to get better generalization
remove = []
for j in range(num_of_bins):
  steer = []
  for i in range(len(data['steering'])) :
    if( data['steering'][i] >= bins[j] and data['steering'][i] <= bins[j+1]) :  #if steering angle is in between two bins, it belongs to current bin in iteration
      steer.append(i)  #add steering angle to list
      
      
  steer = shuffle(steer)  #shuffle is important to not loose parts of the track
  remove.extend(steer[threshold:])  #extend adds elements on to a list
      
data.drop(data.index[remove],inplace = True) #elements over threshold are dropped (if we have 700 : 700 - threshold are dropped)

hist, bins = np.histogram(data['steering'],num_of_bins)
#print(hist[0]) using hist and bin we coul create a perfect data set, due to the fact that the frame rate was very low we might need to come back and change that here
#hist[24] = 50
plt.bar(center, hist, width = 0.05)
plt.plot([np.min(data['steering']), np.max(data['steering'])],[threshold, threshold])

def load_image_data(dr, df):
  im_path = []
  steering = []
  for i in range(len(data)):   #iterate through data
    ind_data = data.iloc[i]
    center, left, right = ind_data[0], ind_data[1], ind_data[2]  
    #center image
    im_path.append(os.path.join(dr, center.strip()))   #add center data, strip erases spaces added just in case
    steering.append(float(ind_data[3]))       
    # left image
    #im_path.append(os.path.join(dr,left.strip()))  # os.path.join : Join one or more path components intelligently
    #steering.append(float(ind_data[3])+0.15)
    # right image 
    #im_path.append(os.path.join(dr,right.strip()))
    #steering.append(float(ind_data[3])-0.15)
    #convert to array
  im_paths = np.asarray(im_path)
  steerings = np.asarray(steering)
  return im_paths, steerings
 
im_paths, steerings = load_image_data(directory + '/IMG', data)
x_train, x_val, y_train, y_val = train_test_split(im_paths, steerings, test_size=0.2, random_state=6)
print('Training Samples: {}\nValid Samples: {}'.format(len(x_train), len(x_val)))
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(y_train, bins=num_of_bins, width=0.05, color='blue')
axes[0].set_title('Training set')
axes[1].hist(y_val, bins=num_of_bins, width=0.05, color='red')
axes[1].set_title('Validation set')

#image preprocessing
def pre_pro(img):
  img = mpimg.imread(img)
  #crop image
  img = img[60:135,:,:]  #crop trees and scenery (irrelevant in terms of just predicting the steering angle)
  #132 is making sure to cut out the hood
  #relying on Nvidia Model : yuv color space required
  img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)   #there's a difference between cv2.COLOR_RGB2YUV and cv2.COLOR_BGR2YUV
  #Gaussian blur to reduce image noise
  img = cv2.GaussianBlur(img,  (3, 3), 0)
  #image = cv2.resize(image, (image.shape[1],old_size))
  img = cv2.resize(img, (200, 66))
  #normalization
  img = img/255
  return img


image = im_paths[100]
preprocessed_image = pre_pro(image)
natural_im = mpimg.imread(image)

fig, axs = plt.subplots(1,2,figsize = (15,10))
axs[0].imshow(natural_im)
axs[0].set_title('Not preprocessed')
axs[1].imshow(preprocessed_image)
axs[1].set_title('Preprocessed image')

#preprocess all the images
x_train = np.array(list(map(pre_pro, x_train)))
x_val = np.array(list(map(pre_pro, x_val)))