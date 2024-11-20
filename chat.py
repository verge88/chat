from flask import Flask, request, jsonify
from gradio_client import Client

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-72B-Instruct")

@app.route('/model_chat', methods=['POST', 'GET'])
def predict():
    try:
        # Обработка текстового ввода
        query = request.form.get('input_text', '') if request.method == 'POST' else request.args.get('input_text', '')

        if not query:
            return jsonify({'error': 'Missing required input_text'}), 400

        # Обработка файла, если предоставлен
        file = request.files.get('file')
        file_data = None
        if file:
            file_data = {'file': file, 'alt_text': file.filename}

        # Вызов модели через Gradio
        result = client.predict(
            query=query,
            history=[file_data],
            system="You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
            api_name="/model_chat"
        )

        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
