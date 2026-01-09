import os
import chromadb
import ollama
import uuid
from datetime import datetime

class VectorStore:
    DATA_DIR = os.path.expanduser("~/.local/share/aira/chroma_db")
    COLLECTION_NAME = "aira_knowledge"
    MODEL = "all-minilm"
    
    def __init__(self):
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.DATA_DIR)
        self.collection = self.client.get_or_create_collection(name=self.COLLECTION_NAME)

    def _chunk_text(self, text, chunk_size=800, overlap=100):
        if len(text) <= chunk_size:
            return [text]
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks
            
    def add_text(self, text):
        if not text.strip(): return
        
        chunks = self._chunk_text(text)
        
        for chunk in chunks:
            try:
                # Generate embedding via Ollama
                embedding = ollama.embeddings(model=self.MODEL, prompt=chunk)['embedding']
                
                # Generate unique ID
                chunk_id = str(uuid.uuid4())
                timestamp = datetime.now().isoformat()
                
                self.collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[{"timestamp": timestamp}],
                    ids=[chunk_id]
                )
            except Exception as e:
                print(f"RAG Indexing Error: {e}")
        
    def query(self, text, top_k=3):
        try:
            query_embedding = ollama.embeddings(model=self.MODEL, prompt=text)['embedding']
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Chroma returns list of lists (for multiple queries)
            if results and results['documents']:
                return results['documents'][0]
            return []
        except Exception as e:
            print(f"RAG Query Error: {e}")
            return []

    def get_all(self):
        # Fetch all documents to display in UI
        results = self.collection.get()
        return results['documents'] if results else []

    def delete(self, index):
        # Map list index to ID (assuming order is consistent with get())
        # Note: ChromaDB doesn't guarantee order like a list, so this is a best-effort 
        # mapping for the simple UI we have. A better UI would use IDs directly.
        results = self.collection.get()
        if results and results['ids']:
            # We assume the UI displays them in the order returned by get()
            ids = results['ids']
            if 0 <= index < len(ids):
                target_id = ids[index]
                self.collection.delete(ids=[target_id])
                return True
        return False

    def clear(self):
        """Clears the entire database."""
        try:
            self.client.delete_collection(self.COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(name=self.COLLECTION_NAME)
        except Exception as e:
            print(f"Clear DB Error: {e}")

class KnowledgeBase:
    _store = None
    @staticmethod
    def get_store():
        if not KnowledgeBase._store: KnowledgeBase._store = VectorStore()
        return KnowledgeBase._store
    @staticmethod
    def auto_index(text): KnowledgeBase.get_store().add_text(text)
    @staticmethod
    def get_context(query):
        results = KnowledgeBase.get_store().query(query)
        if not results: return ""
        return "\n--- RELEVANT CONTEXT ---\n" + "\n".join(results) + "\n------------------------\n"
    @staticmethod
    def get_all_memories():
        return KnowledgeBase.get_store().get_all()
    @staticmethod
    def delete_memory(index):
        return KnowledgeBase.get_store().delete(index)
    @staticmethod
    def clear():
        """Public method to clear memory."""
        KnowledgeBase.get_store().clear()
