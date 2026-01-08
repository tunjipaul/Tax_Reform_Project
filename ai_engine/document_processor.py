"""
document_processor.py
Document loading and chunking with robust handling for PDF text extraction.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import hashlib
import PyPDF2
from docx import Document as DocxDocument
import re

from config import config

@dataclass
class DocumentChunk:
    """Represents a chunk of a document"""
    content: str
    metadata: Dict
    chunk_id: str
    
    def __post_init__(self):
        if not self.chunk_id:
            # Create a deterministic ID based on content
            content_hash = hashlib.md5(self.content.encode()).hexdigest()
            source = self.metadata.get('source', 'unknown').replace(" ", "_")
            self.chunk_id = f"{source}_{content_hash[:8]}"


class DocumentProcessor:
    """Process tax reform documents for RAG system"""
    
    def __init__(self):
        self.docs_dir = Path(config.DOCS_DIRECTORY)
        self.chunk_size = config.CHUNK_SIZE      # e.g., 1000 words/tokens
        self.chunk_overlap = config.CHUNK_OVERLAP # e.g., 200 words/tokens
        self.supported_formats = config.SUPPORTED_FORMATS
    
    def load_documents(self) -> List[Dict]:
        """Load all documents from the documents directory"""
        documents = []
        
        if not self.docs_dir.exists():
            print(f"⚠️ Documents directory not found: {self.docs_dir}")
            return documents
        
        for file_path in self.docs_dir.rglob("*"):
            if file_path.suffix.lower() in self.supported_formats:
                try:
                    doc = self._load_single_document(file_path)
                    if doc and doc["content"].strip():
                        documents.append(doc)
                        print(f"✅ Loaded: {file_path.name} ({len(doc['content'])} chars)")
                    else:
                        print(f"⚠️ Skipped empty file: {file_path.name}")
                except Exception as e:
                    print(f"❌ Error loading {file_path.name}: {e}")
        
        print(f"\n📚 Total documents loaded: {len(documents)}")
        return documents
    
    def _load_single_document(self, file_path: Path) -> Optional[Dict]:
        """Load a single document based on file type"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self._load_pdf(file_path)
        elif suffix == '.txt' or suffix == '.md':
            return self._load_text(file_path)
        elif suffix == '.docx':
            return self._load_docx(file_path)
        else:
            return None
    
    def _load_pdf(self, file_path: Path) -> Dict:
        """Load PDF document with robust text extraction"""
        text = ""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)
                
                print(f"   ...processing {num_pages} pages in {file_path.name}")
                
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        # Clean up header/footer noise if needed, 
                        # or just append with a newline
                        text += f"\n{page_text}"
                    else:
                        print(f"   ⚠️ Warning: Page {i+1} in {file_path.name} yielded no text.")
                        
        except Exception as e:
            print(f"   ❌ PDF Read Error: {e}")
            return {"content": "", "metadata": {}}
        
        return {
            "content": text,
            "metadata": {
                "source": file_path.name,
                "type": "pdf",
                "path": str(file_path),
            }
        }
    
    def _load_text(self, file_path: Path) -> Dict:
        """Load text or markdown document"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return {
            "content": text,
            "metadata": {
                "source": file_path.name,
                "type": file_path.suffix[1:],
                "path": str(file_path)
            }
        }
    
    def _load_docx(self, file_path: Path) -> Dict:
        """Load Word document"""
        doc = DocxDocument(file_path)
        text = "\n\n".join([para.text for para in doc.paragraphs if para.text])
        
        return {
            "content": text,
            "metadata": {
                "source": file_path.name,
                "type": "docx",
                "path": str(file_path),
            }
        }
    
    def chunk_documents(self, documents: List[Dict]) -> List[DocumentChunk]:
        """Split documents into chunks using a sliding window approach"""
        all_chunks = []
        
        for doc in documents:
            chunks = self._recursive_chunk_document(doc)
            all_chunks.extend(chunks)
            print(f"📄 {doc['metadata']['source']}: {len(chunks)} chunks")
        
        print(f"\n✂️ Total chunks created: {len(all_chunks)}")
        return all_chunks

    def _recursive_chunk_document(self, document: Dict) -> List[DocumentChunk]:
        """
        Custom chunking logic that doesn't rely on double newlines.
        It uses a recursive logic similar to LangChain's RecursiveCharacterTextSplitter.
        """
        text = document["content"]
        metadata = document["metadata"]
        
        # 1. Clean up text slightly to normalize spacing
        # Replace multiple newlines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        chunks = []
        
        # We will split by simple separators in priority order
        separators = ["\n\n", "\n", ". ", " ", ""]
        
        final_chunks_text = self._split_text(text, separators, self.chunk_size, self.chunk_overlap)

        for i, chunk_text in enumerate(final_chunks_text):
            chunk = DocumentChunk(
                content=chunk_text.strip(),
                metadata={**metadata, "chunk_index": i},
                chunk_id=""
            )
            chunks.append(chunk)
            
        return chunks

    def _split_text(self, text: str, separators: List[str], chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Recursive splitting function.
        """
        final_chunks = []
        
        # Find the best separator
        separator = separators[-1]
        for sep in separators:
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                break
        
        # Split
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text) # Split by character
            
        # Merge splits into chunks
        current_chunk = []
        current_length = 0
        
        for split in splits:
            split_len = len(split.split()) if split.strip() else 0
            
            # If adding this split exceeds chunk size
            if current_length + split_len > chunk_size:
                if current_chunk:
                    # Join current buffer
                    doc_chunk = (separator if separator else "").join(current_chunk)
                    final_chunks.append(doc_chunk)
                    
                    # Handle overlap (keep last N items? simplify for now)
                    # For a robust overlap, we need to keep enough previous splits
                    # to fill 'chunk_overlap'. 
                    
                    # Simplified overlap logic:
                    # Keep the last split as the start of the next chunk (if it's not too big)
                    # Ideally we'd look back further, but this prevents simple data loss at boundaries
                    current_chunk = [current_chunk[-1]] if len(current_chunk) > 0 else []
                    current_length = len(current_chunk[0].split()) if current_chunk else 0
                
            current_chunk.append(split)
            current_length += split_len
            
        # Add the remainder
        if current_chunk:
            doc_chunk = (separator if separator else "").join(current_chunk)
            final_chunks.append(doc_chunk)
            
        return final_chunks

def load_and_chunk_documents() -> List[DocumentChunk]:
    """Load all documents and return chunks ready for embedding"""
    processor = DocumentProcessor()
    
    print("📖 Loading documents...")
    documents = processor.load_documents()
    
    if not documents:
        print("⚠️ No documents found!")
        return []
    
    print("\n✂️ Chunking documents...")
    chunks = processor.chunk_documents(documents)
    
    return chunks

if __name__ == "__main__":
    chunks = load_and_chunk_documents()
    
    if chunks:
        print(f"\n✅ Processing complete!")
        print(f"📊 Sample chunk 1:")
        print(f"   ID: {chunks[0].chunk_id}")
        print(f"   Source: {chunks[0].metadata['source']}")
        print(f"   Content Length: {len(chunks[0].content)}")
        print(f"   Content Preview: {chunks[0].content[:200]}...")
    else:
        print("\n❌ No chunks created. Add documents to ./documents/ directory")