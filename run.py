import pyautogui
import time
from flask import Flask, request

app = Flask(__name__)

def simulate_keypress():
    """
    Simulates pressing the 'F' key on the keyboard.
    """
    print("Simulating pressing the 'F' key...")
    pyautogui.press('f')
    print("Key 'F' pressed.")

@app.route('/run', methods=['POST'])
def run_script():
    """
    Endpoint to trigger the keypress simulation.
    """
    simulate_keypress()
    return "Script executed on server", 200

if __name__ == "__main__":
    # Delay to give the user time to focus on the target application
    print("Starting Flask server. Switch to the target application if needed.")
    app.run(host="0.0.0.0", port=5000)
