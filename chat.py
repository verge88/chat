from flask import Flask, request, jsonify
from gradio_client import Client

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_text = data.get('text', '')

    if not input_text:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        client.predict(
            _input={"files": [], "text": input_text},
            _chatbot=[],
            api_name="/add_text"
        )

        result = client.predict(
            _chatbot=[[
                          {"id": None, "elem_id": None, "elem_classes": None, "name": None,
                           "text": input_text,
                           "files": []}, None]],
            api_name="/agent_run"
        )

        # Измените эту строку, чтобы вернуть только нужное значение
        return jsonify({
            'result': result[0][0]['text']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
