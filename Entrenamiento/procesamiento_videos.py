import cv2
import os

def procesar_video(video_path, guardar_cada: int = 1):
    """
    Procesa un video: crea la carpeta de frames, extrae fotogramas y devuelve información básica.

    Parámetros:
        video_path (str): Ruta del archivo de video.
        guardar_cada (int): Guarda 1 de cada 'n' fotogramas (por defecto = 1, guarda todos).

    Retorna:
        dict: Contiene FPS, total de fotogramas y duración del video.
    """
    # Verificar que el archivo exista
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"No se encontró el archivo: {video_path}")

    # Obtener la carpeta donde está el video
    video_dir = os.path.dirname(video_path)

    # Crear carpeta "frames" dentro de esa carpeta si no existe
    frames_dir = os.path.join(video_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Abrir el video
    cap = cv2.VideoCapture(video_path)

    # Obtener información del video
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    print(f"FPS del video: {fps}")
    print(f"Total de fotogramas: {total_frames}")
    print(f"Duración del video: {duration:.2f} segundos")

    # Procesar y guardar fotogramas
    frame_number = 0
    saved_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_number % guardar_cada == 0:
            frame_filename = os.path.join(frames_dir, f"frame_{frame_number:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            saved_frames += 1

        frame_number += 1

    cap.release()

    print(f"✅ Se guardaron {saved_frames} fotogramas en '{frames_dir}'")

    # Retornar resultados
    return {
        "fps": fps,
        "total_frames": total_frames,
        "duration": duration,
        "frames_guardados": saved_frames,
        "carpeta_frames": frames_dir
    }

#info = procesar_video("videos/video1/prueba1.mp4", guardar_cada=2)
#print(info)
