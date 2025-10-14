# -*- coding: utf-8 -*- 
import json
from torchvision import models
from flask import Flask
import torch

app = Flask(__name__)

# Ver otros modelos en https://docs.pytorch.org/vision/main/models.html
model_path = 'resnet18_freezed.pth'
class_names= ['backhand', 'forehand', 'ready_position', 'serve']
model = models.resnet18(weights=None)  # sin pesos preentrenados
num_features = model.fc.in_features
model.fc = torch.nn.Linear(num_features, len(class_names))  # misma cantidad de clases
model.load_state_dict(torch.load(model_path))
model.eval()

