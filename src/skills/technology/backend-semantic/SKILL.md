---
name: backend-semantic
description: Foundational semantic and embedding knowledge for backend development. Use when story requires semantic similarity, text embeddings, or semantic search without requiring full LLM integration or vector database. Covers embedding models, similarity metrics, text chunking, and in-memory semantic operations.
---

# Backend Semantic

Foundational knowledge for semantic operations in backend code: embeddings, similarity metrics, text chunking, and in-memory semantic search.

## When to Use

Use this skill for stories that require:
- Semantic similarity comparison (find similar texts)
- Text embeddings (convert text to semantic vectors)
- Semantic search in small datasets (<10k items, in-memory)
- Duplicate detection with semantic matching
- Text clustering or categorization
- FAQ matching with predefined answers

**Don't use for:**
- LLM API integration → Use `backend-llm` instead
- Large-scale vector storage → Use `database-vector` instead
- Pure keyword search → Standard string matching sufficient

## Text Embeddings

### What Are Embeddings?

Embeddings convert text into dense numeric vectors (arrays of floats) that represent semantic meaning. Semantically similar texts have similar vectors.

```python
"dog" → [0.2, 0.8, 0.1, ...]  # 384 dimensions
"puppy" → [0.3, 0.7, 0.2, ...]  # Similar vector (close in meaning)
"car" → [0.9, 0.1, 0.5, ...]  # Different vector (different meaning)
```

### Embedding Models

**Local Models (sentence-transformers)**
Free, fast, runs locally. No API required.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["text1", "text2"])
```

| Model | Dimensions | Speed | Quality | Use Case |
|-------|------------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | General purpose, production |
| all-mpnet-base-v2 | 768 | Medium | Better | Higher quality, slower |
| paraphrase-MiniLM-L6-v2 | 384 | Fast | Good | Paraphrase detection |

**API Models (OpenAI)**
Requires API key, costs per token. Better quality.

```python
from openai import OpenAI

client = OpenAI()
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["text1", "text2"]
)
embeddings = [item.embedding for item in response.data]
```

| Model | Dimensions | Cost | Use Case |
|-------|------------|------|----------|
| text-embedding-3-small | 1536 | $0.02/1M tokens | Production, good quality |
| text-embedding-3-large | 3072 | $0.13/1M tokens | Best quality |

**When to use each:**
- Local (sentence-transformers): No API costs, data stays local, fast for batch processing
- OpenAI: Better quality, easier setup, good for user-facing features

### Compute Embeddings Script

Use `scripts/compute_embeddings.py` for embedding generation:

```bash
# Local model (free, fast)
python scripts/compute_embeddings.py \
  --texts "text1" "text2" \
  --model sentence-transformers \
  --output embeddings.json

# OpenAI model (requires OPENAI_API_KEY)
python scripts/compute_embeddings.py \
  --file texts.txt \
  --model openai \
  --model-name text-embedding-3-small \
  --output embeddings.json
```

## Similarity Metrics

### Cosine Similarity

Most common for text embeddings. Measures angle between vectors (0° = identical, 180° = opposite).

```python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Range: [-1, 1], typically [0, 1] for text
# 1.0 = identical, 0.0 = unrelated, -1.0 = opposite
```

**When to use:** Default choice for semantic similarity. Normalized by vector magnitude.

### Dot Product

Faster than cosine but sensitive to vector magnitude.

```python
def dot_product(a, b):
    return np.dot(a, b)
```

**When to use:** When embeddings are already normalized, or when magnitude matters.

### Euclidean Distance

Measures straight-line distance in vector space.

```python
def euclidean_distance(a, b):
    return np.linalg.norm(a - b)

# Lower = more similar
# Convert to similarity: 1 / (1 + distance)
```

**When to use:** When absolute distance matters, or clustering applications.

### Similarity Search Script

Use `scripts/similarity_search.py` for finding similar items:

```bash
# Search with cosine similarity
python scripts/similarity_search.py \
  --query "user question here" \
  --candidates candidates.txt \
  --metric cosine \
  --top-k 5

# Search with precomputed embeddings
python scripts/similarity_search.py \
  --query "user question" \
  --embeddings embeddings.json \
  --metric cosine
```

## Text Chunking

Large texts must be chunked before embedding (models have token limits: 512-8192 tokens).

### Chunking Strategies

**By Sentences** (Recommended)
Preserves semantic units, natural boundaries.

```python
# Chunk by sentences, max 512 tokens, 50 token overlap
python scripts/chunk_text.py \
  --file document.txt \
  --strategy sentence \
  --max-tokens 512 \
  --overlap 50
```

**By Paragraphs**
Better for structured documents with clear paragraph breaks.

```python
# Chunk by paragraphs
python scripts/chunk_text.py \
  --file document.txt \
  --strategy paragraph \
  --max-tokens 512
```

**By Tokens** (Sliding Window)
Simplest but may break mid-sentence. Use for unstructured text.

```python
# Fixed token chunks with overlap
python scripts/chunk_text.py \
  --file document.txt \
  --strategy token \
  --max-tokens 512 \
  --overlap 50
```

### Overlap Strategy

Overlapping chunks preserve context across boundaries:
- **0 tokens**: Faster, less redundancy, may lose context at boundaries
- **50-100 tokens**: Good balance, preserves context
- **200+ tokens**: High redundancy, useful for critical information retrieval

## In-Memory Semantic Search

For small datasets (<10k items), use in-memory search with numpy:

```python
import numpy as np
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Embed candidates (one-time)
candidates = ["text1", "text2", "text3", ...]
candidate_embeddings = model.encode(candidates)

# Search function
def search(query: str, top_k: int = 5):
    query_embedding = model.encode([query])[0]

    # Cosine similarity
    similarities = np.dot(candidate_embeddings, query_embedding) / (
        np.linalg.norm(candidate_embeddings, axis=1) * np.linalg.norm(query_embedding)
    )

    # Get top-k
    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [(candidates[i], similarities[i]) for i in top_indices]

# Use
results = search("user query", top_k=5)
```

**When to scale up:**
- \>10k items: Consider caching embeddings to disk
- \>100k items: Use vector database (see `database-vector` skill)
- Real-time high QPS: Use vector database with indexing

## Semantic vs Keyword Search

| Aspect | Semantic Search | Keyword Search |
|--------|----------------|----------------|
| Matches | Meaning/intent | Exact words |
| "Dog" finds | "Puppy", "Canine" | Only "Dog" |
| Typos | Handles well | Requires fuzzy match |
| Speed | Slower (embed + compare) | Faster (string match) |
| Setup | Requires embeddings | Simple |
| Best for | User queries, FAQs, intent | Tags, IDs, exact terms |

**Hybrid approach:** Use keyword for filtering, semantic for ranking:
```python
# 1. Filter by keyword (fast)
keyword_matches = [c for c in candidates if keyword in c.lower()]

# 2. Rank by semantic similarity (accurate)
results = semantic_search(query, keyword_matches, top_k=5)
```

## Example: FAQ Matching

Complete example for FAQ matching system:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize
model = SentenceTransformer('all-MiniLM-L6-v2')

faqs = [
    {"q": "How do I reset my password?", "a": "Click 'Forgot Password' on login page..."},
    {"q": "What are your business hours?", "a": "Monday-Friday 9am-5pm EST..."},
    {"q": "How do I contact support?", "a": "Email support@example.com or..."},
]

# Embed FAQ questions (one-time)
faq_embeddings = model.encode([faq["q"] for faq in faqs])

# Search function
def find_faq(user_query: str, threshold: float = 0.7):
    query_embedding = model.encode([user_query])[0]

    # Cosine similarity
    similarities = np.dot(faq_embeddings, query_embedding) / (
        np.linalg.norm(faq_embeddings, axis=1) * np.linalg.norm(query_embedding)
    )

    best_idx = np.argmax(similarities)
    best_score = similarities[best_idx]

    # Return if above threshold
    if best_score >= threshold:
        return faqs[best_idx], best_score
    else:
        return None, best_score  # No good match

# Use
user_question = "I forgot my login credentials"
faq, score = find_faq(user_question)
if faq:
    print(f"Match: {faq['q']} (score: {score:.2f})")
    print(f"Answer: {faq['a']}")
else:
    print("No matching FAQ found")
```

## Helper Scripts

This skill includes Python scripts for common operations:

- **compute_embeddings.py** - Generate embeddings using sentence-transformers or OpenAI
- **similarity_search.py** - Find most similar texts using various metrics
- **chunk_text.py** - Chunk large texts with different strategies

All scripts support `--help` for full usage documentation.
