from flask import Flask, request, jsonify
from gradio_client import Client, handle_file
import textract
import os

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

@app.route('/predict', methods=['POST'])
def predict():
    # Получение данных из запроса
    test_name = request.form.get('test_name')
    question_count = request.form.get('question_count')
    source_text = request.form.get('source_text', '')
    file = request.files.get('file')

    # Проверка наличия обязательных полей
    if not all([test_name, question_count]) or (not source_text and not file):
        return jsonify({'error': 'Необходимо указать название теста, количество вопросов и хотя бы один источник текста (поле или файл).'}), 400
    
        
    # Сохраняем временный файл
    temp_path = os.path.join('/tmp', file.filename)
    file.save(temp_path)
    
    try:
        # Используем textract для конвертации файла в строку
        source_text = textract.process(temp_path).decode('utf-8')
        
        # Удаляем временный файл
        os.remove(temp_path)
        
        # Первый вызов для добавления текста
        client.predict(
            _input={"files": [], "text": f"напиши {question_count} тестовых вопросов на основе данного {source_text} в виде кода SQLite для добавления в таблицу базы данных (в ответ дай только код для добавления вопросов в таблицу. Вот пример кода: INSERT INTO generated (id, question, correctAnswer, incorrectAnswers) VALUES(NULL, 'текст вопроса', 'правильный ответ', 'неправильный вариант ответа|неправильный вариант ответа|неправильный вариант ответа');)" + input_text},
            _chatbot=[],
            api_name="/add_text"
        )
        
        # Второй вызов для запуска агента
        result = client.predict(
            _chatbot=[[{
                "id": None, 
                "elem_id": None, 
                "elem_classes": None, 
                "name": None,
                "text": f"напиши {question_count} тестовых вопросов на основе данного {source_text} в виде кода SQLite для добавления в таблицу базы данных (в ответ дай только код для добавления вопросов в таблицу. Вот пример кода: INSERT INTO generated (id, question, correctAnswer, incorrectAnswers) VALUES(NULL, 'текст вопроса', 'правильный ответ', 'неправильный вариант ответа|неправильный вариант ответа|неправильный вариант ответа');)" + input_text},
                "files": []
            }, None]],
            api_name="/agent_run"
        )
        
        return jsonify({'result': result}), 200
    
    except Exception as e:
        # Удаляем временный файл в случае ошибки
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
