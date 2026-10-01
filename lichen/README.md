# Lichen

A spatial presentation layer extracted from the BoneAmanita framework. Lichen provides the "gamified" elements—inventory management, slash command processing, and cartographic room-mapping—that wrap the pure biological engine (Mycelium) in an interactive Text Adventure / MUD presentation.

## Core Components
- **`inventory.py`**: The `GordonKnot` inventory management system.
- **`commands.py`**: The `CommandProcessor` parsing UI slash commands (`/look`, `/drop`, `/inventory`).
- **`cartographer.py`**: The spatial mapping engine mapping discrete rooms to nodes in the Halcyon graph.
