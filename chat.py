from flask import Flask, request, jsonify
from gradio_client import Client
app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")
@app. route('/predict', methods=['POST', 'GET' ])
def predict():
    # Extract the required parameters from the incoming request
    data = request.args
    # Validate and retrieve the necessary parameters
    input_text = data.get('text', '')
    if not input_text:
        return jsonify({'error': 'Missing required parameters'}), 400
        # Обработка файла, если предоставлен
    file = request.files.get('file')
    file_data = None
    if file:
        file_data = {'file': file, 'alt_text': file.filename}
    try:
        client.predict(
            input={"files": [filedata] if file_data else [], "text": input_text},
            _chatbot=[],
            api_name="/add_text"
        )
        result = client.predict(
            _chatbot=[[
                          {"id": None, "elem_id": None, "elem_classes": None, "name": None,
                           "text": input_text,
                           "files": [file_data] if file_data else []}, None]],
            api_name="/agent_run"
        )
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if name == '__main__':
    app.run(debug=True)
