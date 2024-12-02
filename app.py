import os
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

app = Flask(__name__)

# Configurar diretório de uploads
UPLOAD_FOLDER = './upload'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Criar a pasta se não existir
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Carregar o modelo
reconstructed_model = load_model("my_model.keras")

# Classes do modelo
CLASSES = ['avião', 'carro', 'pássaro', 'gato', 'veado', 'cachorro', 'sapo', 'cavalo', 'navio', 'caminhonete']

# Função para pré-processar a imagem
def preprocess_image(image_path):
    # Carregar a imagem e redimensionar para (32, 32)
    img = load_img(image_path, target_size=(32, 32))
    img_array = img_to_array(img)  # Converter para array
    img_array = img_array.astype('float32') / 255.0  # Normalizar
    img_array = np.expand_dims(img_array, axis=0)  # Adicionar dimensão de batch
    return img_array

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Validar se o arquivo foi enviado
        file_name = request.headers.get('Content-Disposition', '').split('filename=')[-1].strip('"')
        if not file_name:
            return "Nome do arquivo ausente!", 400

        # Salvar o arquivo no servidor
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        with open(file_path, 'wb') as f:
            f.write(request.data)

        print(f"Arquivo salvo em {file_path}")

        # Pré-processar a imagem
        img_array = preprocess_image(file_path)

        # Fazer a predição
        prediction = reconstructed_model.predict(img_array)
        predicted_index = np.argmax(prediction)  # Índice da classe predita
        predicted_class = CLASSES[predicted_index]  # Nome da classe predita
        confidence = prediction[0][predicted_index]  # Confiança

        print(f"Predição: {predicted_class} com confiança {confidence}")

        # Retornar resposta para o Node.js
        return jsonify({
            "confidence": float(confidence),
            "predicted_class": predicted_class
        }), 200
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(port=5000)

