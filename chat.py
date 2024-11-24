from flask import Flask, request, jsonify
from gradio_client import Client
import tempfile
import os
import base64

app = Flask(__name__)
client = Client("Qwen/Qwen2.5-Turbo-1M-Demo")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_text = request.form.get('text', '')
        files = request.files.getlist('files')
        
        files_data = []
        if files:
            for file in files:
                # Создаем временный файл
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, file.filename)
                
                # Сохраняем файл
                file.save(temp_path)
                
                # Читаем файл как base64
                with open(temp_path, 'rb') as f:
                    file_content = f.read()
                    file_base64 = base64.b64encode(file_content).decode('utf-8')
                
                files_data.append({
                    "name": file.filename,
                    "data": f"data:application/octet-stream;base64,{file_base64}"
                })

        # Формируем входные данные для Gradio
        try:
            # Отправляем один запрос с текстом и файлами
            result = client.predict(
                fn_index=0,  # Индекс функции в Gradio
                text=input_text,
                files=files_data
            )

            # Очистка временных файлов
            for file in files:
                try:
                    temp_path = os.path.join(tempfile.gettempdir(), file.filename)
                    os.remove(temp_path)
                except:
                    pass

            return jsonify({'result': result}), 200

        except Exception as e:
            print(f"Error in Gradio API call: {str(e)}")
            raise

    except Exception as e:
        print(f"Error in predict route: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
