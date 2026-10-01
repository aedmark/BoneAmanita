# Lichen

Lichen is an independent extraction and rebuild of BoneAmanita's gamified Text Adventure mechanics. It provides the presentation layer—rooms, inventory, and spatial commands—that wraps around the pure biological logic (Mycelium).

## Core Modules
- **`inventory.py`**: Managing items and pockets.
- **`commands.py`**: Processing spatial interaction rules and `/commands`.
- **`cartographer.py`**: Mapping discrete spatial descriptions into navigable graph nodes.
