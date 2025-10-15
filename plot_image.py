import json
import cv2
import matplotlib.pyplot as plt
import numpy as np

#nombre imagen
nombre_imagen = "S_005.jpeg"
# --- Rutas ---
img_path = "dataset/images/serve/"+nombre_imagen
json_path = "dataset/annotations/serve.json"

# --- Cargar imagen y anotaciones ---
img = cv2.imread(img_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

with open(json_path, 'r') as f:
    data = json.load(f)

# --- Buscar la anotación correspondiente a la imagen ---
image_info = next(img for img in data["images"] if img["file_name"] == nombre_imagen)
annotations = [a for a in data["annotations"] if a["image_id"] == image_info["id"]]
category = data["categories"][0]  # asumimos solo una categoría (e.g. "person")

# --- Dibujar keypoints y skeleton ---
for ann in annotations:
    keypoints = np.array(ann["keypoints"]).reshape(-1, 3)
    skeleton = category.get("skeleton", [])

    # Dibujar keypoints
    for (x, y, v) in keypoints:
        if v > 0:  # visible
            cv2.circle(img, (int(x), int(y)), 4, (0, 255, 0), -1)

    # Dibujar líneas del esqueleto
    for (i1, i2) in skeleton:
        x1, y1, v1 = keypoints[i1 - 1]
        x2, y2, v2 = keypoints[i2 - 1]
        if v1 > 0 and v2 > 0:
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)

# --- Mostrar imagen ---
plt.figure(figsize=(8, 6))
plt.imshow(img)
plt.axis("off")
plt.show()
