import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

HISTORY_PATH = os.path.join(os.path.dirname(__file__), "seed_data", "mock_slack_history.json")
EMBEDDING_MODEL = "gemini-embedding-001"

class RTSIndex:
    def __init__(self, history_path: str = HISTORY_PATH):
        with open(history_path, "r", encoding="utf-8") as f:
            self.messages = json.load(f)
        self.corpus = [m["text"] for m in self.messages]
        self.backend = "tfidf"
        self._embeddings = None

        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                self._build_embedding_index(api_key)
                self.backend = "embeddings"
            except Exception as e:
                pass

        if self.backend == "tfidf":
            self.vectorizer = TfidfVectorizer(stop_words="english")
            self.matrix = self.vectorizer.fit_transform(self.corpus)

    def _build_embedding_index(self, api_key: str):
        from google import genai
        import numpy as np
        client = genai.Client(api_key=api_key)
        response = client.models.embed_content(model=EMBEDDING_MODEL, contents=self.corpus)
        self._embeddings = np.array([e.values for e in response.embeddings])
        self._client = client

    def _embed_query(self, query: str):
        import numpy as np
        response = self._client.models.embed_content(model=EMBEDDING_MODEL, contents=[query])
        return np.array(response.embeddings[0].values).reshape(1, -1)

    def search(self, query: str, top_k: int = 5, min_score: float = 0.05) -> list[dict]:
        if self.backend == "embeddings":
            q_vec = self._embed_query(query)
            scores = cosine_similarity(q_vec, self._embeddings).flatten()
        else:
            q_vec = self.vectorizer.transform([query])
            scores = cosine_similarity(q_vec, self.matrix).flatten()

        ranked = sorted(((score, i) for i, score in enumerate(scores) if score >= min_score), reverse=True)[:top_k]
        return [{**self.messages[i], "score": round(float(score), 3), "backend": self.backend} for score, i in ranked]

    def search_multi(self, queries: list[str], top_k_each: int = 3) -> list[dict]:
        seen = {}
        for q in queries:
            for hit in self.search(q, top_k=top_k_each):
                key = (hit["channel"], hit["timestamp"], hit["text"])
                if key not in seen or hit["score"] > seen[key]["score"]:
                    seen[key] = hit
        return sorted(seen.values(), key=lambda h: -h["score"])
