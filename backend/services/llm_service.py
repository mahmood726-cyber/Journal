"""
Local LLM service using Ollama for all AI functionality.
Provides a unified interface for text generation, embeddings, and chat.
"""
from typing import List, Dict, Any, Optional
import httpx
import numpy as np
from pydantic import BaseModel
import asyncio
from functools import lru_cache
import hashlib
import json
from core.config import settings


class LLMResponse(BaseModel):
    """Response from LLM generation."""
    text: str
    model: str
    tokens_used: int
    finish_reason: str


class EmbeddingResponse(BaseModel):
    """Response from embedding generation."""
    embedding: List[float]
    model: str
    dimensions: int


class LocalLLMService:
    """
    Service for interacting with local Llama via Ollama.

    Features:
    - Text generation
    - Embeddings
    - Streaming responses
    - Response caching
    - Connection pooling
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3.1:8b",
        embedding_model: str = "nomic-embed-text",
        timeout: int = 120,
        cache_enabled: bool = True
    ):
        """Initialize LLM service."""
        self.base_url = base_url
        self.default_model = default_model
        self.embedding_model = embedding_model
        self.timeout = timeout
        self.cache_enabled = cache_enabled

        # Response cache
        self._cache: Dict[str, Any] = {}

        # HTTP client with connection pooling
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        format: Optional[str] = None,  # "json" for JSON output
        stream: bool = False,
        cache_key: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate text completion from prompt.

        Args:
            prompt: Input prompt
            model: Model name (defaults to default_model)
            system: System message
            temperature: Sampling temperature (0-1)
            max_tokens: Max tokens to generate
            format: Output format ("json" for JSON)
            stream: Enable streaming
            cache_key: Custom cache key

        Returns:
            LLMResponse with generated text
        """
        model = model or self.default_model

        # Check cache
        if self.cache_enabled and cache_key:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        # Build request
        request_data = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }

        if system:
            request_data["system"] = system

        if max_tokens:
            request_data["options"]["num_predict"] = max_tokens

        if format == "json":
            request_data["format"] = "json"

        # Make request
        response = await self.client.post("/api/generate", json=request_data)
        response.raise_for_status()

        result = response.json()

        llm_response = LLMResponse(
            text=result["response"],
            model=model,
            tokens_used=result.get("eval_count", 0),
            finish_reason=result.get("done_reason", "stop")
        )

        # Cache result
        if self.cache_enabled and cache_key:
            self._add_to_cache(cache_key, llm_response)

        return llm_response

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        format: Optional[str] = None
    ) -> LLMResponse:
        """
        Chat completion with conversation history.

        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Model name
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            format: Output format ("json" for JSON)

        Returns:
            LLMResponse with assistant's reply
        """
        model = model or self.default_model

        # Build request
        request_data = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        if max_tokens:
            request_data["options"]["num_predict"] = max_tokens

        if format == "json":
            request_data["format"] = "json"

        # Make request
        response = await self.client.post("/api/chat", json=request_data)
        response.raise_for_status()

        result = response.json()

        return LLMResponse(
            text=result["message"]["content"],
            model=model,
            tokens_used=result.get("eval_count", 0),
            finish_reason=result.get("done_reason", "stop")
        )

    async def embed(
        self,
        text: str,
        model: Optional[str] = None,
        cache_key: Optional[str] = None
    ) -> EmbeddingResponse:
        """
        Generate embedding for text.

        Args:
            text: Input text
            model: Embedding model name
            cache_key: Custom cache key

        Returns:
            EmbeddingResponse with embedding vector
        """
        model = model or self.embedding_model

        # Check cache
        if self.cache_enabled and cache_key:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        # Make request
        response = await self.client.post(
            "/api/embeddings",
            json={"model": model, "prompt": text}
        )
        response.raise_for_status()

        result = response.json()

        embedding_response = EmbeddingResponse(
            embedding=result["embedding"],
            model=model,
            dimensions=len(result["embedding"])
        )

        # Cache result
        if self.cache_enabled and cache_key:
            self._add_to_cache(cache_key, embedding_response)

        return embedding_response

    async def embed_batch(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[EmbeddingResponse]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts
            model: Embedding model name

        Returns:
            List of EmbeddingResponse
        """
        tasks = [self.embed(text, model) for text in texts]
        return await asyncio.gather(*tasks)

    async def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Stream text generation (yields tokens as they're generated).

        Args:
            prompt: Input prompt
            model: Model name
            system: System message
            temperature: Sampling temperature

        Yields:
            str: Generated tokens
        """
        model = model or self.default_model

        request_data = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": temperature}
        }

        if system:
            request_data["system"] = system

        async with self.client.stream("POST", "/api/generate", json=request_data) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                    except json.JSONDecodeError:
                        continue

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        response = await self.client.get("/api/tags")
        response.raise_for_status()
        return response.json()["models"]

    async def pull_model(self, model: str) -> bool:
        """
        Pull a model from Ollama registry.

        Args:
            model: Model name to pull

        Returns:
            bool: Success status
        """
        try:
            response = await self.client.post("/api/pull", json={"name": model})
            response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False

    async def health_check(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = await self.client.get("/")
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments."""
        key_str = "|".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        return self._cache.get(key)

    def _add_to_cache(self, key: str, value: Any):
        """Add item to cache (LRU-style, max 1000 items)."""
        if len(self._cache) >= 1000:
            # Remove oldest item
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = value

    def clear_cache(self):
        """Clear response cache."""
        self._cache.clear()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Singleton instance
_llm_service: Optional[LocalLLMService] = None


def get_llm_service() -> LocalLLMService:
    """Get singleton LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LocalLLMService(
            base_url=getattr(settings, 'OLLAMA_URL', 'http://localhost:11434'),
            default_model=getattr(settings, 'OLLAMA_MODEL', 'llama3.1:8b'),
            embedding_model=getattr(settings, 'OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
        )
    return _llm_service


async def shutdown_llm_service():
    """Shutdown LLM service (call on app shutdown)."""
    global _llm_service
    if _llm_service:
        await _llm_service.close()
        _llm_service = None
