# 이미지 기반 문제 추가 가이드

## 📋 개요
DRAG DROP, Hot Area, Hotspot 등 이미지가 포함된 문제를 퀴즈 앱에 추가하는 방법을 설명합니다.

---

## 🔧 필요한 도구 설치

### 1. PyMuPDF 설치 (이미지 추출용)
```bash
pip install PyMuPDF
```

---

## 📝 작업 순서

### Step 1: PDF에서 이미지 추출

#### 방법 A: 자동 추출 스크립트 사용 (추천)
```bash
python extract_images.py
```

스크립트 실행 시 선택:
- **옵션 1**: 모든 이미지 추출
- **옵션 2**: DRAG DROP, Hot Area, Hotspot 문제만 추출 ✅ 추천

추출된 이미지는 `images/` 폴더에 저장됩니다.

#### 방법 B: 수동 추출
1. PDF를 Adobe Acrobat이나 다른 PDF 리더로 열기
2. 문제 이미지를 직접 캡처하거나 추출
3. `images/` 폴더에 저장 (예: `q42_dragdrop.png`)

---

### Step 2: 이미지 파일 정리

추출된 이미지를 문제별로 정리:

```
quiz-app/
  ├── images/
  │   ├── q42_dragdrop.png        # 문제 42번 Drag Drop
  │   ├── q87_hotarea.png         # 문제 87번 Hot Area
  │   ├── q123_hotspot.png        # 문제 123번 Hotspot
  │   └── ...
  └── ...
```

**파일명 규칙:**
- `q[문제번호]_[유형].png`
- 예: `q42_dragdrop.png`, `q87_hotarea.png`

---

### Step 3: quiz_data.json 업데이트

#### 기본 구조
```json
{
  "id": 42,
  "original_number": "45",
  "question": "You need to configure Azure resources...",
  "questionType": "DRAG_DROP",
  "image": "images/q42_dragdrop.png",
  "options": [
    {
      "letter": "A",
      "text": "Option A"
    },
    {
      "letter": "B",
      "text": "Option B"
    }
  ],
  "answer": "A",
  "explanation": "Detailed explanation here..."
}
```

#### 필수 필드 설명

| 필드 | 설명 | 예시 |
|------|------|------|
| `questionType` | 문제 유형 | `"DRAG_DROP"`, `"HOT_AREA"`, `"HOTSPOT"` |
| `image` | 이미지 경로 (선택) | `"images/q42_dragdrop.png"` |
| `imageDescription` | 이미지 설명 (선택) | `"Network topology diagram"` |

---

### Step 4: 문제 유형별 예시

#### 1. DRAG DROP 문제

```json
{
  "id": 42,
  "original_number": "45",
  "questionType": "DRAG_DROP",
  "question": "You have an Azure subscription. You need to match each service to its correct category. Drag the services to the correct categories.",
  "image": "images/q42_dragdrop.png",
  "imageDescription": "Azure services categorization diagram",
  "options": [
    {
      "letter": "A",
      "text": "Azure Virtual Machines → Compute"
    },
    {
      "letter": "B",
      "text": "Azure SQL Database → Storage"
    },
    {
      "letter": "C",
      "text": "Azure Cosmos DB → Database"
    },
    {
      "letter": "D",
      "text": "Azure Functions → Compute"
    }
  ],
  "answer": "A,C,D",
  "explanation": "Azure Virtual Machines and Azure Functions are compute services. Azure Cosmos DB is a database service."
}
```

#### 2. Hot Area 문제

```json
{
  "id": 87,
  "original_number": "92",
  "questionType": "HOT_AREA",
  "question": "You need to identify the region where the resource group is located. Select the correct area in the image.",
  "image": "images/q87_hotarea.png",
  "imageDescription": "Azure Portal screenshot showing resource group details",
  "options": [
    {
      "letter": "A",
      "text": "Location field in Overview section"
    },
    {
      "letter": "B",
      "text": "Region dropdown in Settings"
    },
    {
      "letter": "C",
      "text": "Deployment details tab"
    }
  ],
  "answer": "A",
  "explanation": "The Location field in the Overview section shows the region of the resource group."
}
```

#### 3. Hotspot 문제

```json
{
  "id": 123,
  "original_number": "130",
  "questionType": "HOTSPOT",
  "question": "You are reviewing a network diagram. For each statement, select Yes if the statement is true, otherwise select No.",
  "image": "images/q123_hotspot.png",
  "imageDescription": "Azure network architecture diagram",
  "options": [
    {
      "letter": "A",
      "text": "Statement 1: The virtual network allows communication between subnets - YES"
    },
    {
      "letter": "B",
      "text": "Statement 2: NSG blocks all outbound traffic - NO"
    },
    {
      "letter": "C",
      "text": "Statement 3: VPN Gateway connects to on-premises - YES"
    }
  ],
  "answer": "A,C",
  "explanation": "Virtual networks allow inter-subnet communication by default. NSGs have default rules allowing outbound traffic. VPN Gateway is used for hybrid connectivity."
}
```

---

## 🎨 이미지 최적화 팁

### 권장 이미지 사양
- **포맷**: PNG (투명 배경 지원) 또는 JPG
- **최대 너비**: 1200px
- **파일 크기**: 500KB 이하 (로딩 속도를 위해)
- **DPI**: 72-96 DPI (웹 표준)

### 이미지 최적화 도구
- **온라인**: [TinyPNG](https://tinypng.com/), [Squoosh](https://squoosh.app/)
- **CLI**: 
  ```bash
  # ImageMagick 사용
  magick convert input.png -resize 1200x -quality 85 output.png
  ```

---

## 🔍 이미지 추출 자동화 스크립트 상세

### extract_images.py 사용법

#### 1. 전체 실행
```bash
python extract_images.py
```

#### 2. 커스텀 실행
```python
from extract_images import extract_images_by_keyword

# 특정 키워드로 이미지 추출
extract_images_by_keyword(
    pdf_path="AZ-900 영문 474.pdf",
    keywords=["DRAG DROP", "Hot Area", "Hotspot"],
    output_folder="images"
)
```

---

## ✅ 체크리스트

완료된 항목을 체크하세요:

- [ ] PyMuPDF 설치 완료
- [ ] `extract_images.py` 실행으로 이미지 추출
- [ ] 이미지 파일 정리 및 파일명 규칙 적용
- [ ] `quiz_data.json`에 이미지 경로 추가
- [ ] `questionType` 필드 추가
- [ ] 브라우저에서 이미지 표시 확인
- [ ] 이미지 파일 크기 최적화

---

## 🐛 문제 해결

### 이미지가 표시되지 않을 때

1. **경로 확인**
   - 이미지 경로가 `images/` 폴더를 기준으로 올바른지 확인
   - 예: `"image": "images/q42.png"`

2. **파일 존재 확인**
   ```bash
   ls images/q42.png
   ```

3. **브라우저 콘솔 확인**
   - F12 → Console 탭에서 404 에러 확인

4. **서버 재시작**
   ```bash
   # 서버 중지 (Ctrl+C)
   # 서버 재시작
   npx http-server "C:\Users\PC\Desktop\quiz-app" -p 8080 -c-1
   ```

### 이미지가 너무 클 때

```python
# resize_images.py 생성
from PIL import Image
import os

def resize_images(folder="images", max_width=1200):
    for filename in os.listdir(folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(folder, filename)
            img = Image.open(filepath)
            
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)
                img.save(filepath, optimize=True, quality=85)
                print(f"Resized: {filename}")

if __name__ == "__main__":
    resize_images()
```

---

## 📚 참고 자료

- [PyMuPDF 문서](https://pymupdf.readthedocs.io/)
- [JSON 구조 예시](quiz_data.json)
- [CSS 스타일](style.css) - `.question-image` 클래스

---

## 💡 추가 기능 제안

향후 구현 가능한 기능:
- [ ] 이미지 확대/축소 (Zoom)
- [ ] 이미지 클릭 시 전체화면 모드
- [ ] 이미지 위에 핫스팟 영역 표시
- [ ] Drag & Drop 인터랙션 구현
- [ ] 이미지 로딩 스피너

---

**작성일**: 2025-12-15  
**버전**: 1.0  
**문의**: 이슈 발생 시 GitHub Issues 활용

