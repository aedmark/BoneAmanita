from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from lichen.engine import LichenEngine

app = FastAPI(title="Lichen Adventure API")

# Initialize Engine globally for the session
engine = LichenEngine()

# Setup static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    message = request.message
    response_text = engine.process_input(message)
    
    # Gather state to send back to the UI
    room = None
    if engine.cartographer.current_room:
        r = engine.cartographer.get_room(engine.cartographer.current_room)
        if r:
            room = {
                "name": r.name,
                "description": r.description,
                "pois": r.points_of_interest,
                "exits": list(r.exits.keys())
            }
            
    vitals = {
        "stamina": engine.physics.energy.stamina,
        "dopamine": engine.physics.energy.dopamine,
        "cortisol": engine.physics.energy.cortisol,
        "drag": engine.physics.space.narrative_drag
    }
    
    inventory = engine.inventory.list_items()
    
    return {
        "response": response_text,
        "room": room,
        "vitals": vitals,
        "inventory": inventory,
        "max_slots": engine.inventory.max_slots
    }

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open(os.path.join(static_dir, "index.html"), "r") as f:
        return f.read()

