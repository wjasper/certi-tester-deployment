#!/bin/bash

# Determine script directory
SCRIPT_DIR="/Users/sunday/brainfuck/certi_testor_deployement"
URL="http://127.0.0.1:7784"

# AppleScript command to open a new Terminal window, activate it, and execute the script
CMD="
tell application \"Terminal\"
   do script \"cd $SCRIPT_DIR && source $SCRIPT_DIR/certi_testor_deployement_env/bin/activate && python3 app.py; exec bash\"
   activate
end tell
"

# Run the AppleScript command to execute the main script
osascript -e "$CMD"

# Delay in seconds before opening the URL
DELAY=2

# Function to open and refresh the browser
refresh_browser() {
    open "$URL"
    sleep "$DELAY"
    osascript -e '
        tell application "Safari"
            set URL of front document to "http://127.0.0.1:7784"
        end tell
    '
}

# Open and refresh the browser
refresh_browser
