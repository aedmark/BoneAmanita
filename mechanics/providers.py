import os

CLOUD_ENDPOINTS = {
    "xai": "https://api.x.ai/v1/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages",
}
KEY_ENV = {"xai": "XAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}


def normalize_provider(provider):
    name = provider.lower()
    return {"grok": "xai", "claude": "anthropic"}.get(name, name)


def environment_config(config):
    result = dict(config)
    provider = os.getenv("BONE_PROVIDER")
    if provider:
        result["provider"] = normalize_provider(provider)
        if result["provider"] in CLOUD_ENDPOINTS:
            result["base_url"] = CLOUD_ENDPOINTS[result["provider"]]
            result["api_key"] = os.getenv(KEY_ENV[result["provider"]], "")
            if not os.getenv("BONE_MODEL"):
                raise ValueError("Set BONE_MODEL to a model ID available to your API key")
    for key in ("model", "base_url"):
        if value := os.getenv("BONE_" + key.upper()):
            result[key] = value
    return result
