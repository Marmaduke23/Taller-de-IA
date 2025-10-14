
def split_dataset(data_dir,output_dir,val_ratio=0.2): 
    import os
    import shutil
    import random

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    train_dir = os.path.join(output_dir, 'train')
    val_dir = os.path.join(output_dir, 'val')

    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(val_dir):
        os.makedirs(val_dir)

    classes = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]

    for cls in classes:
        cls_dir = os.path.join(data_dir, cls)
        images = [f for f in os.listdir(cls_dir) if os.path.isfile(os.path.join(cls_dir, f))]
        random.shuffle(images)

        split_idx = int(len(images) * (1 - val_ratio))
        train_images = images[:split_idx]
        val_images = images[split_idx:]

        train_cls_dir = os.path.join(train_dir, cls)
        val_cls_dir = os.path.join(val_dir, cls)

        if not os.path.exists(train_cls_dir):
            os.makedirs(train_cls_dir)
        if not os.path.exists(val_cls_dir):
            os.makedirs(val_cls_dir)

        for img in train_images:
            shutil.copy(os.path.join(cls_dir, img), os.path.join(train_cls_dir, img))

        for img in val_images:
            shutil.copy(os.path.join(cls_dir, img), os.path.join(val_cls_dir, img))

    print(f'Dataset split into training and validation sets at {output_dir}')

#Dividir la data en validación y entrenamiento
split_dataset('dataset/images', 'dataset/split', val_ratio=0.2)