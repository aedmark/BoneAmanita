"""The doctor: is this machine ready to run BoneAmanita, and if not, what is the one command that fixes each thing?

    python main.py --doctor      # checks only what is free: local servers, packages, folders, one tiny local reply; no paid request

Every check returns a status and, when it is not OK, the fix. FAIL means the engine cannot run; WARN means it runs worse
(memory on hash coordinates, no critic, no ordvec); INFO is a fact. The first-run wizard shows the same report once it has
written `config.json`, and lists the Ollama models you already have instead of asking you to remember a name."""
from __future__ import annotations

import importlib.util
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

OK, WARN, FAIL, INFO = "ok", "warn", "FAIL", "info"
REQUIRED = {"requests": "pip install requests", "numpy": "pip install numpy"}
OPTIONAL = {
    "faiss": ("faiss-cpu", "the deep associative memory"),
    "dspy": ("dspy", "the reply critic"),
    "ordvec": ("ordvec", "the subconscious memory search and the governor's bitmap gate"),
    "markdown": ("markdown", "markdown rendering"),
}
logger = logging.getLogger(__name__)
PROBE_TEXT = "the cartographer maps the room"
_ROOT = re.compile(r"/(v1/chat/completions|v1/embeddings|v1|api/chat)/?$")


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str = ""
    fix: str = ""


def _get(url: str, timeout: float = 5.0) -> dict:
    import requests

    reply = requests.get(url, timeout=timeout)
    reply.raise_for_status()
    return reply.json()


def _post(url: str, payload: dict, headers: Optional[dict] = None, timeout: float = 5.0) -> dict:
    import requests

    reply = requests.post(url, json=payload, headers=headers or {}, timeout=timeout)
    reply.raise_for_status()
    return reply.json()


def _attempt(call: Callable, *args):
    """(result, None), or (None, the error) when a server is down or answers badly; the error becomes the check's detail."""
    try:
        return call(*args), None
    except (OSError, ValueError, KeyError, IndexError) as error:
        logger.log(logging.INFO, "doctor: %s failed: %s: %s", getattr(call, "__name__", "call"), type(error).__name__, error)
        return None, error


def server_root(url: str) -> str:
    return _ROOT.sub("", str(url or "").rstrip("/"))


def installed_models(root: str, get: Callable = _get) -> Optional[List[str]]:
    """The model names an Ollama server at `root` has pulled; None when it does not answer."""
    data, error = _attempt(get, f"{root}/api/tags")
    return None if error else [m.get("name", "") for m in data.get("models", [])]


def has_model(installed: List[str], wanted: str) -> bool:
    return any(name == wanted or name == f"{wanted}:latest" for name in installed)


def _resolve(config: Optional[dict]) -> dict:
    from engine.presets import BoneConfig
    from mechanics.providers import environment_config

    config = dict(config) if config is not None else {}
    resolved, error = _attempt(environment_config, config)  # BONE_PROVIDER set to a cloud provider with no BONE_MODEL
    if error:
        config["_env_error"] = str(error)
    else:
        config = resolved
    provider = str(config.get("provider") or getattr(BoneConfig, "PROVIDER", "ollama")).lower()
    defaults = getattr(BoneConfig, "DEFAULT_LLM_ENDPOINTS", {})
    return {
        "provider": provider,
        "model": config.get("model") or getattr(BoneConfig, "MODEL", "gemma4:12b"),
        "base_url": config.get("base_url") or defaults.get(provider, ""),
        "api_key": config.get("api_key", ""),
        "dspy_model": config.get("dspy_model") or getattr(BoneConfig, "DSPY_MODEL", "gemma4:e4b"),
        "env_error": config.get("_env_error", ""),
    }


def _embedding_settings() -> dict:
    from spores.embeddings import _DEFAULTS, _ENV_KEYS

    return {key: os.environ.get(env) or _DEFAULTS[key] for key, env in _ENV_KEYS.items() if key in _DEFAULTS}


def check_python() -> Check:
    have = ".".join(map(str, sys.version_info[:3]))
    if sys.version_info >= (3, 14):
        return Check("python", OK, have)
    return Check("python", WARN, f"{have}; 3.14 is the version this was built and tested on")


def check_packages(find_spec: Callable = importlib.util.find_spec) -> List[Check]:
    checks = []
    for module, fix in REQUIRED.items():
        found = find_spec(module) is not None
        checks.append(Check(f"package {module}", OK if found else FAIL, "" if found else "missing", "" if found else fix))
    for module, (package, what) in OPTIONAL.items():
        found = find_spec(module) is not None
        checks.append(Check(f"package {module}", OK if found else WARN, "" if found else f"missing: {what} is off",
                            "" if found else f"pip install -r requirements.txt   ({package})"))
    return checks


def check_config(path: Path) -> Check:
    if not path.exists():
        return Check("config.json", INFO, "none yet: the first run asks a few setup questions and writes it")
    _, error = _attempt(lambda: json.loads(path.read_text(encoding="utf-8")))
    if error:
        return Check("config.json", FAIL, f"unreadable ({error})", "delete it and run `python main.py` to set up again")
    return Check("config.json", OK, str(path))


def check_folders(root: Path) -> List[Check]:
    checks = []
    for name in ("saves", "logs", "notes"):
        target = root / name
        probe = target if target.exists() else root
        writable = os.access(probe, os.W_OK)
        checks.append(Check(f"folder {name}/", OK if writable else FAIL, "" if writable else f"{probe} is not writable",
                            "" if writable else f"chmod u+w {probe}"))
    return checks


def check_chat(settings: dict, get: Callable, post: Callable) -> List[Check]:
    provider, model, root = settings["provider"], settings["model"], server_root(settings["base_url"])
    if settings["env_error"]:
        return [Check("chat model", FAIL, settings["env_error"], "export BONE_MODEL=<a model your key can use>")]
    if provider == "mock":
        return [Check("chat model", INFO, "mock provider: canned replies, no model needed")]
    if provider in ("openai", "xai", "anthropic"):
        from mechanics.providers import KEY_ENV

        key = os.environ.get(KEY_ENV.get(provider, "OPENAI_API_KEY"), "") or settings["api_key"]
        has_key = bool(key) and key != "ollama"
        detail = f"{provider} {model}; no request made (it would cost); `python tools/live_run.py --provider {provider}` is the smoke run"
        return [Check("chat model", OK if has_key else FAIL, detail if has_key else f"{provider} needs an API key",
                      "" if has_key else f"export {KEY_ENV.get(provider, 'OPENAI_API_KEY')}=...")]
    checks: List[Check] = []
    if provider == "lm_studio":
        data, error = _attempt(get, f"{root}/v1/models")
        models = [] if error else [m.get("id", "") for m in data.get("data", [])]
        if error:
            return [Check("chat model", FAIL, f"LM Studio does not answer at {root}", "start LM Studio's local server and load a model")]
        checks.append(Check("chat server", OK if models else FAIL, f"LM Studio at {root}: {len(models)} model(s) loaded",
                            "" if models else "load a model in LM Studio"))
        return checks
    models = installed_models(root, get)
    if models is None:
        return [Check("chat server", FAIL, f"Ollama does not answer at {root}", "ollama serve   (install: https://ollama.com)")]
    checks.append(Check("chat server", OK, f"Ollama at {root}: {len(models)} model(s) pulled"))
    if not has_model(models, model):
        return checks + [Check("chat model", FAIL, f"{model} is not pulled", f"ollama pull {model}")]
    started = time.time()
    answer, error = _attempt(post, f"{root}/api/chat", {"model": model, "stream": False, "think": False, "options": {"num_predict": 8},
                                                        "messages": [{"role": "user", "content": "Reply with the single word: ok"}]}, None, 120.0)
    said = "" if error else str(answer.get("message", {}).get("content", "")).strip()
    if error:
        return checks + [Check("chat model", FAIL, f"{model} did not answer ({type(error).__name__}: {error})",
                               "check `ollama ps`; a model larger than your VRAM can time out on first load")]
    seconds = time.time() - started
    status = OK if said else WARN
    detail = f"{model} answered in {seconds:.1f}s" if said else f"{model} answered with nothing"
    checks.append(Check("chat model", status, detail, "" if said else "try another model; see docs/TESTING.md, local models"))
    wanted = settings["dspy_model"]
    if not has_model(models, wanted):
        checks.append(Check("critic model", WARN, f"{wanted} is not pulled: the reply critic's calls fail each turn and are skipped",
                            f"ollama pull {wanted}   (or set \"dspy_model\" in config.json to a model you have)"))
    else:
        checks.append(Check("critic model", OK, wanted))
    return checks


def check_embeddings(settings: dict, get: Callable, post: Callable) -> Check:
    emb = _embedding_settings()
    if str(emb.get("BACKEND", "auto")).lower() == "hash":
        return Check("embeddings", INFO, "hash backend chosen: memory runs on hash coordinates, associative recall is off")
    url, model = emb["URL"], emb["MODEL"]
    consequence = "memory runs on hash coordinates and associative recall is off until it is fixed"
    root = server_root(url)
    models = installed_models(root, get) if "11434" in url else None
    if models is not None and not has_model(models, model):
        return Check("embeddings", WARN, f"{model} is not pulled: {consequence}", f"ollama pull {model}")
    answer, error = _attempt(post, url, {"model": model, "input": PROBE_TEXT}, {"Authorization": f"Bearer {emb.get('API_KEY', 'ollama')}"}, 15.0)
    size, error = _attempt(lambda: len(answer["data"][0]["embedding"])) if not error else (None, error)
    if error:
        return Check("embeddings", WARN, f"no embedding answer from {url}: {consequence}",
                     f"ollama pull {model}   (or set BONE_EMBED_URL and BONE_EMBED_MODEL to a server you run)")
    return Check("embeddings", OK, f"{model}, {size} dimensions")


def run_doctor(config: Optional[dict] = None, root: Optional[Path] = None, get: Callable = _get, post: Callable = _post,
               find_spec: Callable = importlib.util.find_spec) -> List[Check]:
    root = Path(root or ".")
    if config is None:
        path = root / "config.json"
        config, error = _attempt(lambda: json.loads(path.read_text(encoding="utf-8")) if path.exists() else {})
        config = {} if error else config
    settings = _resolve(config)
    checks = [check_python(), *check_packages(find_spec), check_config(root / "config.json"), *check_folders(root)]
    checks += check_chat(settings, get, post)
    if settings["provider"] != "mock":
        checks.append(check_embeddings(settings, get, post))
    return checks


def render(checks: List[Check]) -> str:
    lines = []
    for c in checks:
        lines.append(f"[{c.status:>4}] {c.name}" + (f": {c.detail}" if c.detail else ""))
        if c.fix:
            lines.append(f"       fix: {c.fix}")
    failed = sum(c.status == FAIL for c in checks)
    warned = sum(c.status == WARN for c in checks)
    lines.append("")
    lines.append("Ready." if not failed and not warned else
                 f"Ready to run, with {warned} thing(s) worse than they could be." if not failed else
                 f"Not ready: {failed} thing(s) to fix first.")
    return "\n".join(lines)


def main() -> int:
    checks = run_doctor()
    print(render(checks))
    return 1 if any(c.status == FAIL for c in checks) else 0
