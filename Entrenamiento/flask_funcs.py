from torchvision import models, transforms
import torch
from PIL import Image
import io
from app import model, class_names


def transform_image_flask(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(256, interpolation=transforms.InterpolationMode.BILINEAR),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)

def predict_image_flask(image_bytes):
    tensor = transform_image_flask(image_bytes=image_bytes)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)
        top_prob, top_class = torch.max(probs, 1)

    predicted_class = class_names[top_class.item()]
    return predicted_class, top_prob.item()
    