#!/bin/bash

echo "Igniting BoneAmanita Engine on Bare Metal..."

# 1. The Atmosphere Check (Virtual Environment)
if [ ! -d "venv" ]; then
    echo "Building local atmosphere (venv)..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 2. THE INITIATION GATE (The Fix)
# We run the ConfigWizard directly in the foreground terminal.
# This guarantees keyboard input works.
echo "Checking system configuration..."
python3 -c "from bone_main import ConfigWizard; ConfigWizard.load_or_create()"

# 3. The Background Thread (Browser Launch)
(
    sleep 3
    echo "Opening visual interface..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "http://localhost:8000"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "http://localhost:8000"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        start "http://localhost:8000"
    else
        python3 -m webbrowser "http://localhost:8000"
    fi
) &

# 4. The Main Thread (The Anchor)
# Now that the JSON config file is guaranteed to exist, Uvicorn will boot instantly without blocking.
uvicorn bone_server:app --reload