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
    try:
        # Use the Gradio client to make a prediction
        # result = client.predict(
		# 	_input={"files": [], "text": input_text},
		# 	_chatbot=[],
		# 	api_name="/agent_run"
        # )

        client.predict(
            _input={"files": [], "text": input_text},
            _chatbot=[],
            api_name="/add_text"
        )

        result = client.predict(
            _chatbot=[[{"id": None, "elem_id": None, "elem_classes": None, "name": None, "text": "hello",
                        "flushing": None, "avatar": "", "files": []}, [
                           {"id": None, "elem_id": None, "elem_classes": None, "name": None,
                            "text": '',
                            "flushing": None, "avatar": "", "files": []}]], [
                          {"id": None, "elem_id": None, "elem_classes": None, "name": None,
                           "text": input_text,
                           "files": []}, None]],
            api_name="/agent_run"
        )

        return jsonify({'result': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
