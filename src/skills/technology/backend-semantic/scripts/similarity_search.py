#!/usr/bin/env python3
"""
Find most similar texts using semantic similarity.

Usage:
    python similarity_search.py --query "user question" --candidates candidates.txt --top-k 5
    python similarity_search.py --query "user question" --embeddings embeddings.json --metric cosine
"""

import argparse
import json
import sys
from typing import List, Tuple
import numpy as np


def cosine_similarity(query: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between query and candidates.

    Returns: similarity scores (higher = more similar)
    Range: [-1, 1], typically [0, 1] for text embeddings
    """
    # Normalize vectors
    query_norm = query / np.linalg.norm(query)
    candidates_norm = candidates / np.linalg.norm(candidates, axis=1, keepdims=True)

    # Dot product of normalized vectors = cosine similarity
    similarities = np.dot(candidates_norm, query_norm)
    return similarities


def dot_product_similarity(query: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """
    Compute dot product similarity between query and candidates.

    Returns: similarity scores (higher = more similar)
    Faster than cosine but sensitive to vector magnitude.
    """
    similarities = np.dot(candidates, query)
    return similarities


def euclidean_distance(query: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """
    Compute Euclidean (L2) distance between query and candidates.

    Returns: distances (lower = more similar)
    Convert to similarity: 1 / (1 + distance)
    """
    distances = np.linalg.norm(candidates - query, axis=1)
    return distances


def search(query_embedding: np.ndarray, candidate_embeddings: np.ndarray,
           metric: str = "cosine", top_k: int = 5) -> List[Tuple[int, float]]:
    """
    Search for most similar candidates.

    Returns: List of (index, score) tuples sorted by similarity
    """
    if metric == "cosine":
        scores = cosine_similarity(query_embedding, candidate_embeddings)
        # Higher is better for cosine
        top_indices = np.argsort(scores)[::-1][:top_k]
    elif metric == "dot":
        scores = dot_product_similarity(query_embedding, candidate_embeddings)
        # Higher is better for dot product
        top_indices = np.argsort(scores)[::-1][:top_k]
    elif metric == "euclidean":
        distances = euclidean_distance(query_embedding, candidate_embeddings)
        # Lower is better for distance
        top_indices = np.argsort(distances)[:top_k]
        # Convert distance to similarity score
        scores = 1 / (1 + distances)
    else:
        raise ValueError(f"Unknown metric: {metric}")

    results = [(int(idx), float(scores[idx])) for idx in top_indices]
    return results


def main():
    parser = argparse.ArgumentParser(description="Semantic similarity search")
    parser.add_argument("--query", required=True, help="Query text")
    parser.add_argument("--candidates", help="File with candidate texts (one per line)")
    parser.add_argument("--embeddings", help="JSON file with precomputed embeddings")
    parser.add_argument("--metric", choices=["cosine", "dot", "euclidean"], default="cosine",
                       help="Similarity metric")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--model", default="sentence-transformers", help="Model for computing embeddings")

    args = parser.parse_args()

    # Load or compute embeddings
    if args.embeddings:
        # Use precomputed embeddings
        with open(args.embeddings, 'r') as f:
            data = json.load(f)
        candidate_texts = data["texts"]
        candidate_embeddings = np.array(data["embeddings"])

        # Compute query embedding (assume same model)
        if args.model == "sentence-transformers":
            from compute_embeddings import compute_with_sentence_transformers
            query_embedding = compute_with_sentence_transformers([args.query])[0]
        else:
            print("Error: Only sentence-transformers supported for query embedding", file=sys.stderr)
            sys.exit(1)

    elif args.candidates:
        # Compute embeddings on the fly
        with open(args.candidates, 'r') as f:
            candidate_texts = [line.strip() for line in f if line.strip()]

        if args.model == "sentence-transformers":
            from compute_embeddings import compute_with_sentence_transformers
            all_texts = [args.query] + candidate_texts
            all_embeddings = compute_with_sentence_transformers(all_texts)
            query_embedding = all_embeddings[0]
            candidate_embeddings = all_embeddings[1:]
        else:
            print("Error: Only sentence-transformers supported", file=sys.stderr)
            sys.exit(1)
    else:
        parser.error("Must provide either --embeddings or --candidates")

    # Perform search
    results = search(query_embedding, candidate_embeddings, args.metric, args.top_k)

    # Display results
    print(f"\nQuery: {args.query}")
    print(f"Metric: {args.metric}")
    print(f"\nTop {args.top_k} results:\n")

    for rank, (idx, score) in enumerate(results, 1):
        print(f"{rank}. [{score:.4f}] {candidate_texts[idx]}")


if __name__ == "__main__":
    main()
