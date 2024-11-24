бfrom flask import Flask, request, jsonify
from gradio_client import Client

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")


@app.route('/predict', methods=['POST','GET'])
def predict():
    try:
        # Получение текста из запроса
        input_text = request.form.get('text', '')
        if not input_text:
            return jsonify({'error': 'Missing required text parameter'}), 400

        # Получение файлов из запроса
        uploaded_files = request.files.getlist('files')
        files_content = []

        for file in uploaded_files:
            # Чтение содержимого файла
            files_content.append({
                "name": file.filename,
                "content": file.read().decode('utf-8')  # Предполагается текстовый файл
            })

        # Вызов модели через Gradio-клиент
        result = client.predict(
            _input={"files": files_content, "text": input_text},
            _chatbot=[],
            api_name="/agent_run"
        )

        return jsonify({'result': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
