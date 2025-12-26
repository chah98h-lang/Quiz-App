---
description: GitHub Pages에 퀴즈 앱 배포하기
---

# 퀴즈 앱 배포 워크플로우

이 가이드는 AZ-900 퀴즈 앱을 GitHub Pages에 배포하는 방법을 설명합니다.

## 배포 방법

### 1. 변경사항 확인
먼저 현재 변경된 파일들을 확인합니다:
```bash
git status
```

### 2. 변경사항 스테이징
모든 변경사항을 스테이징 영역에 추가합니다:
// turbo
```bash
git add .
```

### 3. 커밋 생성
의미있는 커밋 메시지와 함께 변경사항을 커밋합니다:
```bash
git commit -m "설명적인 커밋 메시지"
```

**커밋 메시지 예시:**
- `"Update quiz data"` - 퀴즈 데이터 업데이트
- `"Fix option selection logic"` - 옵션 선택 로직 수정
- `"Improve mobile responsiveness"` - 모바일 반응형 개선
- `"Add new questions"` - 새로운 문제 추가

### 4. GitHub에 푸시
변경사항을 GitHub 저장소에 푸시합니다:
```bash
git push origin main
```

### 5. 배포 확인
GitHub Pages는 자동으로 배포됩니다. 약 1-2분 후 다음 URL에서 확인할 수 있습니다:
- **배포 URL**: https://chah98h-lang.github.io/Quiz-App/

## 배포 상태 확인

GitHub 웹사이트에서 배포 상태를 확인하려면:
1. https://github.com/chah98h-lang/Quiz-App 방문
2. 상단의 "Actions" 탭 클릭
3. 최근 워크플로우 실행 상태 확인

## 주요 파일 설명

- **index.html**: 메인 HTML 파일
- **app.js**: 퀴즈 로직을 담당하는 JavaScript 파일
- **style.css**: 스타일시트
- **data/quiz_data.json**: 퀴즈 문제 데이터
- **.nojekyll**: GitHub Pages가 Jekyll 빌드를 건너뛰도록 하는 파일

## 문제 해결

### 배포가 반영되지 않을 때
1. 브라우저 캐시 삭제 (Ctrl + Shift + R)
2. GitHub Actions에서 배포 상태 확인
3. 몇 분 후 다시 시도

### 저장소 URL 변경 안내
저장소가 이동되었습니다:
- 이전: `https://github.com/chah98h-lang/quiz-app.git`
- 현재: `https://github.com/chah98h-lang/Quiz-App.git`

Git이 자동으로 리다이렉트하지만, 필요시 원격 저장소 URL을 업데이트할 수 있습니다:
```bash
git remote set-url origin https://github.com/chah98h-lang/Quiz-App.git
```

## 빠른 배포 (한 줄 명령어)

모든 변경사항을 빠르게 배포하려면:
```bash
git add . && git commit -m "Update" && git push origin main
```

## 참고사항

- GitHub Pages는 `main` 브랜치의 루트 디렉토리에서 자동으로 배포됩니다
- 정적 파일(HTML, CSS, JS)만 배포되며, Node.js 서버는 로컬 개발용입니다
- 배포 후 변경사항이 반영되는 데 1-2분 정도 소요될 수 있습니다
