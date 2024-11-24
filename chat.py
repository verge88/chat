from flask import Flask, request, jsonify
from gradio_client import Client
import urllib.parse

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    try:
        # Получаем параметры из URL
        input_text = request.args.get('text', '')
        files = request.args.getlist('files')  # Получаем список файлов из параметров
        
        files_data = []
        if files:
            for file_path in files:
                # Декодируем путь файла
                decoded_path = urllib.parse.unquote(file_path)
                files_data.append({
                    "file": decoded_path,
                    "alt_text": decoded_path.split('/')[-1]
                })

        # Первый predict для инициализации
        client.predict(
            _input={"files": files_data, "text": input_text},
            _chatbot=[],
            api_name="/add_text"
        )

        # Второй predict для получения ответа
        result = client.predict(
            chatbot=[[{
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

        return jsonify({'result': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
