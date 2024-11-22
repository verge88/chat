import os
from flask import Flask, request, jsonify
from gradio_client import Client
from werkzeug.utils import secure_filename

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

# Настройки загрузки файлов
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Создаем папку для загрузок, если она не существует
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Проверка разрешенных расширений файлов"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    try:
        # Получаем текст из запроса
        input_text = request.form.get('text', '')
        
        # Обработка файлов
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and allowed_file(file.filename):
                    # Безопасно сохраняем файл
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    uploaded_files.append(filepath)

        # Проверяем наличие текста или файлов
        if not input_text and not uploaded_files:
            return jsonify({'error': 'Missing text or files'}), 400

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

        return jsonify({
            'result': result,
            'files_processed': len(uploaded_files)
        }), 200

    except Exception as e:
        # Очищаем файлы в случае ошибки
        for filepath in uploaded_files:
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
