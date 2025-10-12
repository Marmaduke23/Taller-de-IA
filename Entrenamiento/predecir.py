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