import torch
from torchvision import models, transforms
from PIL import Image

def predict_image(model_path, img_path, class_names, device=None):
    """
    Carga un modelo entrenado y predice la clase de una imagen.

    Args:
        model_path (str): ruta al .pth del modelo guardado
        img_path (str): ruta a la imagen a predecir
        class_names (list): lista de nombres de clases (orden de ImageFolder)
        device (str, optional): 'cpu' o 'cuda', si None se detecta automáticamente

    Returns:
        tuple: (predicted_class_name, probability)
    """

    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # ---- Carga del modelo ----
    model = models.resnet18(weights=None)  # sin pesos preentrenados
    num_features = model.fc.in_features
    model.fc = torch.nn.Linear(num_features, len(class_names))  # misma cantidad de clases
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    # ---- Transformaciones de la imagen ----
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    image = Image.open(img_path).convert('RGB')
    image = transform(image).unsqueeze(0)  # añadir batch dimension
    image = image.to(device)

    # ---- Inferencia ----
    with torch.no_grad():
        outputs = model(image)
        probs = torch.softmax(outputs, dim=1)
        top_prob, top_class = torch.max(probs, 1)

    predicted_class = class_names[top_class.item()]
    return predicted_class, top_prob.item()


class_names= ['backhand', 'forehand', 'ready_position', 'serve']

pred_class, prob = predict_image(
    model_path='resnet18_freezed.pth',
    img_path='imagenes_ejemplo/serve/serve2.png',
    class_names=class_names
)

print(f"Predicción: {pred_class} ({prob*100:.2f}%)")


import os

#Nos falta hacer predecir secuencia (un solo movimiento) y luego predecir video (varios movimientos)

# Predice asumiendo que es un conjunto de frames para UN SOLO MOVIMIENTO
# Elige la mejor etiqueta
#Si asumimos que la mayor parte del tiempo vamos a tener buenas metricas. Debería ganar la clase que sí es xd
def predict_secuence(model_path, list_images, class_names, step, device=None):

    # Lista donde guardaremos los resultados
    results = []
    # Diccionario para acumular sumas de probabilidades
    accumulator = {cls: 0.0 for cls in class_names}
    i = 0
    while i < len(list_images):
        pred_class, prob = predict_image(
            model_path=model_path,
            img_path=list_images[i],
            class_names=class_names
        )
        # Guardamos como diccionario
        results.append({
            'image_path': i, # antes lo tenía ya no, así que el nombre es un número no más xd
            'predicted_class': pred_class,
            'probability': prob
        })
        i+=step

        cls = pred_class
        accumulator[cls] += prob

    # Mostrar tabla de results
    #print("\nTabla de resultados:")
    #print("{:<50} {:<20} {:<12}".format("Imagen", "Predicción", "Probabilidad"))
    #print("-"*85)
    #for r in results:
        #print("{:<50} {:<20} {:<12}".format(
            #r['image_path'],
            #r['predicted_class'],
            #f"{r['probability']*100:.2f}%"
        #))

    # Clase con mayor suma
    final_class = max(accumulator, key=accumulator.get)
    #print("Predicción agregada:", final_class)
    return final_class # debería devolver tambien la probabilidad total o promedio del fragmento




result = predict_secuence(
    model_path='resnet18_freezed.pth',
    list_images=['imagenes_ejemplo/serve\\serve1.png', 'imagenes_ejemplo/serve\\serve2.png'],
    class_names=class_names,
    step = 1
)


# Asumimos que un movimiento dura 1 segundo.
# Asumimos un minimo de 30 fotogramas por segundo (para ir checkeando cada 5-10 imagenes xd).
# Por ende, un movimiento dura 30 fotogramas aprox. Le llamamos ratio a la duracion de un movimiento.
# (Habrán segundos mal clasificados entre movimiento y movimiento)
# Asumimos que cada fotograma de un video se guarda como imagen y se guardan en una carpeta.

def predict_video_frames(model_path, imgs_dir, class_names, step, ratio, device=None):
    # Ordenamos por nombre para que lea los fotogramas en orden.
    names_images = sorted([f for f in os.listdir(imgs_dir) if os.path.isfile(os.path.join(imgs_dir, f))])
    list_images = [os.path.join(imgs_dir, f) for f in names_images]
    # ['imagenes_ejemplo/serve\\serve1.png', 'imagenes_ejemplo/serve\\serve2.png'] ojo como van a quear los / en el server
    i = 0
    results = []
    while i <= len(list_images):
        subset = list_images[i:i+ratio]
        if len(subset) < 20: # no alcanza a ser un movimiento
            break
        result = predict_secuence(
            model_path= model_path,
            list_images= subset,
            class_names= class_names,
            step = 2
        )
        results.append(result)
        i+=ratio
    
    print(results)
    return results



results = predict_video_frames(
    model_path='resnet18_freezed.pth',
    imgs_dir='imagenes_ejemplo/mix',
    class_names=class_names,
    step = 2,
    ratio = 30
)



# Por lo que da la otra funcion el ratio es 58 aprox
results = predict_video_frames(
    model_path='resnet18_freezed.pth',
    imgs_dir='videos/video1/frames',
    class_names=class_names,
    step = 2,
    ratio = 58*2
)

#demoró 2-3 minutos aprox



# Falta hacer una funcion que diga de que segundo a que segundo dura cada movmiento
# (basta con considerar los FPS por segundo.. creo)
