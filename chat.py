import os
from flask import Flask, request, jsonify
from gradio_client import Client
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

# Настройки загрузки файлов
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Ограничение 16 МБ

# Создаем папку для загрузок, если она не существует
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Проверка разрешенных расширений файлов"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    uploaded_files = []
    try:
        # Для GET-запросов
        if request.method == 'GET':
            input_text = request.args.get('text', '')
            file_params = request.args

        # Для POST-запросов
        else:
            input_text = request.form.get('text', '')
            file_params = request.files

        # Отладочная печать входящих параметров
        print(f"Входящий текст: {input_text}")
        print(f"Входящие параметры: {file_params}")

        # Обработка файлов
        if 'files' in file_params:
            files = file_params.getlist('files') if request.method == 'POST' else []
            for file in files:
                if file and (isinstance(file, str) or hasattr(file, 'filename')):
                    filename = file.filename if hasattr(file, 'filename') else file
                    if allowed_file(filename):
                        # Безопасно сохраняем файл
                        safe_filename = secure_filename(filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
                        
                        # Для POST-запросов сохраняем файл
                        if request.method == 'POST':
                            file.save(filepath)
                        
                        uploaded_files.append(filepath)

        # Проверяем наличие текста или файлов
        if not input_text and not uploaded_files:
            return jsonify({
                'error': 'Missing text or files', 
                'details': {
                    'text': input_text, 
                    'files_count': len(uploaded_files)
                }
            }), 400

        # Подготовка данных для Gradio клиента
        file_paths = uploaded_files if uploaded_files else []
        
        # Первый predict для добавления текста
        client.predict(
            input={"files": file_paths, "text": input_text},
            _chatbot=[],
            api_name="/add_text"
        )

        # Второй predict для получения ответа
        result = client.predict(
            _chatbot=[[
                {"id": None, "elem_id": None, "elem_classes": None, "name": None,
                 "text": input_text,
                 "files": file_paths}, None]],
            api_name="/agent_run"
        )

        # Очищаем загруженные файлы
        for filepath in uploaded_files:
            if os.path.exists(filepath):
                os.remove(filepath)

        # Возвращаем результат
        return jsonify({
            'result': result,
            'files_processed': len(uploaded_files),
            'input_text': input_text
        }), 200

    except Exception as e:
        # Очищаем файлы в случае ошибки
        for filepath in uploaded_files:
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Подробная информация об ошибке
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'input_details': {
                'text': input_text,
                'files_count': len(uploaded_files)
            }
        }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'error': 'File too large',
        'message': 'The uploaded file is too large. Maximum file size is 16 MB.'
    }), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
