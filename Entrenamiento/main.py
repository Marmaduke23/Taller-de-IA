# -*- coding: utf-8 -*- 
from app import app
from flask_funcs import predict_image_flask
from flask import Flask, jsonify, request



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


if __name__ == "__main__":
    app.run(port=7003,debug=True)
