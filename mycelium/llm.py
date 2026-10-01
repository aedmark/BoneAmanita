import json
import urllib.request
import urllib.error
from typing import Optional

class OllamaInterface:
    """Connects Mycelium to a local Ollama instance."""
    def __init__(self, model: str = "mistral-nemo:latest", host: str = "http://127.0.0.1:11434"):
        self.model = model
        self.host = host
        self.api_url = f"{self.host}/api/generate"

    def generate(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        req = urllib.request.Request(
            self.api_url, 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("response", "").strip()
        except urllib.error.URLError as e:
            print(f"[OllamaInterface] Error connecting to {self.host}: {e}")
            return None
