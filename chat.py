from flask import Flask, request, jsonify
from gradio_client import Client
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    try:
        # Извлечение текста
        input_text = request.form.get('text', '')

        if not input_text:
            return jsonify({'error': 'Missing required "text" parameter'}), 400

        # Извлечение файлов
        uploaded_files = request.files.getlist('files')
        files_content = []

        for file in uploaded_files:
            # Читаем содержимое файлов
            files_content.append({
                'filename': file.filename,
                'content': file.read().decode('utf-8')  # Пример для текстовых файлов
            })

        # Используем Gradio клиент для обработки
        result = client.predict(
            _input={"files": files_content, "text": input_text},
            _chatbot=[],
            api_name="/add_text"
        )

        response = client.predict(
            _chatbot=[
                [{
                    "id": None,
                    "elem_id": None,
                    "elem_classes": None,
                    "name": None,
                    "text": input_text,
                    "files": files_content
                }, None]
            ],
            api_name="/agent_run"
        )

        return jsonify({'result': response}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
