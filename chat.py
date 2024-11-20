from flask import Flask, request, jsonify
from gradio_client import Client

app = Flask(__name__)
client = Client("yuntian-deng/ChatGPT4")


@app. route('/predict', methods=['POST', 'GET' ])
def predict():
    # Extract the required parameters from the incoming request
    data = request.args

    # Validate and retrieve the necessary parameters
    input_text = data.get('input_text', '')


    if not input_text:
        return jsonify({'error': 'Missing required parameters'}), 400
    try:
        # Use the Gradio client to make a prediction
        result = client.predict(
            inputs=input_text,
            top_p=1,
            temperature=1,
            chat_counter=0,
            chatbot=[],
            api_name="/predict"
        )

        return jsonify({'result': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
