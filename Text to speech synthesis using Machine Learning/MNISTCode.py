import tensorflow as tf  # deep learning library. Tensors are just multi-dimensional arrays
import matplotlib.pyplot as plt
import numpy as np
import os
import pylab
import cv2
import win32com.client as wincl
import image

# Will convert our output preducted numbers to a numpy string
# Necessary to concantinate with other strings
def to_str(var):
    if type(var) is list:
        return str(var)[1:-1] # list
    if type(var) is np.ndarray:
        try:
            return str(list(var[0]))[1:-1] # numpy 1D array
        except TypeError:
            return str(list(var))[1:-1] # numpy sequence
    return str(var) # everything else



mnist = tf.keras.datasets.mnist  # mnist is a dataset of 28x28 images of handwritten digits and their labels
(x_train, y_train),(x_test, y_test) = mnist.load_data()  # unpacks images to x_train/x_test and labels to y_train/y_test


x_train = tf.keras.utils.normalize(x_train, axis=1)  # scales data between 0 and 1
x_test = tf.keras.utils.normalize(x_test, axis=1)  # scales data between 0 and 1

plt.imshow(x_train[1], cmap='Greys')
#pylab.show()
model = tf.keras.models.Sequential()  # a basic feed-forward model
model.add(tf.keras.layers.Flatten())  # takes our 28x28 and makes it 1x784
model.add(tf.keras.layers.Dense(256, activation=tf.nn.relu))  # a simple fully-connected layer, 128 units, relu activation
model.add(tf.keras.layers.Dense(128, activation=tf.nn.relu))  # a simple fully-connected layer, 128 units, relu activation
model.add(tf.keras.layers.Dense(10, activation=tf.nn.softmax))  # our output layer. 10 units for 10 classes. Softmax for probability distribution

model.compile(optimizer='adam',  # Good default optimizer to start with
              loss='sparse_categorical_crossentropy',  # how will we calculate our "error." Neural network aims to minimize loss.
              metrics=['accuracy'])  # what to track

model.fit(x_train, y_train, epochs=3)  # train the model

#val_loss, val_acc = model.evaluate(x_test, y_test)  # evaluate the out of sample data with model
#print(val_loss)  # model's loss (error)
#print(val_acc)  # model's accuracy


test_data = []
path = "D:/InputImages"

for img in os.listdir(path):  # iterate over each image digits
    img_array = cv2.imread(os.path.join(path,img) ,cv2.IMREAD_GRAYSCALE)  # convert to array
    img_array = cv2.bitwise_not(img_array) #invert image color
    img_array = cv2.resize(img_array, (28,28))
    
    
    
    height, width = img_array.shape
    # for x in range(0,width):
    #     for y in range(0,height):
    #         pixel = img_array[x,y]
    #         print("pixel value is: ")
    #         print(pixel)

    for x in range(0,width):
        for y in range(0,height):
            pixel = img_array[x,y]
            if (pixel < 53):    
                img_array[x,y] = 0
            elif (pixel > 128):
                new_color = pixel*2
                if(new_color > 255):
                    new_color = 254
                new_color = new_color/255
                img_array[x,y] = new_color

    test_data.append(img_array)
    #plt.imshow(img_array)
    # plt.imshow(test_data[0])
    # plt.show


test_data = tf.keras.utils.normalize(test_data, axis=1)  # scales data between 0 and 1


plt.imshow(test_data[1]) #show test images 
plt.show()

# for idx, val in enumerate(test_data):
#     plt.imshow(val)  # graph it
#     plt.show()  # display!
#     plt.imshow(x_test[idx])  # graph it
#     plt.show()  # display!

predictions = model.predict([test_data])

speak = wincl.Dispatch("SAPI.SpVoice")
for prediction in predictions:
    output = "The prediction for the number input is " + to_str(np.argmax(prediction))
    print("The prediction for the number input is: ", np.argmax(prediction))
    speak.Speak(output)

