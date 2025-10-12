import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import numpy as np
import matplotlib.pyplot as plt
from torchvision import datasets, models, transforms
import os
import copy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pathDataset = os.path.join(BASE_DIR, "dataset/")

train_dataset = torchvision.datasets.ImageFolder(pathDataset + 'split/train',
                                      transform = transforms.Compose([
                                                      transforms.Resize(256),
                                                      transforms.ToTensor(),
                                                      transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                                          std = [0.229, 0.224, 0.225])]))
val_dataset = torchvision.datasets.ImageFolder(pathDataset + 'split/val',
                                      transform = transforms.Compose([
                                                      transforms.Resize(256),
                                                      transforms.CenterCrop(224),
                                                      transforms.ToTensor(),
                                                      transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                                          std = [0.229, 0.224, 0.225])]))

print("Data entrenamiento:", len(train_dataset))
print("Data validacion:", len(val_dataset))
print(train_dataset.classes)



## Hacemos uso de data loaders para dividir la data en mini-batches
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=32,shuffle=True)
val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=32, shuffle=False)

class_names = train_dataset.classes

device = ('cuda' if torch.cuda.is_available() else 'cpu')
print('Dispositivo: ', device)
"""
Función para entrenar la red neuronal.

model: red neuronal a entrenar
criterion: función de pérdida
optimizer: optimizador
num_epochs: número de épocas de entrenamiento
"""
def train_model(model, criterion, optimizer, num_epochs=25):
    best_model_wts = copy.deepcopy(model.state_dict()) # Copia los pesos iniciales del modelo
    best_acc = 0.0

    # Iteramos por cada época
    for epoch in range(num_epochs):
        print(f'Epoch {epoch}/{num_epochs-1}')
        print('-' * 10)

        model.train()

        running_loss = 0.0
        running_corrects = 0.0

        # Recorre los lotes de entrenamiento (iteraciones)
        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad() # Reinicia gradientes

            outputs = model(inputs) # Fordward pass
            _, preds = torch.max(outputs, 1) # Predicción: índice de mayor probabilidad
            loss = criterion(outputs, labels) # Computa la pérdida

            loss.backward() # backpropagation
            optimizer.step() # actualizar pesos

            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds ==  labels.data)

        epoch_loss = running_loss / len(train_dataset)
        epoch_acc = running_corrects.double() / len(train_dataset)

        print('Train Loss: {:.4f}  Acc: {:.4f}'.format(epoch_loss, epoch_acc))

        # Validación: La hacemos al termina cada época
        model.eval()
        running_loss = 0.0
        running_corrects = 0.0

        for inputs, labels in val_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            with torch.set_grad_enabled(False): # No actualiza gradientes
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1) # Predicción
                loss = criterion(outputs, labels) # Pérdida

            running_loss += loss.item() * inputs.size(0)
            #print(loss.item())
            #print(inputs.size(0))
            running_corrects += torch.sum(preds == labels.data)

        epoch_loss = running_loss / len(val_dataset)
        epoch_acc = running_corrects / len(val_dataset)
        print('Val Loss: {:.4f}  Acc: {:.4f}'.format(epoch_loss, epoch_acc))

        if epoch_acc > best_acc: # Si mejora el accuracy en validación, guarda los pesos
            best_acc = epoch_acc
            best_model_wts = copy.deepcopy(model.state_dict())

    print('Best accuracy: {:.4f}'.format(best_acc))

    # Cargamos el modelo con los mejores pesos encontrados en validación
    model.load_state_dict(best_model_wts)

    return model

#Usamos un modelo pre-entrenado ResNet18 con dataset Imagenet
model_fr = models.resnet18(pretrained=True)
for param in model_fr.parameters():
  param.requires_grad = False # Congela los parámetros

#Vamos a cambiar la última capa de la red. La red original fur entrenada con
# 1000 clases. Ahora solo necesitamos 4 neuronas de salida.
# Cambiamos la arquitectura final de la red

num_ft = model_fr.fc.in_features
model_fr.fc = nn.Linear(num_ft, 4)

model_fr = model_fr.to(device)
criterion = nn.CrossEntropyLoss()

#La red original fue entrenada con SGD y un lr inicial de 0.1, el cual decrementaba cada vez que el
# error se estancaba. Nosotros partimos con SGD y un lr bajo, dado que solo queremos tunear la red
# para el nuevo problema

optimizer = torch.optim.SGD(model_fr.parameters(), lr = 0.001, momentum=0.9)

# Empezamos con un número de épocas bajo. A más épocas podemos mejorar el performance
model_fr = train_model(model_fr, criterion, optimizer, num_epochs=5)

#Guardamos la mejor red, en términos de accuracy de validación
torch.save(model_fr.state_dict(), 'resnet18_freezed.pth')