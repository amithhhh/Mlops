# -*- coding: utf-8 -*-
"""zenml00.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sDFGehNk92A_NSBKiGCoOTSIDDOIGB6N
"""

!pip install "zenml[server]"
!zenml integration install sklearn -y
!pip install pyparsing==2.4.2

import IPython

IPython.Application.instance().kernel.do_shutdown(restart=True)

NGROK_TOKEN = "2dWD6mhKk49D5ByK1hIbhrb8CNQ_7FfDhyqRAyNMhBXS9F2fP"

from zenml.environment import Environment

if Environment.in_google_colab():
    !pip install pyngrok
    !ngrok authtoken {NGROK_TOKEN}

!rm -rf .zen
!zenml init

import numpy as np
from sklearn.base import ClassifierMixin
from sklearn.svm import SVC
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

def train_test()->None:
    digits = load_digits()
    data = digits.images.reshape((len(digits.images),-1))
    Xtrain,Xtest,ytrain,ytest = train_test_split(
        data,digits.target,test_size=0.2,shuffle=False
    )
    model = SVC(gamma=0.001)
    model.fit(Xtrain,ytrain)
    test_acc = model.score(Xtest,ytest)
    print(f'Test Accuracy: {test_acc}')

train_test()

from zenml import step
from typing_extensions import Annotated
import pandas as pd
from typing import Tuple

@step
def importer()->Tuple[
    Annotated[np.ndarray,'Xtrain'],
    Annotated[np.ndarray,'Xtest'],
    Annotated[np.ndarray,'ytrain'],
    Annotated[np.ndarray,'ytest'],
]:
    digits = load_digits()
    data = digits.images.reshape((len(digits.images),-1))
    Xtrain,Xtest,ytrain,ytest = train_test_split(
        data,digits.target,test_size=0.2,shuffle=False
    )
    return Xtrain,Xtest,ytrain,ytest

@step
def svc_trainer(
        Xtrain: np.ndarray,
        ytrain: np.ndarray
)->ClassifierMixin:
    model = SVC(gamma=0.001)
    model.fit(Xtrain,ytrain)
    return model

@step
def evaluator(
        Xtest:np.ndarray,
        ytest:np.ndarray,
        model:ClassifierMixin
)->float:
    test_acc = model.score(Xtest,ytest)
    print(f'Test Accuracy: {test_acc}')
    return test_acc

from zenml import pipeline

@pipeline
def digits_pipeline():
    Xtrain,Xtest,ytrain,ytest = importer()
    model = svc_trainer(Xtrain,ytrain)
    evaluator(Xtest,ytest,model)

digits_svc_pipeline = digits_pipeline()

from zenml.environment import Environment

def start_dashboard(port=8237):
    if Environment.in_google_colab():
        from pyngrok import ngrok

        public_url = ngrok.connect(port)
        print(f"{public_url}")
        !zenml up --blocking --port (port)
    else:
        !zenml up --port (port)

start_dashboard()

