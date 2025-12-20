"""
PDF 구조 확인 스크립트
"""

import fitz
import sys
import io

# UTF-8 출력
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf = fitz.open("AZ-900 영문 474.pdf")

print("=" * 60)
print("첫 5페이지 텍스트 샘플")
print("=" * 60)

for page_num in range(min(5, pdf.page_count)):
    page = pdf[page_num]
    text = page.get_text()
    
    print(f"\n페이지 {page_num + 1}")
    print("-" * 60)
    print(text[:1000])  # 처음 1000자만
    print("...")

pdf.close()

