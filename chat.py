from flask import Flask, request, jsonify
from gradio_client import Client, handle_file
import textract
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")
#client = Client("Qwen/Qwen/Qwen2.5-Max-Demo")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract form fields
        test_name = request.form.get('testName', '')
        question_count = request.form.get('questionCount', '5')
        source_text = request.form.get('text', '')

        # Validate required fields
        if not test_name or not question_count:
            return jsonify({'error': 'Missing test name or question count'}), 400

        # Check if files are uploaded
        input_text = source_text
        
        # Handle multiple files
        uploaded_files = request.files.getlist('file')
        for file in uploaded_files:
            # Ensure filename is safe
            if file.filename == '':
                continue
            
            # Save temporary file
            temp_path = os.path.join('/tmp', file.filename)
            file.save(temp_path)
            
            try:
                # Convert file to text
                file_text = textract.process(temp_path).decode('utf-8')
                input_text += ' ' + file_text
                print(f"Processed file: {file.filename}, extracted {len(file_text)} characters")
                
            except Exception as e:
                print(f"Error processing file {file.filename}: {str(e)}")
            finally:
                # Always remove temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # Validate input text
        if not input_text:
            return jsonify({'error': 'No source text provided'}), 400

        # Prepare prompt with question count
        prompt = f"напиши {question_count} тестовых вопросов на основе данного текста в виде кода SQLite для добавления в таблицу базы данных (в ответ дай ТОЛЬКО код для добавления вопросов в таблицу. Вот пример кода: INSERT INTO generated (id, question, correctAnswer, incorrectAnswers) VALUES(NULL, 'текст вопроса', 'правильный ответ', 'неправильный вариант ответа|неправильный вариант ответа|неправильный вариант ответа');)" + input_text

        print(f"Sending prompt with {len(prompt)} characters")
        
        # First call to add text with increased timeout
        client.predict(
            _input={"files": [], "text": prompt},
            _chatbot=[],
            api_name="/add_text",
            #timeout=180  # 3 minutes
        )
        
        # Second call to run agent with increased timeout
        result = client.predict(
            _chatbot=[[{
                "id": None, 
                "elem_id": None, 
                "elem_classes": None, 
                "name": None,
                "text": prompt,
                "files": []
            }, None]],
            api_name="/agent_run",
            #timeout=180  # 3 minutes
        )
        
        print("Successfully generated response")
        return jsonify({
            'result': result, 
            'testName': test_name, 
            'questionCount': question_count
        }), 200
    
    except Exception as e:
        import traceback
        print(f"Error in predict endpoint: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
