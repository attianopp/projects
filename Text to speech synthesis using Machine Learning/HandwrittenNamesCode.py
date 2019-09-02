import numpy as np
import tensorflow as tf  # deep learning library. Tensors are just multi-dimensional arrays
import os
import pylab
import win32com.client as wincl
import image
import matplotlib.pyplot as plt
import plotly.offline as py
py.init_notebook_mode(connected=True)
import plotly.graph_objs as go
import plotly.tools as tls
import scipy
import sklearn
import pandas as pd
from sklearn import linear_model, datasets, metrics
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import binarize
from sklearn.neural_network import BernoulliRBM, MLPClassifier
from sklearn.datasets import fetch_mldata
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from skimage import data, color, exposure, measure
from skimage.transform import resize
from skimage.feature import hog
from sklearn.manifold import TSNE
from sklearn.externals import joblib
import urllib
from io import StringIO
import cv2
from scipy import ndimage
from difflib import SequenceMatcher
from sys import stdout
from IPython.display import clear_output


enable_error_output = False


def to_str(var):
    if type(var) is list:
        return str(var)[1:-1] # list
    if type(var) is np.ndarray:
        try:
            return str(list(var[0]))[1:-1] # numpy 1D array
        except TypeError:
            return str(list(var))[1:-1] # numpy sequence
    return str(var) # everything else

#display function
def print_percentage(prct, msg=None):
    if (prct > 100 or prct < 0):
        return
    clear_output(wait=True)
    if (msg == None):
        stdout.write("Progress: [")
    else:
        stdout.write(msg+" [")
    end = int(int(prct)/10)
    for i in range(0, end):
        stdout.write("=")
    for i in range(end, 10):
        stdout.write(" ")
    stdout.write("] "+str(prct)+"%")
    stdout.flush()

df=pd.read_csv('first_and_last_names_fix.csv', sep=',',header=None) #read in dataset


def delborders(crop):
    cropf = ndimage.gaussian_filter(crop, 0.5)
    cropbin = (cropf<0.8)
    labeled, nr_objects = ndimage.label(cropbin)
    labels_to_delete = []
    for i in range(0, labeled.shape[1]):
        if (labeled[labeled.shape[0]-1][i] > 0):
            labels_to_delete.append(labeled[labeled.shape[0]-1][i])
    
    label_in_delete = False
    for x in range(0, labeled.shape[1]):
        for y in range(0, labeled.shape[0]):
            label_in_delete = False
            for l in range(0, len(labels_to_delete)):
                if (labeled[y][x] == labels_to_delete[l]):
                    label_in_delete = True
            
            if(label_in_delete):
                crop[y][x] = 1.0
    
    return crop

def getcrop(n):
    try: 
        urllib.request.urlretrieve(df[1][n], "temp.jpg")
    except urllib.error.URLError as e:
        return None, False
    img = cv2.imread('temp.jpg')
    imgh, imgw = img.shape[:-1]
    img_rgb = img.copy()
    template = cv2.imread('template.png')
    h, w = template.shape[:-1]

    template_match_success = False
    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .7
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        croph1 = pt[1]
        croph2 = pt[1]+h
        cropw = pt[0] + w
        template_match_success = True

    if (not template_match_success):
        #Template matching has failed so return
        return img, False

    if (df[3][n] == 'first' or df[3][n] == 'last'):
        crop = img.copy()[max(croph1-6, 0):min(croph2+6, imgh), cropw:imgw]
    else:
        crop = img.copy()[max(min(croph2+4, imgh-1), 0):imgh, :]
        
    crop = color.rgb2gray(crop)
    if (df[3][n] == 'first_b' or df[3][n] == 'last_b'):
        crop = delborders(crop)
    return crop, True

def gen_dataset(n=df.shape[0]):
    data = []
    labels = []
    for i in range(1, n):
        crop, success = getcrop(i)
        if (success):
            data.append(crop)
            labels.append(df[2][i])
        else:
            if (enable_error_output):
                print("[WARNING] Template matching has failed for image: "+str(i))
        print_percentage((i*100/(n-1)), "Fetched "+str(i)+" images:")
    
    print_percentage(100, "Fetched "+str(n-1)+" images:")
    print("")
    print("Finished!")
    return data, labels

dataset_load_method = 'load'

if (dataset_load_method == 'download'):
    dataset, labels = gen_dataset(10000)

# Load dataset from files
if (dataset_load_method == 'load'):
    dataset = np.load("HandwrittenNames_data.npz")['data']
    labels = np.load("HandwrittenNames_labels.npz")['data']

np.savez("HandwrittenNames_data.npz", data=dataset)
np.savez("HandwrittenNames_labels.npz", data=labels)

# selection = 0
# plt.imshow(dataset[selection], cmap='gray')
# plt.show()
# print(labels[selection])
# print(str(type(labels[0])))

def get_labels(crop):
    img = crop.copy() # gray-scale image

    # blur_radius = 0.5
    # imgf = ndimage.gaussian_filter(img, blur_radius)

    threshold = 0.8

    # Find connected components
    labeled, nr_objects = ndimage.label(img<threshold) 
    #print("Number of objects is " +str(nr_objects))

    return labeled, nr_objects

def get_bboxes(labeled, nr_objects):
    bboxes = np.zeros((nr_objects, 2, 2), dtype='int')

    x1, y1, x2, y2 = 0, labeled.shape[0], 0, 0
    coord = 0
    cont = 0
    ytop, ybot = 0, 0
    nzero, firstb = False, False

    for x in range(0, labeled.shape[1]):
        nzero, firstb = False, False
        ytop, ybot = 0, 0
        for y in range(0, labeled.shape[0]):
            if (labeled[y][x] > 0):
                nzero = True
                if (not firstb):
                    ytop = y
                    firstb = True
                ybot = y

        if (nzero):
            if (ytop < y1):
                y1 = ytop
            if (ybot > y2):
                y2 = ybot
            if (coord == 0):
                x1 = x
                coord = 1
            elif (coord == 1):
                x2 = x
        elif ((not nzero) and (coord == 1)):
            bboxes[cont][0] = [x1, y1]
            bboxes[cont][1] = [x2, y2]
            cont += 1
            coord = 0
            x1, y1, x2, y2 = 0, labeled.shape[0], 0, 0

    bboxes = bboxes[0:cont]
    return bboxes, cont

def crop_characters(img, bboxes, n):
    characters = []
    for i in range(0, n):
        c = img.copy()[bboxes[i][0][1]:bboxes[i][1][1], bboxes[i][0][0]:bboxes[i][1][0]]
        if (c.shape[0] != 0 and c.shape[1] != 0):
            c = resize(c, (28, 28), mode='constant', cval=1.0, clip=True)
            # plt.imshow(c, cmap='gray')
            # plt.show()
            characters.append((c<0.80).reshape(784))
    return characters, len(characters)

def labelsep(label):
    if (type(label) is str or type(label) is np.str_):
        decomposed_label = list(label)
        labels = []
        for i in range(0, len(decomposed_label)):
            if (decomposed_label[i] != ' '):
                labels.append(decomposed_label[i])
        return labels
    else:
        return []

def get_characters(image, label):
    labeled, nr_objects = get_labels(image)
    bboxes, n = get_bboxes(labeled, nr_objects)
    characters, n_chars = crop_characters(image, bboxes, n)
    labels = labelsep(label)
    return characters, labels[0:n_chars]

def get_characters_img_only(image):
    labeled, nr_objects = get_labels(image)
    bboxes, n = get_bboxes(labeled, nr_objects)
    characters, n_chars = crop_characters(image, bboxes, n)

    return characters


# print(labels[selection])
# characters, charlabels = get_characters(dataset[selection], labels[selection])

# for i in range(0, len(characters)):
#     plt.imshow(characters[i].reshape(28,28), cmap='gray')
#     plt.show()
    
# print(str(charlabels))

dataset_character_load_method = "load"

if(dataset_character_load_method == "load"):
    X_train =  np.load("xtrain0_data.npz")['data']
    X_test =  np.load("xtest0_data.npz")['data']
    Y_train =  np.load("ytrain_data.npz")['data']
    Y_test =  np.load("ytest_data.npz")['data']
    X_train_chars = np.load("xtrain_data.npz")['data']
    Y_train_chars = np.load("xtrain_labels.npz")['data']
    X_test_chars = np.load("xtest_data.npz")['data']
    Y_test_chars = np.load("xtest_labels.npz")['data']
    Test_without_inconsistencies = np.load("test_without_inconsistencies.npz")['data']
    Train_with_inconsistencies = np.load("train_with_inconsistencies.npz")['data']

    size = X_train_chars[0].shape
    # print("Di size mon is: "+to_str(size)", +Di Width mon is: "+to_str(width))


    




else:
    X_train, X_test, Y_train, Y_test = train_test_split(dataset, labels, test_size=0.2, random_state=0)


    X_train_chars = []
    Y_train_chars = []
    Train_with_inconsistencies = []
    z = 0
    for i in range(0, len(X_train)):
        #print_percentage(i*100/len(X_train), "Processing train image "+ str(i)+" :")
        characters, charlabels = get_characters(X_train[i], Y_train[i])
        if (len(characters) != len(charlabels) or len(characters) == 0 or len(charlabels) == 0):
            if (enable_error_output):
                print("[Warning] Input number "+str(i)+" inconsistent! Skipping this one...")
            Train_with_inconsistencies.append(i)
            z += 1
        else:
            X_train_chars.extend(characters)
            Y_train_chars.extend(charlabels)

    print_percentage(100, "Processing train image "+ str(len(X_train))+" :")
    print("")
    print(str(100-(z*100/len(X_train)))+"% of the data in train batch correctly extracted.")

    X_test_chars = []
    Y_test_chars = []
    Test_without_inconsistencies = []
    z = 0
    for i in range(0, len(X_test)):
    # print_percentage(i*100/len(X_test), "Processing test image "+ str(i)+" :")
        characters, charlabels = get_characters(X_test[i], Y_test[i])
        if (len(characters) != len(charlabels) or len(characters) == 0 or len(charlabels) == 0):
            if (enable_error_output):
                print("[Warning] Input number "+str(i)+" inconsistent! Skipping this one...")
            z += 1
        else:
            X_test_chars.extend(characters)
            Y_test_chars.extend(charlabels)
            Test_without_inconsistencies.append(i)

    print_percentage(100, "Processing train image "+ str(len(X_test))+" :")
    print("")
    print(str(100-(z*100/len(X_test)))+"% of the data in test batch correctly extracted.")

    np.savez("xtrain0_data.npz", data=X_train)
    np.savez("xtest0_data.npz", data=X_test)
    np.savez("ytrain_data.npz", data=Y_train)
    np.savez("ytest_data.npz", data=Y_test)

    np.savez("xtrain_data.npz", data=X_train_chars)
    np.savez("xtrain_labels.npz", data=Y_train_chars)
    np.savez("xtest_data.npz", data=X_test_chars)
    np.savez("xtest_labels.npz", data=Y_test_chars)
    np.savez("train_with_inconsistencies.npz",data=Train_with_inconsistencies)
    np.savez("test_without_inconsistencies.npz",data=Test_without_inconsistencies)

verbose_classifiers = True
mlp_classifier = MLPClassifier(hidden_layer_sizes=(300,400,150), max_iter=5000, tol=0.0001, random_state=1, verbose=verbose_classifiers)

save_classifiers = False
load_classifiers = True

if (not load_classifiers):
    mlp_classifier.fit(X_train_chars, Y_train_chars)
else:
    mlp_classifier = joblib.load('MLP.pkl')

if (save_classifiers):
    joblib.dump(mlp_classifier, 'MLP.pkl')

def predict_full_name(name, classifier):
    characters = get_characters_img_only(name)
    prediction = classifier.predict(characters)
    strg = ''
    for i in range(0, len(prediction)):
        strg = strg+prediction[i]
    return strg

def predict_full_names(classifier):
    correlation=0.0
    correct = 0
    for i in range(0,len(Test_without_inconsistencies)):
        predicted_name = predict_full_name(X_test[Test_without_inconsistencies[i]], classifier)
        if (predicted_name == Y_test[Test_without_inconsistencies[i]]):
            correct += 1
        correlation += similar(predicted_name, Y_test[Test_without_inconsistencies[i]])
       # print_percentage(i*100/len(X_test),"Making predictions "+str(i)+"/"+str(len(X_test))+":")
   # print_percentage(100,"Making predictions "+str(len(X_test))+"/"+str(len(X_test))+":")
    return (correct/len(Test_without_inconsistencies)), (correlation/len(Test_without_inconsistencies))



def similar(a,b):
        return SequenceMatcher(None,a,b).ratio()

save_results = False
if (save_results):
    result_output_file = open('result_output.txt','w') 

speak = wincl.Dispatch("SAPI.SpVoice")
mlp_prediction = mlp_classifier.predict(X_test_chars)
print("MLP only classification:\n%s\n" % (metrics.classification_report(Y_test_chars, mlp_prediction)))
if (save_results):
    result_output_file.write("\nMLP only classification:\n%s\n" % (metrics.classification_report(Y_test_chars, mlp_prediction)))
correct_mlp, corr_mlp = predict_full_names(mlp_classifier)
print("Full name test results: ")
print("========================================================================")
print("| Classifier            | Correct percentage      | Correlation ratio  |")
print("========================================================================")
print("| MLP only              | "+str(correct_mlp)+"     | "+str(corr_mlp)+" |")
print("========================================================================")


if (save_results):
    result_output_file.write("\n\nFull name test results: ")
    result_output_file.write("\n========================================================================")
    result_output_file.write("\n| Classifier            | Correct percentage      | Correlation ratio  |")
    result_output_file.write("\n========================================================================")
    result_output_file.write("\n| MLP only              | "+str(correct_mlp)+"     | "+str(corr_mlp)+" |")
    result_output_file.write("\n========================================================================")

indexes = [1,2,3,4,5,6,7,8,9,10]
for ind in indexes:
    mlp_predict = predict_full_name(X_test[ind], mlp_classifier)

    speak.Speak("The actual handwritten name is "+Y_test[ind])
    print("> Real label: "+Y_test[ind])
    print("> Image:")
    plt.imshow(X_test[ind], cmap='gray')
    plt.show()
    output = "The predicted handwritten text is " + mlp_predict
    speak.Speak(output)
    print("MLP predicted: "+mlp_predict)
    print("")
    
    if (save_results):
        result_output_file.write("\n\n> Real label: "+Y_test[ind])
        result_output_file.write("\nMLP predicted: "+mlp_predict)
        result_output_file.write("\n")

if (save_results):
    result_output_file.close()

path = "D:/InputImages"

for img in os.listdir(path): 
    img_array = cv2.imread(os.path.join(path,img) ,cv2.IMREAD_GRAYSCALE)  # convert to array
    height, width = img_array.shape
    print("height = "+to_str(height)+", Width = "+to_str(width))
    plt.imshow(img_array, cmap='gray')
    plt.show()
    mlp_predict = predict_full_name(img_array, mlp_classifier)
    print("> Image:")
    plt.imshow(img_array, cmap='gray')
    plt.show()
    output = "The predicted handwritten text is " + mlp_predict
    speak.Speak(output)
    print("MLP predicted: "+mlp_predict)
    print("")
    characters = get_characters_img_only(img)
    for i in range(0, len(characters)):
        plt.imshow(characters[i].reshape(28,28), cmap='gray')
        plt.show()
 
      

