import httpx
import os
import time
from pathlib import Path
from typing import Dict, Any

# ────────────────────────────────────────────────
# Manual .env loading (reliable fallback)
# ────────────────────────────────────────────────
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
else:
    raise FileNotFoundError(f".env not found at {env_path}")

GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY not found after manual parsing")

GROK_BASE_URL = "https://api.x.ai/v1"

async def grok_generate(
    prompt: str,
    model: str = "grok-beta",  # Change to current model name if needed
    max_tokens: int = 1024,
    temperature: float = 0.7,
    timeout: float = 90.0
) -> Dict[str, Any]:
    """
    Call Grok / xAI API (OpenAI-compatible format)
    Returns {'content': str, 'tokens_used': int, 'latency_ms': float}
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = await client.post(
                f"{GROK_BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("completion_tokens", 0) + \
                         data.get("usage", {}).get("prompt_tokens", 0)
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "content": content,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms
            }
            
        except Exception as e:
            raise RuntimeError(f"Grok API error: {str(e)}")
