from flask import Flask, request, jsonify
from gradio_client import Client
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

@app.route('/predict', methods=['POST'])
def predict():
    # Проверка наличия текста в запросе
    input_text = request.form.get('text', '')
    if not input_text:
        return jsonify({'error': 'Missing required parameter: text'}), 400

    # Проверка наличия файлов в запросе
    files = request.files.getlist('files')
    uploaded_files = []

    for file in files:
        try:
            # Сохранение файлов во временной директории для чтения
            file_path = os.path.join('temp', file.filename)
            os.makedirs('temp', exist_ok=True)
            file.save(file_path)
            uploaded_files.append(file_path)
        except Exception as e:
            return jsonify({'error': f"Failed to process file {file.filename}: {str(e)}"}), 500

    try:
        # Gradio prediction
        file_data = [{"name": os.path.basename(f), "content": open(f, 'rb').read()} for f in uploaded_files]
        result = client.predict(
            _input={"files": file_data, "text": input_text},
            _chatbot=[],
            api_name="/agent_run"
        )

        # Удаляем временные файлы
        for file_path in uploaded_files:
            os.remove(file_path)

        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
