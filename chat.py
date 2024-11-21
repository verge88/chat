from flask import Flask, request, jsonify
from gradio_client import Client
import os

# Создаем клиент для обращения к API
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

# Директория для временного хранения загруженных файлов
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route('/add_text', methods=['POST', 'GET'])
def add_text():
    try:
        # Извлекаем текстовые данные из формы
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
        api_response = client.predict(
            _input={"files": file_paths, "text": text},
            _chatbot=[],
            api_name="/add_text"
        )

        # Очищаем временные файлы
        for file_path in file_paths:
            os.remove(file_path)

        # Обрабатываем ответ API
        new_history = api_response.get("new_history", {}).get("value", {})
        updated_chatbot = api_response.get("updated_chatbot", [])

        # Формируем финальный ответ
        result = {
            "new_history": new_history,
            "updated_chatbot": [
                {
                    "text": message.get("text", ""),
                    "avatar": message.get("avatar", ""),
                    "files": message.get("files", [])
                } if message else None
                for message, _ in updated_chatbot
            ]
        }

        # Возвращаем обработанный результат
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
