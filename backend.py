import os
import torch
import faiss
import json
import numpy as np
from transformers import CLIPModel, CLIPProcessor
from groq import Groq

device = "cuda" if torch.cuda.is_available() else "cpu"
model_512 = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor_512 = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

index_top = faiss.read_index("/content/drive/MyDrive/공유드라이브/패션시멘틱검색/옷/faiss/top_db.index")
index_bottom = faiss.read_index("/content/drive/MyDrive/공유드라이브/패션시멘틱검색/옷/faiss/bottom_db.index")
index_dress = faiss.read_index("/content/drive/MyDrive/공유드라이브/패션시멘틱검색/옷/faiss/dress_db.index")

with open("/content/drive/MyDrive/공유드라이브/패션시멘틱검색/옷/faiss/top_paths.json") as f:
    top_paths = [p.replace("/content/drive/MyDrive/패션시멘틱검색",
                           "/content/drive/MyDrive/공유드라이브/패션시멘틱검색")
                 for p in json.load(f)]
with open("/content/drive/MyDrive/공유드라이브/패션시멘틱검색/옷/faiss/bottom_paths.json") as f:
    bottom_paths = [p.replace("/content/drive/MyDrive/패션시멘틱검색",
                              "/content/drive/MyDrive/공유드라이브/패션시멘틱검색")
                    for p in json.load(f)]
with open("/content/drive/MyDrive/공유드라이브/패션시멘틱검색/옷/faiss/dress_paths.json") as f:
    dress_paths = [p.replace("/content/drive/MyDrive/패션시멘틱검색",
                             "/content/drive/MyDrive/공유드라이브/패션시멘틱검색")
                   for p in json.load(f)]

def extract_fashion_keywords(query):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"""
너는 패션 전문가야. CLIP 검색용 영어 키워드 5~10개 추출해줘.
입력: "{query}"
출력: 영어 키워드만 콤마로 구분. 다른 말 하지 마.
"""}]
    )
    return [k.strip() for k in response.choices[0].message.content.strip().split(",")]

def get_text_embedding(query_text):
    inputs = processor_512(text=[query_text], return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        output = model_512.get_text_features(**inputs)
    embedding = output.pooler_output if hasattr(output, 'pooler_output') else output
    embedding = embedding / embedding.norm(dim=-1, keepdim=True)
    return embedding.cpu().numpy()

def search_category(query_text, index, paths, top_k=5):
    if index.ntotal == 0:
        return []
    top_k = min(top_k, index.ntotal)
    text_vec = get_text_embedding(query_text)
    scores, indices = index.search(text_vec, top_k)
    return [{"path": paths[idx], "score": float(score)} for score, idx in zip(scores[0], indices[0])]

def get_outfit_combinations(query, sel_top, sel_bottom, sel_dress):
    keywords = extract_fashion_keywords(query)
    text_query = ", ".join(keywords)
    result = {"keywords": keywords, "tops": [], "bottoms": [], "dresses": [], "combinations": []}
    if sel_top:
        result["tops"] = search_category(text_query, index_top, top_paths)
    if sel_bottom:
        result["bottoms"] = search_category(text_query, index_bottom, bottom_paths)
    if sel_dress:
        result["dresses"] = search_category(text_query, index_dress, dress_paths)
    for top in result["tops"]:
        for bottom in result["bottoms"]:
            result["combinations"].append({
                "top": top["path"],
                "bottom": bottom["path"],
                "score": (top["score"] + bottom["score"]) / 2
            })
    result["combinations"].sort(key=lambda x: -x["score"])
    result["combinations"] = result["combinations"][:3]
    return result
