from flask import Flask, request, jsonify
from gradio_client import Client, handle_file
import textract
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

@app.route('/predict', methods=['POST'])
def predict():
    # Проверяем наличие файла в запросе
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    # Сохраняем временный файл
    temp_path = os.path.join('/tmp', file.filename)
    file.save(temp_path)
    
    try:
        # Используем textract для конвертации файла в строку
        input_text = textract.process(temp_path).decode('utf-8')
        
        # Удаляем временный файл
        os.remove(temp_path)
        
        # Первый вызов для добавления текста
        client.predict(
            _input={"files": [], "text": input_text},
            _chatbot=[],
            api_name="/add_text"
        )
        
        # Второй вызов для запуска агента
        result = client.predict(
            _chatbot=[[{
                "id": None, 
                "elem_id": None, 
                "elem_classes": None, 
                "name": None,
                "text": input_text,
                "files": []
            }, None]],
            api_name="/agent_run"
        )
        
        return jsonify({'result': result}), 200
    
    except Exception as e:
        # Удаляем временный файл в случае ошибки
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
