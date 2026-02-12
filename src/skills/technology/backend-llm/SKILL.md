---
name: backend-llm
description: LLM API integration patterns. Use when story requires LLM integration, prompt engineering, RAG (retrieval augmented generation), function calling, streaming responses, or working with OpenAI/Anthropic APIs. References backend-semantic for embeddings.
---

# Backend LLM

LLM API integration patterns, prompt engineering, and RAG implementation.

## Prerequisites

For embedding fundamentals, see [backend-semantic](../backend-semantic/SKILL.md).

## LLM Providers

| Provider | Models | Strengths | Pricing |
|----------|--------|-----------|---------|
| OpenAI | GPT-4, GPT-3.5 | General purpose, tools | $3-$30/1M tokens |
| Anthropic | Claude 3.5 Sonnet | Long context, safety | $3-$15/1M tokens |
| Google | Gemini Pro | Multimodal, code | $1.25-$7/1M tokens |
| Local | Llama 3, Mistral | Privacy, cost | Free (compute) |

## OpenAI API

```python
from openai import OpenAI

client = OpenAI(api_key="your-key")

# Basic completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing"}
    ],
    temperature=0.7,
    max_tokens=500
)

print(response.choices[0].message.content)
```

## Anthropic API

```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

# Basic completion
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain quantum computing"}
    ]
)

print(response.content[0].text)
```

## Prompt Engineering

### System Prompts

```python
system_prompt = """You are an expert Python developer.
Follow these guidelines:
- Write clean, PEP 8 compliant code
- Include docstrings and type hints
- Handle errors gracefully
- Write tests for all functions
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Write a function to validate emails"}
]
```

### Few-Shot Examples

```python
messages = [
    {"role": "system", "content": "Extract entities from text."},
    {"role": "user", "content": "Apple announced iPhone 15 in California."},
    {"role": "assistant", "content": '{"company": "Apple", "product": "iPhone 15", "location": "California"}'},
    {"role": "user", "content": "Tesla opened factory in Texas."},
    {"role": "assistant", "content": '{"company": "Tesla", "product": "factory", "location": "Texas"}'},
    {"role": "user", "content": "Google released Gemini in December."}
]
```

### Chain-of-Thought

```python
user_prompt = """Problem: A store sold 15 apples on Monday, 23 on Tuesday, and 18 on Wednesday. How many total?

Think through this step-by-step:
1. Identify the numbers
2. Add them together
3. State the answer"""
```

## Function Calling (Tools)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in SF?"}],
    tools=tools,
    tool_choice="auto"
)

# Check if tool was called
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    
    # Execute function
    if tool_call.function.name == "get_weather":
        args = json.loads(tool_call.function.arguments)
        weather = get_weather(args["location"])
        
        # Send result back
        messages.append(response.choices[0].message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(weather)
        })
        
        final_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
```

## Streaming Responses

```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## RAG (Retrieval Augmented Generation)

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. Setup
model = SentenceTransformer('all-MiniLM-L6-v2')
documents = load_documents()  # Your doc corpus
doc_embeddings = model.encode(documents)

# 2. Retrieve relevant docs
def retrieve(query: str, top_k: int = 5) -> List[str]:
    query_embedding = model.encode([query])[0]
    
    # Cosine similarity
    similarities = np.dot(doc_embeddings, query_embedding) / (
        np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    
    # Get top-k
    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [documents[i] for i in top_indices]

# 3. Generate with context
def rag_query(question: str) -> str:
    # Retrieve
    context_docs = retrieve(question)
    context = "\n\n".join(context_docs)
    
    # Generate
    prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}

Answer based on the context above:"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

## Error Handling

```python
from openai import OpenAIError, RateLimitError, APIError
import time

def call_with_retry(
    func,
    max_attempts: int = 3,
    backoff_factor: float = 2.0
):
    for attempt in range(max_attempts):
        try:
            return func()
        except RateLimitError:
            if attempt == max_attempts - 1:
                raise
            wait = backoff_factor ** attempt
            time.sleep(wait)
        except APIError as e:
            logger.error(f"API error: {e}")
            raise

# Usage
response = call_with_retry(
    lambda: client.chat.completions.create(
        model="gpt-4",
        messages=[...]
    )
)
```

## Token Management

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def truncate_to_token_limit(text: str, max_tokens: int) -> str:
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated = tokens[:max_tokens]
    return encoding.decode(truncated)

# Estimate cost
input_tokens = count_tokens(prompt)
output_tokens = 500  # max_tokens
cost = (input_tokens * 0.03 + output_tokens * 0.06) / 1000  # GPT-4 pricing
```

## Conversation Memory

```python
class ConversationMemory:
    def __init__(self, max_tokens: int = 4000):
        self.messages = []
        self.max_tokens = max_tokens

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._truncate()

    def _truncate(self):
        """Keep conversation under token limit."""
        total_tokens = sum(count_tokens(m["content"]) for m in self.messages)
        
        while total_tokens > self.max_tokens and len(self.messages) > 1:
            # Remove oldest message (keep system prompt)
            self.messages.pop(1 if self.messages[0]["role"] == "system" else 0)
            total_tokens = sum(count_tokens(m["content"]) for m in self.messages)

    def get_messages(self) -> List[dict]:
        return self.messages
```

## Structured Output

```python
from pydantic import BaseModel

class ExtractedEntity(BaseModel):
    name: str
    type: str  # person, organization, location
    confidence: float

def extract_entities(text: str) -> List[ExtractedEntity]:
    prompt = f"""Extract named entities from this text.
Return as JSON array with fields: name, type, confidence.

Text: {text}

JSON:"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    return [ExtractedEntity(**entity) for entity in data["entities"]]
```

## Best Practices

1. **Use system prompts**: Set behavior and constraints
2. **Provide examples**: Few-shot learning improves accuracy
3. **Handle rate limits**: Exponential backoff with retries
4. **Monitor costs**: Track token usage and set budgets
5. **Cache results**: Avoid redundant API calls
6. **Stream for UX**: Show progress for long responses
7. **Validate output**: LLMs can hallucinate, validate responses
8. **Use tools**: Function calling for structured operations
9. **Context window management**: Truncate or summarize long conversations
10. **Test prompts**: Iterate on prompts with eval datasets
