from flask import Flask, request, jsonify
from gradio_client import Client
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

# Путь для сохранения временных файлов
TEMP_DIR = 'temp_files'
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    try:
        # Обработка текстового ввода
        query = request.form.get('query', '') if request.method == 'POST' else request.args.get('query', '')

        if not query:
            return jsonify({'error': 'Missing required query'}), 400

        # Обработка истории чата, если предоставлена
        history = request.form.get('history', []) if request.method == 'POST' else request.args.get('history', [])
        if isinstance(history, str):
            history = eval(history)  # Convert string representation of list to list

        # Обработка системного сообщения, если предоставлено
        system = request.form.get('system', 'You are Qwen, created by Alibaba Cloud. You are a helpful assistant.') if request.method == 'POST' else request.args.get('system', 'You are Qwen, created by Alibaba Cloud. You are a helpful assistant.')

        # Обработка загруженных файлов
        uploaded_files = []
        for file in request.files.getlist('file'):
            if file.filename != '':
                filename = os.path.join(TEMP_DIR, file.filename)
                file.save(filename)
                uploaded_files.append(filename)

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
