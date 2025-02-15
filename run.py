import pyautogui
import time
from flask import Flask, request

app = Flask(__name__)

def simulate_keypress():
    """
    模拟按下键盘上的 'F' 键
    """
    print("Simulating pressing the 'F' key...")
    pyautogui.press('f')
    print("Key 'F' pressed.")

@app.route('/run', methods=['POST'])
def run_script():
    """
    触发按键模拟
    """
    simulate_keypress()
    return "Script executed on server", 200

@app.route('/test', methods=['GET'])
def test_connection():
    """
    用于测试连接的接口，不会执行任何操作，只返回连接成功的响应
    """
    return "Connected", 200

if __name__ == "__main__":
    # 延时让用户有时间切换到目标应用
    print("Starting Flask server. Switch to the target application if needed.")
    app.run(host="0.0.0.0", port=5000)
