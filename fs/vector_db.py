"""
neuro-casio-os/fs/vector_db.py

The Semantic File System (Vector Space).
----------------------------------------
Implements a "No-Inode" file system where files are addressed by
high-dimensional vectors derived from their content or metadata.

Research Note:
This is a pure Python implementation of a Vector Database.
In a production Unikernel, this would use SIMD instructions via the HAL.
"""

import json
import math
import struct
import os
from typing import List, Dict, Tuple, Optional

class VectorDB:
    def __init__(self, db_path="fs/vfs.bin"):
        self.db_path = db_path
        self.vectors: List[Dict] = []
        self._load_db()

    def _load_db(self):
        """Loads the vector store from disk."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    self.vectors = json.load(f)
            except:
                self.vectors = []

    def _save_db(self):
        """Persists the vector store to disk."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w") as f:
            json.dump(self.vectors, f)

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generates a real embedding vector using Ollama (nomic-embed-text).
        """
        url = "http://127.0.0.1:11434/api/embeddings"
        payload = {
            "model": "nomic-embed-text",
            "prompt": text
        }
        
        try:
            import urllib.request
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("embedding", [])
        except Exception as e:
            print(f"[VFS] Embedding Error: {e}")
            # Fallback to mock if offline
            return self._mock_embedding(text)

    def _mock_embedding(self, text: str) -> List[float]:
        """Fallback deterministic embedding"""
        vector = [0.0] * 768 # nomic-embed-text is 768d
        for i, char in enumerate(text):
            idx = (ord(char) + i) % 768
            vector[idx] += 1.0
        magnitude = math.sqrt(sum(x*x for x in vector))
        return [x / magnitude for x in vector] if magnitude > 0 else vector

    def save_file(self, content: str, metadata: Dict):
        """
        Saves a file by generating its embedding and storing it.
        """
        vector = self._get_embedding(content)
        entry = {
            "id": len(self.vectors),
            "vector": vector,
            "content": content,
            "metadata": metadata
        }
        self.vectors.append(entry)
        self._save_db()
        print(f"[VFS] Saved file with ID {entry['id']}")

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calculates the cosine similarity between two vectors.
        Formula: (A . B) / (||A|| * ||B||)
        """
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(a * a for a in vec_a))
        mag_b = math.sqrt(sum(b * b for b in vec_b))
        
        if mag_a == 0 or mag_b == 0:
            return 0.0
            
        return dot_product / (mag_a * mag_b)

    def find_nearest(self, query: str, top_k=1) -> List[Tuple[Dict, float]]:
        """
        Finds the nearest files to the query string.
        """
        query_vec = self._get_embedding(query)
        results = []
        
        for entry in self.vectors:
            score = self.cosine_similarity(query_vec, entry["vector"])
            results.append((entry, score))
            
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

# Test block
if __name__ == "__main__":
    vfs = VectorDB("test_vfs.json")
    vfs.save_file("Meeting notes: Discuss Q3 budget", {"type": "text"})
    vfs.save_file("Grocery list: Milk, Eggs, Bread", {"type": "list"})
    
    print("Query: 'budget'")
    results = vfs.find_nearest("budget")
    for res, score in results:
        print(f"Match: {res['content']} (Score: {score:.4f})")
