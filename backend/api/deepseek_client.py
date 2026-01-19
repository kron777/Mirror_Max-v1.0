import httpx
import os
import time
from pathlib import Path
from typing import Dict, Any
import asyncio

# Manual .env loading - reliable fallback
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

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

async def deepseek_generate(
    prompt: str,
    model: str = "deepseek/deepseek-r1",  # Stable & available model on OpenRouter (Jan 2026)
    max_tokens: int = 1024,
    temperature: float = 0.7,
    timeout: float = 60.0,          # Shorter per attempt
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Call DeepSeek via OpenRouter with retry on timeout/hang
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(1, max_retries + 1):
            start_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://mirror-max.local",
                "X-Title": "Mirror Max Debate"
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            try:
                print(f"Attempt {attempt}/{max_retries}...")
                response = await client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens", 0)
                
                latency_ms = (time.time() - start_time) * 1000
                
                return {
                    "content": content,
                    "tokens_used": tokens_used,
                    "latency_ms": latency_ms
                }
                
            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadTimeout) as e:
                print(f"Timeout/connect error on attempt {attempt}: {str(e)}")
                if attempt == max_retries:
                    raise RuntimeError(f"Max retries exceeded - network/server issue: {str(e)}")
                await asyncio.sleep(5)  # Exponential backoff
            except Exception as e:
                raise RuntimeError(f"OpenRouter error: {str(e)}\n"
                                  f"Try alternative model: deepseek/deepseek-v3")
