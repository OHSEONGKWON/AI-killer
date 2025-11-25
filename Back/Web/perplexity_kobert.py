# -*- coding: utf-8 -*-
"""
KoGPT2 기반 텍스트 Perplexity 계산 모듈
"""
import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional

logging.getLogger("transformers").setLevel(logging.ERROR)

# 전역 변수로 모델 지연 로드
_perplexity_model = None
_perplexity_tokenizer = None
_device = None

def get_perplexity_model():
    """Perplexity 계산용 KoGPT2 모델을 로드합니다 (지연 로딩)"""
    global _perplexity_model, _perplexity_tokenizer, _device
    
    if _perplexity_model is None:
        try:
            model_id = 'skt/kogpt2-base-v2'
            _perplexity_model = AutoModelForCausalLM.from_pretrained(model_id)
            _perplexity_tokenizer = AutoTokenizer.from_pretrained(model_id)
            
            # 패딩 토큰 설정
            if _perplexity_tokenizer.pad_token is None:
                _perplexity_tokenizer.pad_token = _perplexity_tokenizer.eos_token
            
            # 장치 설정
            _device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
            _perplexity_model.to(_device)
            _perplexity_model.eval()
            
            logging.info(f"Perplexity 모델 로드 완료: {model_id} on {_device}")
        except Exception as e:
            logging.error(f"Perplexity 모델 로드 실패: {e}")
            raise RuntimeError("Perplexity 모델을 로드할 수 없습니다.")
    
    return _perplexity_model, _perplexity_tokenizer, _device


def calculate_perplexity(text: str) -> float:
    """
    입력 텍스트에 대한 Perplexity (혼란도) 값을 계산합니다.
    
    Args:
        text: 분석할 텍스트
    
    Returns:
        Perplexity 값 (낮을수록 자연스러운 텍스트)
    """
    if not text.strip():
        raise ValueError("입력 텍스트가 비어있습니다.")
    
    model, tokenizer, device = get_perplexity_model()
    
    # 텍스트 인코딩
    encodings = tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(device)
    input_ids = encodings.input_ids
    
    # 모델 설정
    max_length = model.config.n_positions if hasattr(model.config, 'n_positions') else 1024
    stride = 256
    seq_len = input_ids.size(1)
    
    total_nll = 0
    total_tokens = 0
    
    # 슬라이딩 윈도우 처리
    for i in range(0, seq_len, stride):
        begin_loc = max(i - max_length + stride, 0)
        end_loc = min(i + stride, seq_len)
        trg_len = end_loc - begin_loc
        
        input_ids_chunk = input_ids[:, begin_loc:end_loc]
        target_ids = input_ids_chunk.clone()
        target_ids[:, :-trg_len] = -100
        
        with torch.no_grad():
            outputs = model(input_ids_chunk, labels=target_ids)
            
            if hasattr(outputs, 'loss'):
                neg_log_likelihood = outputs.loss * trg_len
            else:
                raise ValueError("모델 출력에서 'loss'를 찾을 수 없습니다.")
        
        total_nll += neg_log_likelihood
        total_tokens += trg_len
    
    # Perplexity 계산
    ppl = torch.exp(total_nll / total_tokens)
    
    return round(ppl.item(), 2)
