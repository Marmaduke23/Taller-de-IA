from procesamiento_videos import procesar_video
from predecir import predict_video_frames
import json

path_video = "videos/video1/prueba1.mp4"

class_names= ['backhand', 'forehand', 'ready_position', 'serve']

step = 2

info_video = procesar_video(path_video, guardar_cada=step)

fps = info_video['fps']
ratio = round(fps/step)

#Usamos como ratio los fps, para catalogar por segundo
vector_clases = predict_video_frames(
                    model_path='resnet18_freezed.pth',
                    imgs_dir='videos/video1/frames',
                    class_names=class_names,
                    step = 1,
                    ratio = ratio
                )

#Considerando que se asume que cada movimiento dura ratio.
# EL primer movimiento dura de 0 a ratio, el segundo de ratio a 2 ratio y así sucesivamente,
def generar_json_movimientos(vector_clases, fps, ratio, step):
    """
    Genera un JSON con movimientos y sus tiempos de inicio/fin,
    considerando el 'step' (cuántos frames se saltan al guardar).
    """

    # FPS efectivos luego de aplicar step
    fps_efectivos = fps / step

    def formatear_tiempo(seg):
        h = int(seg // 3600)
        m = int((seg % 3600) // 60)
        s = seg % 60  # incluye parte decimal
        return f"{h:02d}:{m:02d}:{s:05.2f}"

    movimientos = []

    for i, clase in enumerate(vector_clases):
        # Cada "bloque" representa ratio frames procesados (ya filtrados por step)
        tiempo_inicio_seg = (i * ratio) / fps_efectivos
        tiempo_fin_seg = ((i + 1) * ratio) / fps_efectivos

        movimientos.append({
            "movimiento": clase,
            "tiempo_inicio": formatear_tiempo(tiempo_inicio_seg),
            "tiempo_termino": formatear_tiempo(tiempo_fin_seg)
        })
    
    return movimientos


movs = generar_json_movimientos(vector_clases, fps, ratio, step=step)
print(json.dumps(movs, indent=4, ensure_ascii=False))
