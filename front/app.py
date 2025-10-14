from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración de uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Crear carpeta de uploads si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página principal con el formulario"""
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    """Procesa el video subido y realiza el análisis"""
    
    # Validar que se haya enviado un archivo
    if 'video' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['video']
    
    # Validar que se haya seleccionado un archivo
    if file.filename == '':
        return redirect(url_for('index'))
    
    # Obtener otros datos del formulario
    titulo = request.form.get('titulo', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    
    # Validar título
    if not titulo:
        return redirect(url_for('index'))
    
    # Validar y guardar el archivo
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Agregar timestamp para evitar colisiones de nombres
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            
            # Aquí falta llamar al modelo de IA para analizar el video
            # TODO: Integrar el modelo de IA
            # El modelo retorna una lista con este formato:
            # [
            #   {
            #     "movimiento": "backhand",  # serve, forehand, backhand, ready_position
            #     "tiempo_inicio": "00:00:00.00",
            #     "tiempo_termino": "00:00:01.00"
            #   },
            #   ...
            # ]
            # resultado = modelo_ia.analizar_video(filepath)
            # detecciones = resultado  # Lista de detecciones con timestamps
            
            # Aquí hay que redirigir a la página de resultados cuando esté lista
            # return redirect(url_for('resultados', video_id=video_id))
            return redirect(url_for('index'))
            
        except Exception as e:
            print(f'Error al guardar el archivo: {str(e)}')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/resultados/<video_id>')
def resultados(video_id):
    """Muestra los clips recortados por tipo de jugada (placeholder)"""
    # TODO: Implementar la página de resultados
    # Aquí debo mostrar las detecciones agrupadas por tipo de movimiento:
    # - serve (Saque)
    # - forehand (Derecha)
    # - backhand (Revés)
    # - ready_position (Posición de Espera)
    # Cada detección tiene tiempo_inicio y tiempo_termino para recortar el video
    return f"<h1>Clips de tu partido</h1><p>Video ID: {video_id}</p><p>Aquí verás tus clips organizados por tipo de jugada</p>"

@app.errorhandler(413)
def too_large(e):
    """Maneja errores de archivos demasiado grandes"""
    print('Error: El archivo es demasiado grande. El tamaño máximo es 100MB.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
