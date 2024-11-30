from flask import Flask, request, jsonify
from gradio_client import Client, handle_file
import textract
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")




@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Получаем параметры
        test_name = request.form.get('testName')
        question_count = request.form.get('questionCount')
        text = request.form.get('text', '')

        # Если текст отсутствует, используем прикрепленный файл
        if not text and 'file' in request.files:
            file = request.files['file']
            temp_path = os.path.join('/tmp', file.filename)
            file.save(temp_path)
            text = textract.process(temp_path).decode('utf-8')
            os.remove(temp_path)

        if not text:
            return jsonify({'error': 'Текст или файл не предоставлены'}), 400

            # Первый вызов для добавления текста
        client.predict(
            _input={"files": [],
                        "text": f"напиши {question_count} тестовых вопросов на основе данного текста {text} в виде кода SQLite для добавления в таблицу базы данных (в ответ дай только код для добавления вопросов в таблицу. Вот пример кода: INSERT INTO generated (id, question, correctAnswer, incorrectAnswers) VALUES(NULL, 'текст вопроса', 'правильный ответ', 'неправильный вариант ответа|неправильный вариант ответа|неправильный вариант ответа');)"},
            _chatbot=[],
            api_name="/add_text"
        )
        
        # Генерация SQL-запросов
        prompt = f"напиши {question_count} тестовых вопросов на основе данного текста {text} в виде кода SQLite для добавления в таблицу базы данных (в ответ дай только код для добавления вопросов в таблицу. Вот пример кода: INSERT INTO generated (id, question, correctAnswer, incorrectAnswers) VALUES(NULL, 'текст вопроса', 'правильный ответ', 'неправильный вариант ответа|неправильный вариант ответа|неправильный вариант ответа');)"}
        result = client.predict(_chatbot=[[{"text": prompt, "files": []}, None]], api_name="/agent_run")

        return jsonify({'result': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
