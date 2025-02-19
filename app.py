from flask import Flask, jsonify, request, send_from_directory
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# 用于存储目标 IP 地址的列表，并添加默认 IP 地址
ip_list = [
    "192.168.1.28", 
    "192.168.1.26", 
    "192.168.1.22", 
    "192.168.1.38", 
    "192.168.1.40", 
    "192.168.1.67"
    ]

@app.route('/')
def index():
    """
    提供前端页面
    """
    return send_from_directory(os.path.dirname(__file__), 'index.html')

@app.route('/api/ips', methods=['GET'])
def get_ips():
    """
    获取当前所有 IP 地址
    """
    return jsonify(ip_list)

@app.route('/api/ips', methods=['POST'])
def add_ip():
    """
    添加 IP 地址
    """
    data = request.get_json()
    new_ip = data.get('ip')
    if new_ip and new_ip not in ip_list:
        ip_list.append(new_ip)
    return jsonify({"status": "success", "ips": ip_list})

@app.route('/api/ips/<ip>', methods=['DELETE'])
def delete_ip(ip):
    """
    删除指定 IP 地址
    """
    if ip in ip_list:
        ip_list.remove(ip)
    return jsonify({"status": "success", "ips": ip_list})

def send_post_request(ip):
    """
    发送 POST 请求到指定 IP 的 /run 接口，带超时和错误处理
    """
    try:
        response = requests.post(f'http://{ip}:5000/run', timeout=1)
        return {"ip": ip, "status": "success", "response": response.text}
    except requests.exceptions.Timeout:
        return {"ip": ip, "status": "error", "message": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"ip": ip, "status": "error", "message": "Connection error"}
    except requests.exceptions.RequestException as e:
        return {"ip": ip, "status": "error", "message": f"Unexpected error: {str(e)}"}

@app.route('/api/send/<ip>', methods=['POST'])
def send_request(ip):
    """
    发送 POST 请求到指定 IP 的 /run 接口
    """
    result = send_post_request(ip)
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/send_all', methods=['POST'])
def send_request_all():
    """
    向所有 IP 地址发送 POST 请求到 /run 接口，使用并发方式
    """
    results = []
    # 这里设置最大并发线程数，根据实际情况调整
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ip = {executor.submit(send_post_request, ip): ip for ip in ip_list}
        for future in as_completed(future_to_ip):
            result = future.result()
            results.append(result)
    print(results)  # 打印详细结果到控制台
    return jsonify(results)

# ----------------------- 新增测试连接功能 -----------------------

def send_test_request(ip):
    """
    发送 GET 请求到指定 IP 的 /test 接口，用于测试连接
    """
    try:
        response = requests.get(f'http://{ip}:5000/test', timeout=1)
        return {"ip": ip, "status": "success", "response": response.text}
    except requests.exceptions.Timeout:
        return {"ip": ip, "status": "error", "message": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"ip": ip, "status": "error", "message": "Connection error"}
    except requests.exceptions.RequestException as e:
        return {"ip": ip, "status": "error", "message": f"Unexpected error: {str(e)}"}

@app.route('/api/test/<ip>', methods=['GET'])
def test_request(ip):
    """
    测试指定 IP 的连接
    """
    result = send_test_request(ip)
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/test_all', methods=['GET'])
def test_request_all():
    """
    测试所有 IP 地址的连接
    """
    results = [send_test_request(ip) for ip in ip_list]
    print(results)
    return jsonify(results)

# ----------------------- 结束新增 -----------------------

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
