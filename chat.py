from flask import Flask, request, jsonify
from gradio_client import Client
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-72B-Instruct")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Обработка текстового ввода
        query = request.form.get('query', '')

        if not query:
            return jsonify({'error': 'Missing required query'}), 400

        # Обработка истории чата, если предоставлена
        history = request.form.get('history', [])
        if isinstance(history, str):
            history = eval(history)  # Convert string representation of list to list

        # Обработка системного сообщения, если предоставлено
        system = request.form.get('system', 'You are Qwen, created by Alibaba Cloud. You are a helpful assistant.')

        # Обработка файла, если предоставлен
        file = request.files.get('file')
        file_data = None
        if file:
            file_path = os.path.join('/tmp', file.filename)
            file.save(file_path)
            file_data = {'file': file_path, 'alt_text': file.filename}

        # Вызов модели через Gradio
        result = client.predict(
            query=query,
            history=history,
            system=system,
            api_name="/model_chat"
        )

        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
