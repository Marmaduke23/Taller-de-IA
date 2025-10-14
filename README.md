# Taller-de-IA

Instrucciones para entrenar y hacer predicciones con el modelo:
1- Descargar el dataser Tennis Players Dataset de Kaggle: https://www.kaggle.com/datasets/orvile/tennis-player-actions-dataset
2- Descomprimir el archivo y colocar la carpeta "images" dentro de la carpeta "dataset" en el directorio del proyecto.
3- Ejecutar el script "split_data.py" dentro de la carpeta "Entrenamiento" para dividir el dataset en carpetas de entrenamiento y validación.
4- Ejecutar el script "train.py" dentro de la carpeta "Entrenamiento" para entrenar el modelo. (Este paso es opcional, ya que el modelo ya está entrenado (de forma rapida) y guardado en el archivo "resnet18_freezed.pth").
5- Ejecutar el script "predecir.py" dentro de la carpeta "Entrenamiento" para hacer predicciones con el modelo entrenado.(Van unas imagenes de ejemplo que estan en la carpeta "imagenes_ejemplo" y estan sacadas de videos random de yputube).