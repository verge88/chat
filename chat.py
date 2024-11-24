from flask import Flask, request, jsonify
from gradio_client import Client
import tempfile
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    try:
        input_text = request.form.get('text', '')
        files = request.files.getlist('files')
        
        files_data = []
        if files:
            for file in files:
                # Создаем временный файл
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, file.filename)
                
                # Сохраняем файл
                file.save(temp_path)
                
                files_data.append({
                    "file": temp_path,
                    "alt_text": file.filename
                })

        # Отправляем запросы в Gradio
        client.predict(
            _input={"files": files_data, "text": input_text},
            _chatbot=[],
            api_name="/add_text"
        )

        result = client.predict(
            _chatbot=[[{
                "id": None,
                "elem_id": None,
                "elem_classes": None,
                "name": None,
                "text": input_text,
                "flushing": None,
                "avatar": "",
                "files": files_data
            }, None]],
            api_name="/agent_run"
        )

        # Очищаем временные файлы
        for file_data in files_data:
            try:
                os.remove(file_data["file"])
                os.rmdir(os.path.dirname(file_data["file"]))
            except:
                pass

        return jsonify({'result': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
