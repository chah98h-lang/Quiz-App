# 📸 이미지 기반 문제 지원 기능 추가 완료!

## ✨ 새로운 기능

퀴즈 앱에 **이미지 기반 문제** 지원 기능이 추가되었습니다!

### 지원하는 문제 유형
- 🔀 **DRAG DROP**: 드래그 앤 드롭 문제
- 🎯 **Hot Area**: 핫 에어리어 (화면 영역 선택)
- 📍 **Hotspot**: 핫스팟 (Yes/No 선택)
- 🖼️ **일반 이미지**: 도표, 그래프 등이 포함된 문제

---

## 🚀 빠른 시작

### 1단계: Python 패키지 설치

```bash
cd "C:\Users\PC\Desktop\quiz-app"
pip install -r requirements.txt
```

### 2단계: PDF에서 이미지 추출

```bash
python extract_images.py
```

**옵션 2번 선택** (DRAG DROP, Hot Area, Hotspot 문제만 추출)

### 3단계: 이미지 최적화 (선택사항)

```bash
python resize_images.py
```

### 4단계: quiz_data.json에 문제 추가

```json
{
  "id": 42,
  "questionType": "DRAG_DROP",
  "question": "문제 내용...",
  "image": "images/q42_dragdrop.png",
  "options": [...],
  "answer": "A",
  "explanation": "설명..."
}
```

### 5단계: 확인

서버 재시작 후 브라우저에서 확인:
```bash
npx http-server "C:\Users\PC\Desktop\quiz-app" -p 8080 -c-1
```

---

## 📂 추가된 파일

```
quiz-app/
├── 📄 extract_images.py           # PDF 이미지 추출 스크립트
├── 📄 resize_images.py            # 이미지 최적화 스크립트
├── 📄 verify_setup.py             # 설정 검증 스크립트
├── 📄 requirements.txt            # Python 패키지 목록
├── 📘 IMAGE_GUIDE.md              # 상세 가이드 문서
├── 📘 WORKFLOW_GUIDE.md           # 워크플로우 가이드
├── 📘 README_IMAGE_SUPPORT.md     # 이 파일
├── 📋 sample_image_questions.json # 샘플 JSON
├── 📁 images/                     # 이미지 저장 폴더
└── ...기존 파일들
```

---

## ✅ 검증 실행

설정이 올바른지 확인:

```bash
python verify_setup.py
```

검증 항목:
- ✅ Python 패키지 설치 여부
- ✅ 필수 파일 존재 여부
- ✅ JSON 문법 오류 확인
- ✅ 이미지 파일 존재 확인
- ✅ 서버 실행 상태 확인

---

## 🎨 UI 개선 사항

### 1. 이미지 표시
- 문제에 이미지가 자동으로 표시됩니다
- 반응형 디자인으로 모바일에서도 최적화

### 2. 이미지 확대 기능
- 이미지 클릭 시 전체화면으로 확대
- ESC 키 또는 클릭으로 닫기

### 3. 오류 처리
- 이미지 로딩 실패 시 에러 메시지 표시
- 사용자 친화적인 안내

---

## 📖 상세 문서

### 필수 읽기
1. **[WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)**  
   → 전체 작업 프로세스 단계별 설명

2. **[IMAGE_GUIDE.md](IMAGE_GUIDE.md)**  
   → 이미지 추출 및 최적화 상세 가이드

### 참고 자료
- **[sample_image_questions.json](sample_image_questions.json)**  
  → 이미지 문제 JSON 구조 예시

---

## 🔧 도구 사용법

### extract_images.py
PDF에서 이미지 자동 추출

```bash
python extract_images.py
```

**특징:**
- 키워드 기반 필터링 (DRAG DROP, Hot Area, Hotspot)
- 자동 파일명 생성 (문제 유형 포함)
- 진행 상황 실시간 표시

### resize_images.py
이미지 크기 최적화

```bash
python resize_images.py
```

**기능:**
- 자동 리사이징 (최대 1200px)
- 파일 크기 압축 (50-80% 감소)
- 썸네일 생성 (선택사항)

### verify_setup.py
설정 및 파일 검증

```bash
python verify_setup.py
```

**검증 항목:**
- Python 패키지 설치
- 필수 파일 존재
- JSON 문법 오류
- 이미지 파일 확인
- 서버 실행 상태

---

## 💡 사용 예시

### 예시 1: DRAG DROP 문제

```json
{
  "id": 101,
  "questionType": "DRAG_DROP",
  "question": "Match Azure services to their categories.",
  "image": "images/q101_dragdrop_services.png",
  "options": [
    {"letter": "A", "text": "Azure VM → Compute"},
    {"letter": "B", "text": "Blob Storage → Storage"}
  ],
  "answer": "A,B",
  "explanation": "Both mappings are correct..."
}
```

### 예시 2: Hot Area 문제

```json
{
  "id": 102,
  "questionType": "HOT_AREA",
  "question": "Select the subscription ID in the portal.",
  "image": "images/q102_hotarea_portal.png",
  "options": [
    {"letter": "A", "text": "Overview section"},
    {"letter": "B", "text": "Properties section"}
  ],
  "answer": "A",
  "explanation": "Subscription ID is in Overview..."
}
```

---

## 🎯 작업 흐름

```
📄 PDF 파일
    ↓
🔍 extract_images.py 실행
    ↓
🖼️ 이미지 추출 (images/ 폴더)
    ↓
🎨 resize_images.py 실행 (선택)
    ↓
📝 quiz_data.json 업데이트
    ↓
🔄 서버 재시작
    ↓
🌐 브라우저 테스트
    ↓
✅ 완료!
```

---

## 🐛 문제 해결

### Q: 이미지가 표시되지 않아요
**A:** 다음을 확인하세요:
1. 이미지 경로가 `"images/파일명.png"` 형식인지
2. 파일이 실제로 존재하는지 (`ls images/`)
3. 서버를 재시작했는지
4. 브라우저 캐시 삭제 (Ctrl+Shift+R)

### Q: 이미지가 너무 커요
**A:** 최적화 스크립트 실행:
```bash
python resize_images.py
```

### Q: JSON 오류가 발생해요
**A:** JSON 검증:
```bash
python -m json.tool quiz_data.json
```

### Q: PyMuPDF 설치 오류
**A:** 관리자 권한으로 설치:
```bash
pip install --user PyMuPDF
```

---

## 📊 현재 상태

```
✅ 이미지 지원 기능 추가 완료
✅ UI 개선 완료 (이미지 표시 + 확대)
✅ 자동화 스크립트 3종 생성
✅ 상세 문서 작성 완료
✅ 샘플 파일 제공

🔄 진행 중
- PDF에서 이미지 추출 (사용자 작업)
- quiz_data.json 업데이트 (사용자 작업)
```

---

## 📞 지원

### 문서
- **전체 워크플로우**: [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)
- **상세 가이드**: [IMAGE_GUIDE.md](IMAGE_GUIDE.md)

### 검증
```bash
python verify_setup.py
```

### 서버 실행
```bash
npx http-server "C:\Users\PC\Desktop\quiz-app" -p 8080 -c-1
```

---

## 🎉 다음 단계

1. **Python 패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **이미지 추출**
   ```bash
   python extract_images.py
   ```

3. **설정 검증**
   ```bash
   python verify_setup.py
   ```

4. **문서 읽기**
   - WORKFLOW_GUIDE.md 정독
   - 단계별로 진행

5. **문제 추가**
   - quiz_data.json 수정
   - 서버 재시작
   - 브라우저 테스트

---

**작성일**: 2025-12-15  
**버전**: 1.0  
**작성자**: AI Assistant

**Happy Coding! 🚀**

