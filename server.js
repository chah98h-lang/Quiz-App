const express = require('express');
const path = require('path');
const app = express();
const port = process.env.PORT || 3000;

// 정적 파일 서빙 (현재 디렉토리)
app.use(express.static(path.join(__dirname, '.')));

// 기본 라우트
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// 서버 시작
app.listen(port, () => {
    console.log(`Quiz app server listening at http://localhost:${port}`);
    console.log(`Working directory: ${__dirname}`);
});
