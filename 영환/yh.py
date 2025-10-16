# -*- coding: utf-8 -*-
import os
import io
import sys
import logging
import google.generativeai as genai

# ===== [1] 한글 깨짐 방지 =====
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# ===== [2] 로그 메시지 최소화 =====
logging.getLogger("absl").setLevel(logging.ERROR)
logging.getLogger("grpc").setLevel(logging.ERROR)

# ===== [3] API 키 설정 =====
# (1) 환경 변수에서 불러오기
api_key = os.environ.get("GOOGLE_API_KEY")

# (2) 환경 변수 없으면 직접 입력 가능
if not api_key:
    api_key = "AIzaSyCIPntPpsP4mJMutYp_UeGi6KfDNS9wizc" 

# ===== [4] Gemini 모델 설정 =====
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")  

# ===== [5] 사용자 입력 =====
topic = input("주제를 입력하세요: ")

# ===== [6] 5개 문장 생성 =====
results = []
for i in range(5):
    prompt = (
        f"'{topic}'에 대해 한 문장으로 요약해줘. "
        "반드시 100자 이내, 목록이나 개조식 없이 작성하고, "
        "문장마다 독립적이어야 합니다."
    )
    response = model.generate_content(prompt)
    # 100자 제한 후 공백 제거
    text = response.text.strip()[:100]
    results.append(text)

# ===== [7] 결과 출력 =====
print("\n=== 생성된 5개의 요약 문장 ===")
for idx, text in enumerate(results, 1):
    print(f"{idx}. {text}")
