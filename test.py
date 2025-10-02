# --- 0. 라이브러리 임포트 ---
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader
from torch.optim import AdamW
from tqdm import tqdm
import torch
import os

# --- 1. 데이터 준비 ---
print("--- 1. 데이터 준비 시작 ---")

# 각 파일 경로를 직접 한 줄로 지정
HUMAN_FILE = 'human_datasets/processed_human.json'
AI_FILE = 'ai_datasets/processed_gpt.json'

# 각 JSON 파일 불러오기
try:
    with open(HUMAN_FILE, 'r', encoding='utf-8') as f:
        human_texts = json.load(f)
    with open(AI_FILE, 'r', encoding='utf-8') as f:
        ai_texts = json.load(f)
except FileNotFoundError as e:
    print(f"오류: 데이터 파일({e.filename})을 찾을 수 없습니다.")
    print("스크립트와 같은 폴더에 human_datasets와 ai_datasets 폴더 및 파일들이 있는지 확인하세요.")
    exit()

# 데이터 리스트 생성 (텍스트와 라벨을 딕셔너리로 묶어줌)
data = []
for text in human_texts:
    data.append({'text': text, 'label': 0}) # 사람은 라벨 0
for text in ai_texts:
    data.append({'text': text, 'label': 1}) # AI는 라벨 1

# 데이터프레임으로 변환 후 무작위로 섞기
df = pd.DataFrame(data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print("데이터 준비 완료")
print(f"총 데이터 개수: {len(df)}")
print(f"사람 데이터 개수: {len(human_texts)}")
print(f"AI 데이터 개수: {len(ai_texts)}")

# 훈련/테스트셋 분리
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df['label']
)

# --- 2. 모델 및 토크나이저 로딩 ---
print("\n--- 2. 모델 및 토크나이저 로딩 시작 ---")
MODEL_NAME = "skt/kobert-base-v1"
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
print("모델 및 토크나이저 로딩 완료")

# --- 3. 커스텀 데이터셋 클래스 정의 ---
class KoBERTDataset(torch.utils.data.Dataset):
    def __init__(self, dataframe, tokenizer, max_len):
        self.tokenizer = tokenizer
        self.text = dataframe.text.values
        self.labels = dataframe.label.values
        self.max_len = max_len

    def __len__(self):
        return len(self.text)

    def __getitem__(self, index):
        text = str(self.text[index])
        label = self.labels[index]
        encoding = self.tokenizer.encode_plus(
            text, add_special_tokens=True, max_length=self.max_len,
            return_token_type_ids=False, padding='max_length',
            truncation=True, return_attention_mask=True, return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# --- 4. 설정값 정의 ---
MAX_LEN = 256
BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 2e-5
SAVE_PATH = "./kobert_ai_human_classifier.pth"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# --- 5. 모델 학습 또는 불러오기 ---
if os.path.exists(SAVE_PATH):
    print(f"\n--- 저장된 모델({SAVE_PATH})을 불러옵니다 ---")
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    print("모델 로딩 완료")
else:
    print("\n--- 저장된 모델이 없어 새로 학습을 시작합니다 ---")
    train_dataset = KoBERTDataset(train_df, tokenizer, MAX_LEN)
    train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

    # 6. 모델 학습
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        for batch in tqdm(train_dataloader, desc=f"Epoch {epoch + 1}/{EPOCHS}"):
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            total_loss += loss.item()
            loss.backward()
            optimizer.step()
        avg_train_loss = total_loss / len(train_dataloader)
        print(f"Epoch {epoch + 1} | Training Loss: {avg_train_loss:.4f}")

    # 7. 모델 평가
    test_dataset = KoBERTDataset(test_df, tokenizer, MAX_LEN)
    test_dataloader = DataLoader(test_dataset, batch_size=BATCH_SIZE)
    model.eval()
    total_eval_accuracy = 0
    for batch in tqdm(test_dataloader, desc="Evaluating"):
        with torch.no_grad():
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            predictions = torch.argmax(logits, dim=-1)
            total_eval_accuracy += (predictions == labels).sum().item()
    accuracy = total_eval_accuracy / len(test_df)
    print(f"Accuracy: {accuracy:.4f}")

    # 8. 학습된 모델 저장
    torch.save(model.state_dict(), SAVE_PATH)
    print(f"모델 학습 및 평가 완료. 모델이 {SAVE_PATH}에 저장되었습니다.")

# --- 9. 예측 함수 정의 ---
def predict(text):
    model.eval()
    encoding = tokenizer.encode_plus(
        text, add_special_tokens=True, max_length=MAX_LEN, return_token_type_ids=False,
        padding='max_length', truncation=True, return_attention_mask=True, return_tensors='pt'
    )
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
    probs = torch.nn.functional.softmax(logits, dim=-1)
    human_prob = probs[0][0].item()
    ai_prob = probs[0][1].item()
    prediction = "사람이 작성한 글" if human_prob > ai_prob else "AI가 작성한 글"
    
    print(f"\n입력 텍스트: \"{text}\"")
    print("-" * 50)
    print(f"🤖 AI일 확률: {ai_prob*100:.2f}%")
    print(f"🧑‍💻 사람일 확률: {human_prob*100:.2f}%")
    print(f"==> 최종 판별: {prediction}")
    print("-" * 50)

# --- 10. 사용자 입력으로 실시간 예측 ---
print("\n--- 실시간 예측을 시작합니다 ---")
while True:
    user_input = input("\n판별할 문장을 입력하세요 (종료하시려면 '종료' 또는 'exit' 입력): ")
    if user_input.lower() in ['종료', 'exit']:
        print("프로그램을 종료합니다.")
        break
    predict(user_input)