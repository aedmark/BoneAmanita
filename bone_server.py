import json
import os
import time
import shutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, PlainTextResponse

from bone_main import ConfigWizard, BoneAmanita
from bone_cycle import GeodesicOrchestrator
from bone_core import TelemetryService, LoreManifest, BoneJSONEncoder

app = FastAPI()
app.state.reset_triggered = False

# 1. Initialize the Core Engine once at startup
sys_config = ConfigWizard.load_or_create()
engine = BoneAmanita(config=sys_config)
orchestrator = GeodesicOrchestrator(engine)

def sanitize_payload(obj):
    if isinstance(obj, dict):
        return {str(k): sanitize_payload(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [sanitize_payload(v) for v in obj]
    elif hasattr(obj, "to_dict"):
        return sanitize_payload(obj.to_dict())
    elif hasattr(obj, "__dict__"):
        return sanitize_payload(obj.__dict__)
    return obj

def strip_hud(text: str) -> str:
    """Surgically removes the ASCII dashboard artifacts from the boot sequence."""
    if not text:
        return text
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        if any(m in line for m in ["♦", "🧊", "📍", "HP ", "STM ", "────────────────", "ATP:", "THE OBSERVER"]):
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines).strip()

def inject_metrics(snapshot: dict):
    """Guarantees the frontend always receives the core systemic vitals."""
    metrics = engine.get_metrics()
    snapshot["metrics"] = metrics
    if hasattr(engine, "bio") and engine.bio and hasattr(engine.bio, "mito"):
        snapshot["metrics"]["ros"] = engine.bio.mito.state.ros_buildup
    else:
        snapshot["metrics"]["ros"] = 0.0

@app.get("/")
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    app.state.reset_triggered = False # Reset the flag on new connection

    try:
        # --- THE FIX: Wrap the boot sequence in the try block ---
        if engine.tick_count == 0:
            boot_packet = engine.engage_cold_boot()
            if boot_packet:
                if "ui" in boot_packet:
                    boot_packet["ui"] = strip_hud(boot_packet["ui"])
                inject_metrics(boot_packet)
                clean_boot = sanitize_payload(boot_packet)
                # If the browser timed out while waiting for this, it will throw here.
                await websocket.send_text(json.dumps(clean_boot, cls=BoneJSONEncoder))

        # --- The Main Loop ---
        while True:
            user_message = await websocket.receive_text()
            snapshot = engine.process_turn(user_message)
            inject_metrics(snapshot)

            clean_snapshot = sanitize_payload(snapshot)
            await websocket.send_text(json.dumps(clean_snapshot, cls=BoneJSONEncoder))

    # --- Catch ALL disconnects gracefully ---
    except WebSocketDisconnect:
        print("[SERVER] Client disconnected.")
        if not getattr(app.state, "reset_triggered", False):
            print("[SERVER] Saving state...")
            engine.save_checkpoint()
        else:
            print("[SERVER] Reset was triggered. Skipping save to preserve purged state.")

@app.get("/api/reset")
async def factory_reset():
    app.state.reset_triggered = True

    if os.path.exists("__pycache__"):
        shutil.rmtree("__pycache__")
    if os.path.exists("logs"):
        shutil.rmtree("logs")
    if os.path.exists("memories"):
        shutil.rmtree("memories")
    if os.path.exists("saves"):
        shutil.rmtree("saves")
    if os.path.exists("bone_config.json"):
        os.rename("bone_config.json", f"bone_config.json.{int(time.time())}.bak")

    LoreManifest.get_instance().flush_cache()
    return {"status": "success", "message": "System purged. Restart server to re-initialize."}

@app.get("/api/export_transcript")
async def export_transcript():
    telemetry = TelemetryService.get_instance()
    history = telemetry.read_recent_history(limit=50)

    if not history:
        return PlainTextResponse(content="No transcript available. Talk to the lattice first.", media_type="text/plain")

    transcript = "\n\n".join(history)
    return PlainTextResponse(content=transcript, media_type="text/plain")