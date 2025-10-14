from procesamiento_videos import procesar_video
from predecir import predict_video_frames

path_video = "videos/video1/prueba1.mp4"

class_names= ['backhand', 'forehand', 'ready_position', 'serve']

step = 2

info_video = procesar_video(path_video, guardar_cada=step)

#usamos como ratio los fps, para catalogar por segundo
vector_clases = predict_video_frames(
                    model_path='resnet18_freezed.pth',
                    imgs_dir='videos/video1/frames',
                    class_names=class_names,
                    step = 1,
                    ratio = round(info_video['fps'])
                )

