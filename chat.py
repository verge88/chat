from flask import Flask, request, jsonify
from gradio_client import Client

app = Flask(__name__)

# Создаем клиент для API Qwen
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

@app.route('/add_text', methods=['POST'])
def add_text():
    data = request.json
    input_text = data.get("text", "")
    files = data.get("files", [])

    try:
        result = client.predict(
            _input={"files": files, "text": input_text},
            _chatbot=[],
            api_name="/add_text"
        )
        return jsonify(result=result)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/agent_run', methods=['POST'])
def agent_run():
    try:
        result = client.predict(
            _chatbot=[],
            api_name="/agent_run"
        )
        return jsonify(result=result)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/flushed', methods=['POST'])
def flushed():
    try:
        result = client.predict(
            api_name="/flushed"
        )
        return jsonify(result=result)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(port=5000)
