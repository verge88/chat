from flask import Flask, request, jsonify
from gradio_client import Client
import textract
import os
import logging
import traceback

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Max-Demo")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract form fields
        test_name = request.form.get('testName', '')
        question_count = request.form.get('questionCount', '5')
        source_text = request.form.get('text', '')
        
        logger.debug(f"Request received: test_name={test_name}, question_count={question_count}")
        
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
            logger.debug(f"File saved at {temp_path}")
            
            try:
                # Convert file to text
                input_text += ' ' + textract.process(temp_path).decode('utf-8')
                logger.debug("File processed successfully")
                
                # Remove temporary file
                os.remove(temp_path)
            except Exception as e:
                logger.error(f"File processing error: {str(e)}")
                # Remove temporary file if exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return jsonify({'error': f'File processing error: {str(e)}'}), 500
        
        # Validate input text
        if not input_text:
            return jsonify({'error': 'No source text provided'}), 400
        
        logger.debug("Preparing to send request to Qwen model")
        
        # Prepare prompt
        prompt = f"напиши {question_count} тестовых вопросов на основе данного текста в виде кода SQLite для добавления в таблицу базы данных (в ответ дай ТОЛЬКО код для добавления вопросов в таблицу. Вот пример кода: INSERT INTO generated (id, question, correctAnswer, incorrectAnswers) VALUES(NULL, 'текст вопроса', 'правильный ответ', 'неправильный вариант ответа|неправильный вариант ответа|неправильный вариант ответа');) {input_text}"
        
        # Пробуем без предварительной очистки сессии
        try:
            logger.debug("Sending request to model")
            result = client.predict(
                query=prompt,
                history=[],
                system="You are a helpful assistant.",
                api_name="/model_chat",
                #timeout=180  # Увеличиваем время ожидания до 3 минут
            )
            
            logger.debug(f"Response received: {result}")
            
            # Проверим структуру ответа
            if isinstance(result, tuple) and len(result) >= 2:
                model_response = result[1]
                if isinstance(model_response, list) and len(model_response) > 0:
                    sql_code = model_response[-1][1] if len(model_response[-1]) > 1 else "No response data"
                else:
                    sql_code = "Empty response from model"
            else:
                sql_code = str(result)  # Возвращаем весь результат, если структура не соответствует ожиданиям
            
            return jsonify({
                'result': sql_code, 
                'testName': test_name, 
                'questionCount': question_count
            }), 200
            
        except Exception as model_error:
            logger.error(f"Model prediction error: {str(model_error)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': f"Model prediction error: {str(model_error)}",
                'stack': traceback.format_exc()
            }), 500
    
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'stack': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
