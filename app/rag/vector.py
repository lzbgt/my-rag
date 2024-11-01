from pinecone import Pinecone, ServerlessSpec
import os
from sentence_transformers import SentenceTransformer
from app.config import PINECONE_TOKEN
import requests
from typing import List, Any

from pydantic import BaseModel


class VEntity(BaseModel):
    id: str
    q: str  # what to embeded
    a: str


class VStorage:
    def __init__(self, index: str = "solo") -> None:
        self.token = PINECONE_TOKEN
        self.index_name = index

    def connect(self):
        self.pc = Pinecone(api_key=self.token)

        # Check if the index already exists
        if self.index_name not in self.pc.list_indexes().names():
            # Create the index with a vector dimension (e.g., 384 for all-MiniLM-L6-v2)
            self.pc.create_index(self.index_name, dimension=384,
                                 metric="cosine",
                                 spec=ServerlessSpec(
                                     cloud="aws",
                                     region="us-east-1"
                                 ))
        self.index = self.pc.Index(self.index_name)

    def save(self, model,  ns: str, data: List[VEntity]):
        sentences = [x["q"] for x in data]
        embeddings = model.encode(sentences)

        vectors = []
        for d, e in zip(data, embeddings):
            vectors.append({
                "id": d["id"],
                "values": e,
                "metadata": {'a': d["a"]}
            })

        self.index.upsert(
            vectors=vectors,
            namespace=ns
        )

    def query(self, model, ns: str, query: str, score=0.9):
        query_embedding = model.encode(query).tolist()
        print(query_embedding)

        results = self.index.query(
            namespace=ns,
            vector=query_embedding,
            top_k=1,
            include_values=False,
            include_metadata=True
        )

        if not results["matches"]:
            return None

        if results["matches"][0]["score"] < score:
            return None

        return results["matches"][0]["metadata"]["a"]


if __name__ == "__main__":
    test_data = [
        {"id": "1", "q": "What is the capital of France?",
            "a": "The capital of France is Paris."},
        {"id": "2", "q": "Explain the theory of relativity.",
            "a": "The theory of relativity refers to two interrelated theories by Albert Einstein: special relativity and general relativity."},
        {"id": "3", "q": "What is the process of photosynthesis?",
            "a": "Photosynthesis is the process by which green plants use sunlight to synthesize nutrients from carbon dioxide and water."},
        {"id": "4", "q": "What is Newton's first law?",
            "a": "Newton's first law states that an object will remain at rest or in uniform motion unless acted upon by a force."},
        {"id": "5", "q": "Define the Pythagorean theorem.",
            "a": "The Pythagorean theorem states that in a right-angled triangle, the square of the hypotenuse is equal to the sum of the squares of the other two sides."}]
    model = SentenceTransformer('all-MiniLM-L6-v2')
    index = VStorage()
    index.connect()
    # index.save(model, "test", test_data)
    # r = index.query(model, "test", "What is the capital of France?")
    r = index.query(model, "test", "why China called China")
    print(r)
