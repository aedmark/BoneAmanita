""" bone_api.py """

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from bone_main import BoneAmanita, ConfigWizard
from bone_types import Prisma

import re

def parse_vsl_markdown(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text, flags=re.DOTALL)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text, flags=re.DOTALL)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text, flags=re.DOTALL)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<em>\1</em>', text, flags=re.DOTALL)
    text = re.sub(r'(?m)^[ \t]*[-*][ \t]+(.*)$', r'<li>\1</li>', text)
    text = re.sub(r'(?:<li>.*?</li>\n?)+', lambda m: f"<ul>\n{m.group(0)}</ul>\n", text)
    return text

class EngineState:
    engine: BoneAmanita = None
    active_connections: list[WebSocket] = []
state = EngineState()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    print("[API] Booting BoneAmanita Engine...")
    Prisma.enable_web_mode()
    sys_config = ConfigWizard.load_or_create()
    if "mode_settings" not in sys_config:
        sys_config["mode_settings"] = {}
    sys_config["mode_settings"]["render_target"] = "WEB"
    state.engine = BoneAmanita(config=sys_config)
    state.engine.events.flush()
    original_log = state.engine.events.log

    def websocket_log_hook(text: str, category: str = "SYS", persist: bool = True):
        original_log(text, category, persist)
        if state.active_connections:
            payload = json.dumps({"type": "EVENT_BUS", "category": category, "text": text})
            for connection in state.active_connections:
                asyncio.create_task(connection.send_text(payload))
    state.engine.events.log = websocket_log_hook
    print("[API] Engine Online. EventBus hooked to WebSockets.")
    yield
    print("[API] Shutting down Engine...")
    if state.engine:
        state.engine.shutdown()

def stringify_lattice_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {(str(k) if isinstance(k, tuple) else k): stringify_lattice_keys(v)for k, v in obj.items()}
    elif isinstance(obj, list):
        return [stringify_lattice_keys(item) for item in obj]
    else:
        return obj

app = FastAPI(lifespan=lifespan, title="BoneAmanita Hypervisor API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"], )

@app.get("/")
async def health_check():
    if not state.engine:
        return {"status": "OFFLINE"}
    metrics = state.engine.get_metrics()
    metrics["SLASH_gamma"] = state.engine.phys.observer.last_physics_packet.gamma if hasattr(state.engine, "phys") and state.engine.phys.observer.last_physics_packet else 0.0
    return {"status": "ONLINE", "tick": state.engine.tick_count, "metrics": metrics}

@app.websocket("/ws/lattice")
async def lattice_websocket(websocket: WebSocket):
    await websocket.accept()
    state.active_connections.append(websocket)
    try:
        if state.engine.tick_count == 0:
            boot_packet = state.engine.engage_cold_boot()
            if boot_packet:
                await websocket.send_json(stringify_lattice_keys(boot_packet))
        await websocket.send_json(stringify_lattice_keys({"type": "METRICS_UPDATE", "metrics": state.engine.get_metrics()}))
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_text = payload.get("text", "").strip()
            response_packet = state.engine.process_turn(user_text)
            if "ui" in response_packet:
                raw_ui = response_packet["ui"]
                if "────────────────" in raw_ui:
                    parts = raw_ui.rsplit("────────────────", 1)
                    dashboard = parts[0] + "────────────────"
                    narrative = parts[1]
                    clean_dash = f"<pre class='dashboard-terminal'>{dashboard.strip()}</pre>"
                    clean_narrative = parse_vsl_markdown(narrative.strip())
                    response_packet["ui"] = clean_dash + "\n\n" + clean_narrative
                else:
                    response_packet["ui"] = parse_vsl_markdown(raw_ui)
            await websocket.send_json(stringify_lattice_keys(response_packet))
            await websocket.send_json(stringify_lattice_keys({"type": "METRICS_UPDATE", "metrics": state.engine.get_metrics()}))
    except WebSocketDisconnect:
        state.active_connections.remove(websocket)
        print("[API] Client disconnected.")
    except Exception as e:
        print(f"[API] WebSocket Error: {e}")
        if websocket in state.active_connections:
            state.active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bone_api:app", host="127.0.0.1", port=8000, reload=True)