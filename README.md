# findmycloset

"실행 전 GROQ_API_KEY 환경변수 설정 필요"
# 👗 Find Closet — LoRA 기반 개인 옷장 코디 추천 시스템

## 프로젝트 소개
사용자가 보유한 옷 사진을 업로드하면, LoRA 파인튜닝된 CLIP 모델과 LLM이 협력하여
자연어 입력("결혼식 하객룩 추천해줘")에 맞는 최적의 코디 조합을 추천해주는 서비스입니다.

## 팀원
| 이름 | 역할 |
|------|------|
| 정다영 | Backend / AI (CLIP, LLM, FAISS, Streamlit) |
| 유혜빈 | Frontend / Data (데이터 수집, LoRA 학습, FAISS 인덱싱) |

## 시스템 아키텍처
자연어 입력 → Groq LLM(키워드 추출) → CLIP 텍스트 임베딩
→ FAISS 유사도 검색 → 상의/하의 조합 → Streamlit 시각화

## 개발 환경
- Python 3.12
- Google Colab (T4 GPU)

## 설치 및 실행
```bash
pip install -r requirements.txt
```

실행 전 환경변수 설정:
```bash
export GROQ_API_KEY="your_groq_api_key"
```

Streamlit 실행:
```bash
streamlit run app.py
```

## 모델 가중치 & 데이터
- LoRA 가중치: [Google Drive 링크](https://drive.google.com/drive/folders/1j2l14qFLW-URCiv36BvqfC9OJwWaAdg2)
- FAISS 인덱스: [Google Drive 링크](https://drive.google.com/drive/u/0/folders/1F8ye8dDVlqAt9jr5s-RrnDpzijb85cnH)

## 기술 스택
| 분류 | 기술 |
|------|------|
| Embedding 모델 | CLIP-ViT-Base-Patch32 + LoRA (rank=8, alpha=16) |
| LLM | LLaMA-3.3-70B (Groq API) |
| 벡터 DB | FAISS |
| Frontend | Streamlit |
| 학습 프레임워크 | PyTorch, HuggingFace PEFT |
