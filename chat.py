from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/add_text', methods=['POST'])
def add_text():
    try:
        text = request.form.get('text', '')
        files = request.files.getlist('files')

        # Логика обработки текста и файлов
        if not text and not files:
            return jsonify({'error': 'No input provided'}), 400

        # Пример возвращаемого значения
        new_history = {
            'type': 'update',
            'interactive': False,
            'value': {'files': [], 'text': f"Processed: {text}"}
        }

        updated_chatbot = [
            [{'avatar': '', 'elem_classes': None, 'text': f"'{text}'"}, None]
        ]

        return jsonify({
            'new_history': new_history,
            'updated_chatbot': updated_chatbot
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
