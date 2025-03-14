import pyautogui
import time
import socket
import requests
from flask import Flask, request

app = Flask(__name__)

def simulate_keypress(key='f7'):
    """
    模拟按下指定的键盘按键（默认 F7）
    """
    print(f"Simulating pressing the '{key}' key...")
    pyautogui.press(key)
    print(f"Key '{key}' pressed.")

@app.route('/run', methods=['POST'])
def run_script():
    """
    从请求中获取按键参数，并触发按键模拟
    """
    data = request.get_json() or {}
    key = data.get("key", "f7")
    simulate_keypress(key)
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
        host_ips = socket.gethostbyname_ex(host_name)[2]
    except socket.error:
        host_ips = ['127.0.0.1']
    return host_ips

def get_client_ip():
    """
    从本机所有 IP 中选择一个符合 192.168.0.x 且不是 192.168.0.254 的 IP
    """
    ips = get_ip_addresses()
    for ip in ips:
        if ip.startswith("192.168.0.") and ip != "192.168.0.254":
            return ip
    return None

if __name__ == "__main__":
    # 尝试自动发送本机 IP 到主机服务器
    client_ip = get_client_ip()
    if client_ip:
        try:
            url = "http://192.168.0.254:5000/api/ips"
            response = requests.post(url, json={"ip": client_ip}, timeout=2)
            if response.status_code != 200:
                print("\033[91m错误：发送IP到主机失败，状态码：{}\033[0m".format(response.status_code))
        except Exception as e:
            print("\033[91m错误：发送IP到主机失败：{}\033[0m".format(e))
    else:
        print("\033[91m错误：未找到符合条件的本机 IP。\033[0m")
    
    print("Starting Flask server. Switch to the target application if needed.")
    
    # 打印所有本机 IP 地址
    ips = get_ip_addresses()
    print("Server is available on the following IP addresses:")
    for ip in ips:
        print(f" - {ip}:5000")
    
    app.run(host="0.0.0.0", port=5000)
