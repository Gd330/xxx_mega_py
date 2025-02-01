from flask import Flask, jsonify, request, send_from_directory
import os
import requests

app = Flask(__name__)

# 用于存储目标 IP 地址的列表
ip_list = []

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
    发送 POST 请求到指定 IP，带超时和错误处理
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
    发送 POST 请求到指定 IP
    """
    result = send_post_request(ip)
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/send_all', methods=['POST'])
def send_request_all():
    """
    向所有 IP 地址发送 POST 请求
    """
    results = [send_post_request(ip) for ip in ip_list]
    print(results)  # 打印详细结果到控制台
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
