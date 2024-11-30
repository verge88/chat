from flask import Flask, request, jsonify
from gradio_client import Client, handle_file
import textract
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

@app.route('/predict', methods=['POST'])
def predict():
    # Extract form fields
    test_name = request.form.get('testName', '')
    question_count = request.form.get('questionCount', '5')
    source_text = request.form.get('text', '')

    # Validate required fields
    if not test_name or not question_count:
        return jsonify({'error': 'Missing test name or question count'}), 400

    # Check if files are uploaded
    input_text = source_text
    if 'file' in request.files:
        file = request.files['file']
        
        # Ensure filename is safe
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Save temporary file
        temp_path = os.path.join('/tmp', file.filename)
        file.save(temp_path)
        
        try:
            # Convert file to text
            input_text += ' ' + textract.process(temp_path).decode('utf-8')
            
            # Remove temporary file
            os.remove(temp_path)
        except Exception as e:
            # Remove temporary file if exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'error': f'File processing error: {str(e)}'}), 500
    
    # Validate input text
    if not input_text:
        return jsonify({'error': 'No source text provided'}), 400

    try:
        # Prepare prompt with question count
        prompt = f"напиши {question_count} тестовых вопросов на основе данного текста в виде кода SQLite для добавления в таблицу базы данных (в ответ дай только код для добавления вопросов в таблицу. Вот пример кода: INSERT INTO generated (id, question, correctAnswer, incorrectAnswers) VALUES(NULL, 'текст вопроса', 'правильный ответ', 'неправильный вариант ответа|неправильный вариант ответа|неправильный вариант ответа');)" + input_text

        # First call to add text
        client.predict(
            _input={"files": [], "text": prompt},
            _chatbot=[],
            api_name="/add_text"
        )
        
        # Second call to run agent
        result = client.predict(
            _chatbot=[[{
                "id": None, 
                "elem_id": None, 
                "elem_classes": None, 
                "name": None,
                "text": prompt,
                "files": []
            }, None]],
            api_name="/agent_run"
        )
        
        return jsonify({
            'result': result, 
            'testName': test_name, 
            'questionCount': question_count
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
