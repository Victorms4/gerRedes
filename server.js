const express = require('express');
const multer = require('multer');
const axios = require('axios');

const app = express();
const upload = multer(); // Armazenar o arquivo em buffer
const PORT = 3000;

// Servir arquivos estáticos
app.use(express.static('.'));

// Rota para upload
app.post('/upload', upload.single('photo'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).send('Nenhum arquivo foi enviado!');
        }

        console.log('Recebendo arquivo do front-end...');
        console.log(`Nome do arquivo: ${req.file.originalname}`);
        console.log(`Mimetype: ${req.file.mimetype}`);

        // Enviar arquivo para o Flask
        const flaskResponse = await axios.post('http://localhost:5000/upload', req.file.buffer, {
            headers: {
                'Content-Type': req.file.mimetype,
                'Content-Disposition': `attachment; filename="${req.file.originalname}"`,
            },
        });

        console.log('Resposta do Flask:', flaskResponse.data);

        // Enviar o resultado da predição para o front-end
        res.json({
            message: "Arquivo processado com sucesso!",
            prediction: flaskResponse.data
        });
    } catch (error) {
        console.error('Erro ao enviar para o Flask:', error.message);
        res.status(500).send('Erro ao processar o upload');
    }
});

// Iniciar o servidor
app.listen(PORT, () => {
    console.log(`Servidor Node.js rodando em http://localhost:${PORT}`);
});

