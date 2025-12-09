from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = 'uploads'
COMMENTS_FOLDER = 'comments'
PROCESSING_FOLDER = 'processing_cache'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Crear carpetas si no existen
for folder in [UPLOAD_FOLDER, COMMENTS_FOLDER, PROCESSING_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Funciones auxiliares
def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_json_file(folder, video_filename):
    """Obtiene la ruta de un archivo JSON para un video"""
    base_name = os.path.splitext(video_filename)[0]
    return os.path.join(folder, f"{base_name}.json")

def load_json_data(filepath):
    """Carga datos desde un archivo JSON"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_json_data(filepath, data):
    """Guarda datos en un archivo JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Funciones de comentarios
def load_comments(video_filename):
    """Carga los comentarios de un video"""
    filepath = get_json_file(COMMENTS_FOLDER, video_filename)
    comments = load_json_data(filepath)
    return comments if comments else []

def save_comment(video_filename, comment_text):
    """Guarda un nuevo comentario para un video"""
    comments = load_comments(video_filename)
    
    new_comment = {
        'text': comment_text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'id': len(comments) + 1
    }
    
    comments.append(new_comment)
    filepath = get_json_file(COMMENTS_FOLDER, video_filename)
    save_json_data(filepath, comments)
    
    return new_comment

# Funciones de procesamiento
def load_processing_data(video_filename):
    """Carga los datos de procesamiento de un video"""
    filepath = get_json_file(PROCESSING_FOLDER, video_filename)
    return load_json_data(filepath)

def save_processing_data(video_filename, samples):
    """Guarda los datos de procesamiento de un video"""
    processing_data = {
        'video_filename': video_filename,
        'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'samples': samples
    }
    
    filepath = get_json_file(PROCESSING_FOLDER, video_filename)
    save_json_data(filepath, processing_data)
    
    return processing_data

# Rutas principales
@app.route('/')
def index():
    """Página principal con el formulario"""
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    """Procesa el video subido y realiza el análisis"""
    if 'video' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['video']
    
    if file.filename == '':
        return redirect(url_for('index'))
    
    titulo = request.form.get('titulo', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    
    if not titulo:
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            return redirect(url_for('index'))
        except Exception as e:
            print(f'Error al guardar el archivo: {str(e)}')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/resultados/<video_id>')
def resultados(video_id):
    """Muestra los clips recortados por tipo de jugada (placeholder)"""
    return f"<h1>Clips de tu partido</h1><p>Video ID: {video_id}</p>"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Sirve los archivos de video desde la carpeta uploads"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/revision')
def revision():
    """Muestra la interfaz de revisión de videos"""
    videos = []
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                videos.append({
                    'filename': filename,
                    'url': url_for('uploaded_file', filename=filename)
                })
    return render_template('video_revision.html', videos=videos)

# API de comentarios
@app.route('/api/comments/<video_filename>', methods=['GET'])
def get_comments(video_filename):
    """Obtiene los comentarios de un video"""
    comments = load_comments(video_filename)
    return jsonify({'success': True, 'comments': comments})

@app.route('/api/comments/<video_filename>', methods=['POST'])
def add_comment(video_filename):
    """Agrega un comentario a un video"""
    try:
        data = request.get_json()
        comment_text = data.get('comment', '').strip()
        
        if not comment_text:
            return jsonify({'success': False, 'error': 'El comentario no puede estar vacío'}), 400
        
        new_comment = save_comment(video_filename, comment_text)
        return jsonify({'success': True, 'comment': new_comment})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/comments/<video_filename>/<int:comment_id>', methods=['DELETE'])
def delete_comment(video_filename, comment_id):
    """Elimina un comentario de un video"""
    try:
        comments = load_comments(video_filename)
        comments = [c for c in comments if c['id'] != comment_id]
        
        filepath = get_json_file(COMMENTS_FOLDER, video_filename)
        save_json_data(filepath, comments)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API de procesamiento
@app.route('/api/processing/<video_filename>', methods=['GET'])
def get_processing(video_filename):
    """Consulta si un video ya fue procesado"""
    processing_data = load_processing_data(video_filename)
    
    if processing_data:
        return jsonify({'success': True, 'cached': True, 'data': processing_data})
    else:
        return jsonify({'success': True, 'cached': False})

@app.route('/api/processing/<video_filename>', methods=['POST'])
def save_processing(video_filename):
    """Guarda el resultado del procesamiento de un video"""
    try:
        data = request.get_json()
        samples = data.get('samples', [])
        
        if not samples:
            return jsonify({'success': False, 'error': 'No hay datos para guardar'}), 400
        
        processing_data = save_processing_data(video_filename, samples)
        return jsonify({'success': True, 'data': processing_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Manejo de errores
@app.errorhandler(413)
def too_large(e):
    """Maneja errores de archivos demasiado grandes"""
    print('Error: El archivo es demasiado grande. El tamaño máximo es 100MB.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)