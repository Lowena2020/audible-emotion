# Apply classifier model to song dataframe

import tensorflow as tf

from tensorflow.keras.models import model_from_json
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler

import pandas as pd


def get_labels(df_test):
    # Loads the model and loads the song data frame for the model to act on
    
    model = load_model(r'C:/Users/lowen/Anaconda3/envs/tensor/AIMusicDataFiles/modeltest.h5')
    model.summary()
    
    standardizer = StandardScaler()
    
    x_test_set = df_test.drop(['id', 'track', 'artist','genre'],axis = 1)
    print(x_test_set.head())

    # Scale the new data and predict the labels
    x_test_set_scaled = standardizer.fit_transform(x_test_set)

    y_test_set = model.predict_classes(x_test_set_scaled)
    labels = y_test_set # a 2d array, to access items use [0][i]
    
    labels_list = []
    for item in labels:
        x = item[0]
        labels_list.append(x)
    
    return labels_list
    
df = pd.read_csv("songdataframe.csv")

labels = get_labels(df)

df['energy_tensor'] = labels

df.to_csv("songdataframewithlabel.csv", index =False)

