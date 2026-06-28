import re
from dataclasses import dataclass
from typing import List

from backend.memory.document import MemoryDocument, ChunkType
from backend.memory.constants import MAX_CHUNK_SIZE, CHUNK_OVERLAP
from backend.memory.exceptions import ChunkingError

@dataclass
class Chunk:
    chunk_text: str
    chunk_order: int
    chunk_type: ChunkType

class ChunkingService:
    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()
        
    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        # Split by punctuation followed by space, keeping the punctuation attached.
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s]

    @staticmethod
    def chunk_document(doc: MemoryDocument) -> List[Chunk]:
        if not doc.text or not doc.text.strip():
            raise ChunkingError("Document text cannot be empty or just whitespace.")
            
        text = ChunkingService._normalize_whitespace(doc.text)
        sentences = ChunkingService._split_into_sentences(text)
        
        chunks = []
        chunk_order = 0
        
        current_chunk_sentences = []
        current_len = 0
        
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            sentence_len = len(sentence)
            
            if current_len + sentence_len + (1 if current_len > 0 else 0) <= MAX_CHUNK_SIZE:
                current_chunk_sentences.append(sentence)
                current_len += sentence_len + (1 if current_len > 0 else 0)
                i += 1
            else:
                # If the sentence itself is larger than MAX_CHUNK_SIZE and we have no sentences currently
                if not current_chunk_sentences:
                    # We must hard-split the sentence
                    sub_text = sentence
                    while sub_text:
                        chunks.append(Chunk(
                            chunk_text=sub_text[:MAX_CHUNK_SIZE],
                            chunk_order=chunk_order,
                            chunk_type=doc.chunk_type
                        ))
                        chunk_order += 1
                        if len(sub_text) > MAX_CHUNK_SIZE:
                            sub_text = sub_text[MAX_CHUNK_SIZE - CHUNK_OVERLAP:]
                        else:
                            break
                    i += 1
                    continue
                else:
                    # Current chunk is full, emit it
                    chunks.append(Chunk(
                        chunk_text=" ".join(current_chunk_sentences),
                        chunk_order=chunk_order,
                        chunk_type=doc.chunk_type
                    ))
                    chunk_order += 1
                    
                    # Backtrack to create overlap
                    overlap_len = 0
                    overlap_sentences = []
                    # We iterate backwards through the current chunk sentences
                    for s in reversed(current_chunk_sentences):
                        if overlap_len + len(s) + (1 if overlap_len > 0 else 0) <= CHUNK_OVERLAP:
                            overlap_sentences.insert(0, s)
                            overlap_len += len(s) + (1 if overlap_len > 0 else 0)
                        else:
                            break
                    
                    # If a single sentence was larger than CHUNK_OVERLAP, overlap_sentences might be empty
                    # We must advance i by at least 1 relative to the start of current_chunk_sentences
                    # to prevent infinite loops.
                    start_of_current = i - len(current_chunk_sentences)
                    next_start = i - len(overlap_sentences)
                    
                    if next_start <= start_of_current:
                        next_start = start_of_current + 1
                        
                    i = next_start
                    current_chunk_sentences = []
                    current_len = 0
                    
        # Emit any remaining sentences
        if current_chunk_sentences:
            chunks.append(Chunk(
                chunk_text=" ".join(current_chunk_sentences),
                chunk_order=chunk_order,
                chunk_type=doc.chunk_type
            ))
            
        return chunks
