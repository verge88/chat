@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_text = request.form.get('text', '')
        if not input_text:
            input_text = "Проанализируйте прикрепленный файл" # Дефолтный текст если нет входного текста
            
        files = request.files.getlist('files')
        
        files_data = []
        if files:
            for file in files:
                # Создаем временный файл
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, file.filename)
                
                # Сохраняем файл
                file.save(temp_path)
                
                files_data.append({
                    "file": temp_path,
                    "alt_text": file.filename
                })

        # Формируем входные данные для Gradio
        input_data = {
            "files": files_data,
            "text": input_text
        }

        try:
            # Инициализация чата
            client.predict(
                _input=input_data,
                _chatbot=[],
                api_name="/add_text"
            )

            # Получение ответа
            result = client.predict(
                _chatbot=[[{
                    "id": None,
                    "elem_id": None,
                    "elem_classes": None,
                    "name": None,
                    "text": input_text,
                    "flushing": None,
                    "avatar": "",
                    "files": files_data
                }, None]],
                api_name="/agent_run"
            )

            # Очистка временных файлов
            for file_data in files_data:
                try:
                    os.remove(file_data["file"])
                    os.rmdir(os.path.dirname(file_data["file"]))
                except:
                    pass

            return jsonify({'result': result}), 200

        except Exception as e:
            print(f"Error in Gradio API call: {str(e)}")
            raise

    except Exception as e:
        print(f"Error in predict route: {str(e)}")
        return jsonify({'error': str(e)}), 500
