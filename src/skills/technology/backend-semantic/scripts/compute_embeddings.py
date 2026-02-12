#!/usr/bin/env python3
"""
Compute embeddings for text using various models.

Usage:
    python compute_embeddings.py --texts "text1" "text2" --model sentence-transformers
    python compute_embeddings.py --file texts.txt --model openai --output embeddings.json
"""

import argparse
import json
import sys
from typing import List, Optional
import numpy as np


def compute_with_sentence_transformers(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """
    Compute embeddings using sentence-transformers (local, fast, free).

    Popular models:
    - all-MiniLM-L6-v2: 384 dims, fast, good for general use
    - all-mpnet-base-v2: 768 dims, slower, better quality
    - paraphrase-MiniLM-L6-v2: 384 dims, optimized for paraphrase detection
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Error: sentence-transformers not installed. Install with: pip install sentence-transformers", file=sys.stderr)
        sys.exit(1)

    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings


def compute_with_openai(texts: List[str], model_name: str = "text-embedding-3-small") -> np.ndarray:
    """
    Compute embeddings using OpenAI API (requires API key, costs $).

    Models:
    - text-embedding-3-small: 1536 dims, $0.02/1M tokens, good quality
    - text-embedding-3-large: 3072 dims, $0.13/1M tokens, best quality
    - text-embedding-ada-002: 1536 dims, legacy model
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai not installed. Install with: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI()  # Reads OPENAI_API_KEY from environment

    response = client.embeddings.create(
        model=model_name,
        input=texts
    )

    embeddings = np.array([item.embedding for item in response.data])
    return embeddings


def main():
    parser = argparse.ArgumentParser(description="Compute text embeddings")
    parser.add_argument("--texts", nargs="+", help="Texts to embed")
    parser.add_argument("--file", help="File containing texts (one per line)")
    parser.add_argument("--model", choices=["sentence-transformers", "openai"], required=True,
                       help="Embedding model to use")
    parser.add_argument("--model-name", help="Specific model name (optional)")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")

    args = parser.parse_args()

    # Load texts
    if args.texts:
        texts = args.texts
    elif args.file:
        with open(args.file, 'r') as f:
            texts = [line.strip() for line in f if line.strip()]
    else:
        parser.error("Must provide either --texts or --file")

    # Compute embeddings
    if args.model == "sentence-transformers":
        model_name = args.model_name or "all-MiniLM-L6-v2"
        embeddings = compute_with_sentence_transformers(texts, model_name)
    elif args.model == "openai":
        model_name = args.model_name or "text-embedding-3-small"
        embeddings = compute_with_openai(texts, model_name)

    # Output results
    result = {
        "model": args.model,
        "model_name": model_name if args.model_name else None,
        "texts": texts,
        "embeddings": embeddings.tolist(),
        "shape": embeddings.shape
    }

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Embeddings saved to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
