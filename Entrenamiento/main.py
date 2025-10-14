# -*- coding: utf-8 -*- 
from app import app, class_names
from flask_funcs import predict_image_flask
from procesar_video import procesar_video
from flask import Flask, jsonify, request
from predecir import predict_video_frames
import os



@app.route('/ejercicio3/app1-ia/predict', methods=['POST'])
def predict():
    headers = request.headers
    if 'Codigo' not in headers or headers['Codigo'] != 'pengu':
        return jsonify({"error": "No autorizado"}), 401
    file = request.files['file']
    img_bytes = file.read()
    clase_nombre,score = predict_image_flask(image_bytes=img_bytes)
    json_respuesta = {"predicciones": []}
    #for clase_nombre, score in zip(clases_nombre,score):
    json_respuesta['predicciones'].append({'clase_nombre': clase_nombre,'score': score})
    print("responder: {}".format(json_respuesta))
    return jsonify(json_respuesta)


@app.route('/ejercicio3/app1-ia/video', methods=['POST'])
def video():
    file = request.files['file']
    #guardar el video en carpeta videos
    video_name, ext = os.path.splitext(file.filename)
    # Crear carpeta con el nombre del video
    save_dir = os.path.join("videos", video_name)
    print(save_dir)
    os.makedirs(save_dir, exist_ok=True)
    # Guardar el video dentro de esa carpeta
    save_path = os.path.join(save_dir, file.filename)
    file.save(save_path)
    step = 1
    info_video = procesar_video(save_path, guardar_cada=step)
    vector_clases=predict_video_frames(
                    imgs_dir=save_dir+'/frames',
                    class_names=class_names,
                    step = 1,
                    ratio = round(info_video['fps']*0.5)
                )

    return jsonify({"message": "Video procesado"}), 200
    

if __name__ == "__main__":
    app.run(port=7003,debug=True)
