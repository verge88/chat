from flask import Flask, request, jsonify
from gradio_client import Client
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

# Путь для сохранения временных файлов
TEMP_DIR = 'temp_files'
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Получение данных из запроса
        data = request.json
        query = data.get('query', '')
        history = data.get('history', [])
        system = data.get('system', 'You are Qwen, created by Alibaba Cloud. You are a helpful assistant.')
        files = data.get('files', [])

        # Обработка загруженных файлов
        uploaded_files = []
        for file_path in files:
            file_name = os.path.basename(file_path)
            destination = os.path.join(TEMP_DIR, file_name)
            with open(file_path, 'rb') as f:
                with open(destination, 'wb') as f_out:
                    f_out.write(f.read())
            uploaded_files.append(destination)

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
        new_history = result[0]['value']
        updated_chatbot = result[1]

        return jsonify({
            'new_history': new_history,
            'updated_chatbot': updated_chatbot
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
