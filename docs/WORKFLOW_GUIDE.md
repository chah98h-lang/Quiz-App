# 🚀 이미지 문제 추가 워크플로우

## 빠른 시작 가이드

PDF에서 이미지 기반 문제를 추출하여 퀴즈 앱에 추가하는 전체 프로세스입니다.

---

## 📦 1단계: 환경 설정 (1회만 실행)

### Python 패키지 설치

```bash
cd "C:\Users\PC\Desktop\quiz-app"
pip install -r requirements.txt
```

설치되는 패키지:
- **PyMuPDF**: PDF에서 이미지 추출
- **Pillow**: 이미지 리사이징 및 최적화
- **jsonschema**: JSON 검증 (선택)

---

## 🔍 2단계: PDF에서 이미지 추출

### 방법 A: 자동 추출 (추천) ✅

```bash
python extract_images.py
```

실행 화면:
```
============================================================
AZ-900 PDF 이미지 추출 도구
============================================================

선택하세요:
1. 모든 이미지 추출
2. DRAG DROP, Hot Area, Hotspot 문제만 추출 (추천)

선택 (1 또는 2): 2
```

**옵션 2 선택 시**:
- "DRAG DROP", "Hot Area", "Hotspot" 키워드가 포함된 페이지만 검색
- 해당 페이지의 이미지만 추출
- 파일명에 문제 유형 자동 포함 (예: `q_page045_dragdrop_img01.png`)

### 방법 B: 수동 추출

1. PDF 뷰어(Adobe Acrobat)에서 PDF 열기
2. 이미지 부분 선택 → 우클릭 → "이미지로 복사"
3. 이미지 편집기(Paint, Photoshop)에 붙여넣기
4. `images/` 폴더에 저장

---

## 🎨 3단계: 이미지 최적화

추출된 이미지가 너무 크거나 용량이 클 경우:

```bash
python resize_images.py
```

실행 화면:
```
이미지 최적화 도구
1. 이미지 리사이징 및 최적화
2. 썸네일 생성
3. 둘 다 실행

선택 (1-3): 1
```

최적화 효과:
- 최대 너비 1200px로 조정
- 파일 크기 50-80% 감소
- 웹 로딩 속도 향상

---

## 📝 4단계: quiz_data.json 업데이트

### 4-1. 이미지 파일명 정리

추출된 이미지를 확인하고 의미 있는 이름으로 변경:

```bash
# 변경 전
q_page045_dragdrop_img01.png

# 변경 후
q42_dragdrop_vm_categories.png
```

### 4-2. JSON에 문제 추가

`quiz_data.json` 파일을 열고 다음 형식으로 문제 추가:

```json
{
  "id": 42,
  "original_number": "45",
  "questionType": "DRAG_DROP",
  "question": "You need to categorize Azure services. Drag each service to its correct category.",
  "image": "images/q42_dragdrop_vm_categories.png",
  "imageDescription": "Diagram showing Azure services and empty category boxes",
  "options": [
    {
      "letter": "A",
      "text": "Azure Virtual Machines → Compute"
    },
    {
      "letter": "B",
      "text": "Azure Blob Storage → Storage"
    },
    {
      "letter": "C",
      "text": "Azure SQL Database → Database"
    }
  ],
  "answer": "A,B,C",
  "explanation": "All three services are correctly categorized..."
}
```

### 필수 필드

| 필드 | 필수 | 설명 | 예시 |
|------|------|------|------|
| `id` | ✅ | 고유 문제 ID | `42` |
| `questionType` | ✅ | 문제 유형 | `"DRAG_DROP"`, `"HOT_AREA"`, `"HOTSPOT"` |
| `question` | ✅ | 문제 텍스트 | `"You need to..."` |
| `image` | ⭕ | 이미지 경로 | `"images/q42.png"` |
| `imageDescription` | ⭕ | 이미지 설명 (접근성) | `"Network diagram"` |
| `options` | ✅ | 선택지 배열 | `[{letter: "A", text: "..."}]` |
| `answer` | ✅ | 정답 | `"A"` 또는 `"A,B,C"` |
| `explanation` | ✅ | 해설 | `"The correct answer is..."` |

---

## ✅ 5단계: 테스트

### 5-1. 서버 재시작

현재 실행 중인 서버 종료:
```bash
# 터미널에서 Ctrl+C
```

서버 재시작:
```bash
npx http-server "C:\Users\PC\Desktop\quiz-app" -p 8080 -c-1
```

### 5-2. 브라우저에서 확인

1. 브라우저에서 http://127.0.0.1:8080 접속
2. 이미지가 포함된 문제로 이동
3. 확인 사항:
   - ✅ 이미지가 제대로 표시되는가?
   - ✅ 이미지 클릭 시 확대되는가?
   - ✅ 선택지가 정상적으로 작동하는가?
   - ✅ 정답 확인이 제대로 되는가?

### 5-3. 개발자 도구로 디버깅

문제 발생 시 F12 → Console 탭 확인:

**일반적인 오류:**

1. **404 오류 (이미지를 찾을 수 없음)**
   ```
   GET http://127.0.0.1:8080/images/q42.png 404 (Not Found)
   ```
   → 이미지 경로 확인 또는 파일 존재 여부 확인

2. **CORS 오류**
   ```
   Access to image blocked by CORS policy
   ```
   → 서버 재시작 필요

3. **JSON 파싱 오류**
   ```
   SyntaxError: Unexpected token...
   ```
   → JSON 문법 오류 (콤마, 괄호 확인)

---

## 📊 6단계: 문제 통계 업데이트

`quiz_data.json` 상단의 메타데이터 업데이트:

```json
{
  "title": "AZ-900 Azure Fundamentals",
  "description": "Microsoft Azure Fundamentals - 250 Questions (텍스트 203 + 이미지 47)",
  "totalQuestions": 250,
  "imageQuestions": 47,
  "textQuestions": 203,
  "questions": [...]
}
```

---

## 🔄 반복 워크플로우

새로운 이미지 문제 추가 시:

```
1. extract_images.py 실행 → 새 이미지 추출
                          ↓
2. resize_images.py 실행 → 이미지 최적화
                          ↓
3. 이미지 파일명 정리 → 의미 있는 이름으로 변경
                          ↓
4. quiz_data.json 수정 → 새 문제 추가
                          ↓
5. 서버 재시작 (Ctrl+C → npx http-server...)
                          ↓
6. 브라우저 테스트 → F5로 새로고침
                          ↓
7. 문제 확인 ✅
```

---

## 🎯 베스트 프랙티스

### 1. 파일명 규칙

```
q[문제ID]_[유형]_[간단한설명].png

예시:
✅ q42_dragdrop_vm_categories.png
✅ q87_hotarea_portal_subscription.png
✅ q123_hotspot_nsg_rules.png

❌ image1.png
❌ screenshot_20250115.png
```

### 2. 이미지 품질

- **해상도**: 충분히 선명하지만 너무 크지 않게 (1200px 이하)
- **포맷**: PNG (투명 배경/스크린샷) 또는 JPG (사진/복잡한 이미지)
- **크기**: 500KB 이하 권장

### 3. JSON 구조

- **일관성**: 모든 문제에 동일한 필드 구조 사용
- **설명**: `imageDescription` 필드로 접근성 향상
- **검증**: JSON 리터 도구로 문법 오류 체크

### 4. 문제 유형 분류

```json
"questionType": "DRAG_DROP"    // 드래그 앤 드롭
"questionType": "HOT_AREA"     // 핫 에어리어 (영역 선택)
"questionType": "HOTSPOT"      // 핫스팟 (Yes/No 선택)
"questionType": "IMAGE"        // 일반 이미지 포함 문제
```

---

## 🛠 도구 및 리소스

### 추천 도구

1. **이미지 편집**: Paint.NET, GIMP, Photoshop
2. **JSON 편집**: VS Code (JSON 검증 기능 내장)
3. **이미지 최적화**: TinyPNG, Squoosh
4. **PDF 뷰어**: Adobe Acrobat Reader

### 온라인 도구

- **JSON Validator**: https://jsonlint.com/
- **Image Optimizer**: https://tinypng.com/
- **Image Compressor**: https://squoosh.app/

---

## 📈 진행 상황 추적

### 체크리스트

```
이미지 문제 추가 진행 상황
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Python 환경 설정 완료
□ PDF에서 이미지 추출 (___개)
□ 이미지 최적화 및 정리
□ JSON에 문제 추가 (___/___개)
□ 서버 테스트 완료
□ 브라우저 확인 완료
□ 최종 배포 준비

현재 진행률: ____%
```

---

## 🐛 트러블슈팅

### 문제: 이미지가 표시되지 않음

**원인 1**: 경로 오류
```json
// ❌ 잘못된 경로
"image": "/images/q42.png"
"image": "C:\\Users\\..\\images\\q42.png"

// ✅ 올바른 경로
"image": "images/q42.png"
```

**원인 2**: 파일이 없음
```bash
# 파일 존재 확인
ls images/q42.png
```

**원인 3**: 서버 캐시
```bash
# 서버 재시작 및 브라우저 강제 새로고침 (Ctrl+Shift+R)
```

### 문제: 이미지가 너무 큼

```bash
python resize_images.py
# 또는
python -c "from resize_images import resize_and_optimize_images; resize_and_optimize_images(max_width=1200, quality=80)"
```

### 문제: JSON 파싱 오류

**일반적인 실수:**
```json
// ❌ 마지막 콤마
{
  "id": 42,
  "question": "...",
}

// ❌ 따옴표 누락
{
  id: 42,
  question: "..."
}

// ✅ 올바른 형식
{
  "id": 42,
  "question": "..."
}
```

**JSON 검증:**
```bash
# Python으로 JSON 검증
python -m json.tool quiz_data.json
```

---

## 💡 고급 기능

### 1. 배치 처리

여러 이미지를 한 번에 처리:

```python
# batch_process.py
import os
from extract_images import extract_images_by_keyword
from resize_images import resize_and_optimize_images

# 1. 이미지 추출
extract_images_by_keyword("AZ-900 영문 474.pdf")

# 2. 이미지 최적화
resize_and_optimize_images(max_width=1200, quality=85)

print("✅ 배치 처리 완료!")
```

### 2. 이미지 검증 스크립트

```python
# verify_images.py
import json
import os

with open('quiz_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

missing_images = []

for q in data['questions']:
    if 'image' in q and q['image']:
        if not os.path.exists(q['image']):
            missing_images.append({
                'id': q['id'],
                'image': q['image']
            })

if missing_images:
    print(f"❌ {len(missing_images)}개 이미지 누락:")
    for item in missing_images:
        print(f"  Q{item['id']}: {item['image']}")
else:
    print("✅ 모든 이미지 파일 존재 확인!")
```

---

## 📚 참고 문서

- [IMAGE_GUIDE.md](IMAGE_GUIDE.md) - 상세 가이드
- [sample_image_questions.json](sample_image_questions.json) - 예시 파일
- [extract_images.py](extract_images.py) - 이미지 추출 스크립트
- [resize_images.py](resize_images.py) - 이미지 최적화 스크립트

---

**작성일**: 2025-12-15  
**버전**: 1.0  
**업데이트**: 문제 발생 시 GitHub Issues 활용

