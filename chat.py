from flask import Flask, request, jsonify
from gradio_client import Client
import os

# Создаем клиент для обращения к API
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

# Инициализируем Flask
app = Flask(__name__)

# Директория для временного хранения загруженных файлов
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/add_text', methods=['POST'])
def add_text():
    try:
        # Проверяем, содержит ли запрос JSON-данные
        text = request.form.get("text", "")
        files = request.files.getlist("files")  # Список загруженных файлов

        # Сохраняем загруженные файлы во временную папку
        file_paths = []
        for file in files:
            if file.filename:
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                file_paths.append(file_path)

        # Выполняем запрос к API
        result = client.predict(
            _input={"files": file_paths, "text": text},
            _chatbot=[],
            api_name="/add_text"
        )

        # Очищаем временные файлы
        for file_path in file_paths:
            os.remove(file_path)

        # Возвращаем результат
        return jsonify({"result": result[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
