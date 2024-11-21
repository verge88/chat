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
        # Получаем текст и файлы из запроса
        text = request.form.get("text", "")
        files = request.files.getlist("files")

        # Сохраняем файлы во временную папку
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

        # Преобразуем результат из tuple в JSON-совместимый формат
        if isinstance(result, tuple):
            result_dict = {
                "new_history": result[0],
                "updated_chatbot": result[1]
            }
        else:
            result_dict = {"result": result}

        # Возвращаем результат клиенту
        return jsonify(result_dict), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
