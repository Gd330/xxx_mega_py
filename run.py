import pyautogui
import time
import socket
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

def get_ip_addresses():
    """
    获取本机所有 IP 地址
    """
    host_name = socket.gethostname()
    try:
        # 获取所有与主机名关联的 IP 地址
        host_ips = socket.gethostbyname_ex(host_name)[2]
    except socket.error:
        host_ips = ['127.0.0.1']
    return host_ips

if __name__ == "__main__":
    # 延时让用户有时间切换到目标应用
    print("Starting Flask server. Switch to the target application if needed.")
    
    # 打印所有本机 IP 地址
    ips = get_ip_addresses()
    print("Server is available on the following IP addresses:")
    for ip in ips:
        print(f" - {ip}:5000")
    
    app.run(host="0.0.0.0", port=5000)
