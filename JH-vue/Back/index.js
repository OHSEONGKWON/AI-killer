const express = require('express');
const axios = require('axios');
const cors = require('cors');

require('dotenv').config();

const app = express();
const port = 3000;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

// CORS 및 JSON 미들웨어 설정
app.use(cors({
    origin: 'http://localhost:8080'
}));
app.use(express.json());

// Gemini API 엔드포인트
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-latest:generateContent';

app.post('/api/analyze', async (req, res) => {
    console.log('===== /api/analyze 요청 받음 =====');
    console.log('받은 데이터:', req.body);
    
    try {
        const userText = req.body.text;
        if (!userText || userText.trim() === '') {
            return res.status(400).json({ error: '분석할 텍스트가 필요합니다.' });
        }

        const prompt = `다음 텍스트가 인공지능(AI)이 작성했을 가능성이 몇 퍼센트인지 (0부터 100까지의 정수) 숫자만 응답해주세요. 텍스트: """${userText}"""`;
        
        const payload = {
            contents: [{ 
                parts: [{ text: prompt }] 
            }]
        };

        console.log('Gemini API 호출 중...');

        const geminiResponse = await axios.post(
            `${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, 
            payload,
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        console.log('Gemini API 응답 성공!');
        res.json(geminiResponse.data);
    } catch (error) {
        console.error('백엔드에서 Gemini API 호출 실패:', error.message);
        console.error('상세 오류:', error.response?.data || error);
        
        const status = error.response ? error.response.status : 500;
        const message = error.response ? error.response.data : { error: '내부 서버 오류' };
        res.status(status).json(message);
    }
});

// 서버 시작
app.listen(port, () => {
    console.log(`통합 서버가 http://localhost:${port}에서 실행 중입니다.`);
    console.log(`Gemini API 키 설정 여부: ${GEMINI_API_KEY ? 'O' : 'X'}`);
});