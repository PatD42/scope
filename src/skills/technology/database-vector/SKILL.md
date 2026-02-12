---
name: database-vector
description: Vector database design and implementation. Use when story requires semantic search at scale, vector similarity queries, embedding storage, ANN indexes (HNSW/IVF), hybrid search, or vector databases (Pinecone, Weaviate, pgvector, Chroma). References backend-semantic for embedding fundamentals.
---

# Database Vector

Vector database patterns for storing and querying embeddings at scale.

## Prerequisites

This skill builds on embedding fundamentals. For embeddings and similarity basics, see [backend-semantic](../backend-semantic/SKILL.md).

## Vector Database Options

| Database | Type | Best For | Managed | Open Source |
|----------|------|----------|---------|-------------|
| Pinecone | Cloud-native | Production, scale | Yes | No |
| Weaviate | Hybrid | Flexibility, features | Optional | Yes |
| Chroma | Embedded | Development, prototypes | No | Yes |
| pgvector | PostgreSQL extension | Existing Postgres apps | No | Yes |
| Qdrant | High-performance | Speed, on-prem | Optional | Yes |

## pgvector (PostgreSQL Extension)

```sql
-- Install extension
CREATE EXTENSION vector;

-- Create table with vector column
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),  -- Dimension matches model
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index (HNSW for speed)
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);

-- Insert embedding
INSERT INTO documents (content, embedding, metadata)
VALUES (
    'Sample text',
    '[0.1, 0.2, ...]',  -- 1536-dim vector
    '{"category": "tech"}'
);

-- Similarity search (cosine)
SELECT id, content, 1 - (embedding <=> query_embedding) AS similarity
FROM documents
WHERE metadata->>'category' = 'tech'  -- Metadata filter
ORDER BY embedding <=> query_embedding  -- <=> = cosine distance
LIMIT 10;

-- Operators
-- <-> : L2 distance (Euclidean)
-- <=> : Cosine distance  
-- <#> : Inner product (dot product)
```

## Pinecone (Cloud)

```python
import pinecone

# Initialize
pinecone.init(api_key="your-key", environment="us-west1-gcp")

# Create index
pinecone.create_index(
    "my-index",
    dimension=1536,
    metric="cosine",
    pod_type="p1.x1"
)

# Connect to index
index = pinecone.Index("my-index")

# Upsert vectors
index.upsert(vectors=[
    ("id1", [0.1, 0.2, ...], {"category": "tech"}),
    ("id2", [0.3, 0.4, ...], {"category": "science"})
])

# Query
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=10,
    filter={"category": "tech"},  # Metadata filter
    include_metadata=True
)

for match in results.matches:
    print(f"ID: {match.id}, Score: {match.score}")
    print(f"Metadata: {match.metadata}")
```

## Weaviate

```python
import weaviate

# Connect
client = weaviate.Client("http://localhost:8080")

# Create schema
schema = {
    "class": "Document",
    "vectorizer": "text2vec-openai",
    "properties": [
        {"name": "content", "dataType": ["text"]},
        {"name": "category", "dataType": ["string"]}
    ]
}
client.schema.create_class(schema)

# Add documents (auto-vectorizes)
client.data_object.create(
    class_name="Document",
    data_object={
        "content": "Sample text",
        "category": "tech"
    }
)

# Semantic search
result = (
    client.query
    .get("Document", ["content", "category"])
    .with_near_text({"concepts": ["artificial intelligence"]})
    .with_where({
        "path": ["category"],
        "operator": "Equal",
        "valueString": "tech"
    })
    .with_limit(10)
    .do()
)
```

## Chroma (Embedded)

```python
import chromadb

# Create client
client = chromadb.Client()

# Get or create collection
collection = client.get_or_create_collection("my_collection")

# Add documents (auto-generates embeddings)
collection.add(
    documents=["doc1 text", "doc2 text"],
    metadatas=[{"category": "tech"}, {"category": "science"}],
    ids=["id1", "id2"]
)

# Query
results = collection.query(
    query_texts=["search query"],
    n_results=10,
    where={"category": "tech"}  # Metadata filter
)
```

## Index Types

### HNSW (Hierarchical Navigable Small World)

- **Speed**: Very fast queries (sub-ms)
- **Memory**: High memory usage
- **Accuracy**: High (>95%)
- **Best for**: Production, real-time search

```python
# pgvector
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

# Pinecone (default)
pinecone.create_index("my-index", dimension=1536, metric="cosine")
```

### IVF (Inverted File Index)

- **Speed**: Fast queries
- **Memory**: Lower memory usage
- **Accuracy**: Good (>90%)
- **Best for**: Large datasets, cost-sensitive

### Flat Index

- **Speed**: Slow (brute force)
- **Memory**: Lowest
- **Accuracy**: 100% (exact search)
- **Best for**: Small datasets (<10k), development

## Hybrid Search

Combine semantic (vector) and keyword (BM25) search:

```python
# Weaviate hybrid search
result = (
    client.query
    .get("Document", ["content"])
    .with_hybrid(
        query="user query",
        alpha=0.75  # 0 = pure keyword, 1 = pure vector
    )
    .with_limit(10)
    .do()
)

# Manual hybrid (pgvector + PostgreSQL)
WITH semantic_results AS (
    SELECT id, 1 - (embedding <=> query_embedding) AS semantic_score
    FROM documents
    ORDER BY embedding <=> query_embedding
    LIMIT 100
),
keyword_results AS (
    SELECT id, ts_rank(to_tsvector(content), query) AS keyword_score
    FROM documents
    WHERE to_tsvector(content) @@ query
)
SELECT 
    d.id,
    d.content,
    COALESCE(s.semantic_score, 0) * 0.7 +  -- Weight semantic
    COALESCE(k.keyword_score, 0) * 0.3 AS combined_score  -- Weight keyword
FROM documents d
LEFT JOIN semantic_results s ON d.id = s.id
LEFT JOIN keyword_results k ON d.id = k.id
WHERE s.id IS NOT NULL OR k.id IS NOT NULL
ORDER BY combined_score DESC
LIMIT 10;
```

## Metadata Filtering

```python
# Pinecone
index.query(
    vector=[...],
    filter={
        "category": {"$eq": "tech"},
        "date": {"$gte": "2025-01-01"},
        "$or": [
            {"tag": "python"},
            {"tag": "ai"}
        ]
    }
)

# pgvector
SELECT *
FROM documents
WHERE 
    metadata->>'category' = 'tech'
    AND (metadata->>'date')::date >= '2025-01-01'
    AND metadata->'tags' ?| array['python', 'ai']
ORDER BY embedding <=> query_embedding
LIMIT 10;
```

## Production Patterns

### Batch Upsert

```python
# Efficient batch insertion
batch_size = 100
for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    vectors = [(doc.id, doc.embedding, doc.metadata) for doc in batch]
    index.upsert(vectors=vectors)
```

### Sharding Strategy

```python
# Shard by namespace (Pinecone)
index.upsert(
    vectors=[(id, embedding, metadata)],
    namespace="user_123"  # Separate namespace per user
)

# Query specific namespace
index.query(
    vector=[...],
    namespace="user_123"
)
```

### Caching

```python
# Cache query results
import hashlib
import redis

redis_client = redis.Redis()

def cached_query(query_vector, top_k=10):
    # Create cache key from query
    cache_key = hashlib.sha256(query_vector.tobytes()).hexdigest()
    
    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Query vector DB
    results = index.query(vector=query_vector, top_k=top_k)
    
    # Cache results (1 hour TTL)
    redis_client.setex(cache_key, 3600, json.dumps(results))
    
    return results
```

## Scaling Considerations

| Dataset Size | Recommendation |
|--------------|----------------|
| <10k vectors | In-memory (Chroma, pgvector) |
| 10k-1M | Single index (pgvector, Pinecone starter) |
| 1M-10M | Managed service (Pinecone, Weaviate Cloud) |
| >10M | Sharded indexes, replicas |

## Cost Optimization

1. **Use smaller embeddings**: 384-dim vs 1536-dim (4x cheaper storage)
2. **Dimension reduction**: PCA/UMAP after embedding
3. **Quantization**: Store vectors as int8 vs float32 (4x smaller)
4. **Tiered storage**: Hot (SSD) vs cold (S3) for old data
5. **Smart caching**: Cache popular queries

## Best Practices

1. **Match dimensions**: Embedding model and DB must agree
2. **Index after bulk load**: Don't index during initial data load
3. **Metadata for filtering**: Store filterable fields as metadata
4. **Monitor query latency**: P95, P99 latencies matter
5. **Test with production scale**: Performance degrades with size
6. **Backup regularly**: Vector data is expensive to regenerate
7. **Version your embeddings**: Model changes require reindexing
