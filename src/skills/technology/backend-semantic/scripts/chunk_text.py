#!/usr/bin/env python3
"""
Chunk text for embedding with various strategies.

Usage:
    python chunk_text.py --file document.txt --strategy sentence --max-tokens 512
    python chunk_text.py --file document.txt --strategy paragraph --overlap 50
"""

import argparse
import json
import re
import sys
from typing import List, Dict


def chunk_by_sentences(text: str, max_tokens: int = 512, overlap: int = 0) -> List[Dict]:
    """
    Chunk text by sentences, keeping chunks under max_tokens.

    Overlap: number of tokens to overlap between chunks (useful for context preservation)
    """
    # Simple sentence splitting (can be improved with spacy/nltk)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = len(sentence.split())

        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            # Save current chunk
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "tokens": current_tokens,
                "sentences": len(current_chunk)
            })

            # Handle overlap
            if overlap > 0:
                # Keep last few sentences for overlap
                overlap_sentences = []
                overlap_tokens = 0
                for sent in reversed(current_chunk):
                    sent_tokens = len(sent.split())
                    if overlap_tokens + sent_tokens > overlap:
                        break
                    overlap_sentences.insert(0, sent)
                    overlap_tokens += sent_tokens

                current_chunk = overlap_sentences
                current_tokens = overlap_tokens
            else:
                current_chunk = []
                current_tokens = 0

        current_chunk.append(sentence)
        current_tokens += sentence_tokens

    # Add final chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append({
            "text": chunk_text,
            "tokens": current_tokens,
            "sentences": len(current_chunk)
        })

    return chunks


def chunk_by_paragraphs(text: str, max_tokens: int = 512, overlap: int = 0) -> List[Dict]:
    """
    Chunk text by paragraphs, keeping chunks under max_tokens.
    """
    paragraphs = text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks = []
    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = len(para.split())

        if current_tokens + para_tokens > max_tokens and current_chunk:
            # Save current chunk
            chunk_text = "\n\n".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "tokens": current_tokens,
                "paragraphs": len(current_chunk)
            })

            # Handle overlap
            if overlap > 0 and current_chunk:
                last_para = current_chunk[-1]
                last_para_tokens = len(last_para.split())
                if last_para_tokens <= overlap:
                    current_chunk = [last_para]
                    current_tokens = last_para_tokens
                else:
                    current_chunk = []
                    current_tokens = 0
            else:
                current_chunk = []
                current_tokens = 0

        current_chunk.append(para)
        current_tokens += para_tokens

    # Add final chunk
    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunks.append({
            "text": chunk_text,
            "tokens": current_tokens,
            "paragraphs": len(current_chunk)
        })

    return chunks


def chunk_by_tokens(text: str, max_tokens: int = 512, overlap: int = 0) -> List[Dict]:
    """
    Chunk text by fixed token count (sliding window).

    Simplest strategy but may break mid-sentence.
    """
    tokens = text.split()
    chunks = []

    stride = max_tokens - overlap
    for i in range(0, len(tokens), stride):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = " ".join(chunk_tokens)
        chunks.append({
            "text": chunk_text,
            "tokens": len(chunk_tokens),
            "start_idx": i,
            "end_idx": i + len(chunk_tokens)
        })

        if i + max_tokens >= len(tokens):
            break

    return chunks


def chunk_by_semantic(text: str, max_tokens: int = 512) -> List[Dict]:
    """
    Chunk text by semantic boundaries (requires sentence embeddings).

    Groups sentences with high semantic similarity.
    More sophisticated but requires embeddings.
    """
    print("Error: Semantic chunking requires sentence-transformers", file=sys.stderr)
    print("Use --strategy sentence or --strategy paragraph instead", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Chunk text for embedding")
    parser.add_argument("--file", required=True, help="Input text file")
    parser.add_argument("--strategy", choices=["sentence", "paragraph", "token", "semantic"],
                       default="sentence", help="Chunking strategy")
    parser.add_argument("--max-tokens", type=int, default=512,
                       help="Maximum tokens per chunk")
    parser.add_argument("--overlap", type=int, default=0,
                       help="Token overlap between chunks")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")

    args = parser.parse_args()

    # Read input file
    with open(args.file, 'r') as f:
        text = f.read()

    # Chunk text
    if args.strategy == "sentence":
        chunks = chunk_by_sentences(text, args.max_tokens, args.overlap)
    elif args.strategy == "paragraph":
        chunks = chunk_by_paragraphs(text, args.max_tokens, args.overlap)
    elif args.strategy == "token":
        chunks = chunk_by_tokens(text, args.max_tokens, args.overlap)
    elif args.strategy == "semantic":
        chunks = chunk_by_semantic(text, args.max_tokens)

    # Output results
    result = {
        "file": args.file,
        "strategy": args.strategy,
        "max_tokens": args.max_tokens,
        "overlap": args.overlap,
        "num_chunks": len(chunks),
        "chunks": chunks
    }

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Chunks saved to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
