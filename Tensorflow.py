#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 21:00:43 2020

@author: jan
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import clear_output
from six.moves import urllib

import tensorflow.compat.v2.feature_column as fc

import tensorflow as tf

from Repository import Repository


#Load and unpack data for feature creation and seperate labels 
train_data = Repository().read_csv('/home/jan/python-workspace/angewendete_daten_analyse/testsets/training_data')
eval_data = Repository().read_csv('/home/jan/python-workspace/angewendete_daten_analyse/testsets/eval_data')

train_array = train_data.values

xt = []
yt = []

for item in train_array:
    Means = item[0]
    xt.append(Means[0])
    yt.append(Means[1])
    
train_data.pop('Means')    
train_data.insert(0,'Y',yt)
train_data.insert(0,'X',xt)

dftrain = train_data

eval_array = eval_data.values

xe = []
ye = []

for item in eval_array:
    Means = item[0]
    xe.append(Means[0])
    ye.append(Means[1])
    
eval_data.pop('Means')    
eval_data.insert(0,'Y',ye)
eval_data.insert(0,'X',xe)

dfeval = eval_data

# # Load dataset.
dftrain.pop('Covariances')
dfeval.pop('Covariances')

y_train = dftrain.pop('label')
y_eval = dfeval.pop('label')
print(dftrain.head())
print(y_train)


#Prepare columns as features for tensors
NUMERIC_COLUMNS = ['X', 'Y', 'weights']

feature_columns = []
for feature_name in NUMERIC_COLUMNS:
  feature_columns.append(tf.feature_column.numeric_column(feature_name, dtype=tf.float32))

print(feature_columns)
#Input functions to create tensors from dataset
def make_input_fn(data_df, label_df, num_epochs=15, shuffle=True, batch_size=32):
  def input_function():  # inner function, this will be returned
    ds = tf.data.Dataset.from_tensor_slices((dict(data_df), label_df))  # create tf.data.Dataset object with data and its label
    if shuffle:
      ds = ds.shuffle(1000)  # randomize order of data
    ds = ds.batch(batch_size).repeat(num_epochs)  # split dataset into batches of 32 and repeat process for number of epochs
    return ds  # return a batch of the dataset
  return input_function  # return a function object for use

train_input_fn = make_input_fn(dftrain, y_train)  # here we will call the input_function that was returned to us to get a dataset object we can feed to the model
eval_input_fn = make_input_fn(dfeval, y_eval, num_epochs=1, shuffle=False)

linear_est = tf.estimator.LinearClassifier(feature_columns=feature_columns)
# We create a linear estimtor by passing the feature columns we created earlier

linear_est.train(train_input_fn)  # train
result = linear_est.evaluate(eval_input_fn)  # get model metrics/stats by testing on tetsing data

clear_output()  # clears consoke output
print(result['accuracy'])  # the result variable is simply a dict of stats about our model
# print(result)


pred_dicts = list(linear_est.predict(eval_input_fn))
probs = pd.Series([pred['probabilities'] for pred in pred_dicts])

print(probs)