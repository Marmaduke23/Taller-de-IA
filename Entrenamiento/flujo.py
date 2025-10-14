from procesamiento_videos import procesar_video
from predecir import predict_video_frames
import json



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

