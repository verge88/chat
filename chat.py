from flask import Flask, request, jsonify
from gradio_client import Client
import os
import json

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

# Путь для сохранения временных файлов
TEMP_DIR = 'temp_files'
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/add_text', methods=['POST'])
def add_text():
    try:
        # Получение данных из запроса
        data = request.json
        query = data.get('query', '')
        history = data.get('history', [])
        
        # Обработка загруженных файлов
        files = request.files.getlist('files')
        uploaded_files = []
        for file in files:
            file_path = os.path.join(TEMP_DIR, file.filename)
            file.save(file_path)
            uploaded_files.append(file_path)

        # Создание входных данных для API
        _input = {
            "files": uploaded_files,
            "text": query
        }
        
        # Вызов модели через Gradio
        result = client.predict(
            _input=_input,
            _chatbot=history,
            api_name="/add_text"
        )

        # Извлечение результатов
        new_history = result[0]
        updated_chatbot = result[1]

        return jsonify({
            'new_history': new_history,
            'updated_chatbot': updated_chatbot
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
