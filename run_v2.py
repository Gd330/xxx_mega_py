import os
import time
import re
import base64
import cv2
import numpy as np
import pytesseract
import pyautogui
import logging
import socket
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

import ctypes
import win32gui
import win32con
import win32api

# 初始化 Flask 应用并配置 CORS
app = Flask(__name__)
CORS(app)

# 日志目录与配置：同时写入日志文件和控制台
if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/app.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

@app.before_request
def log_request_info():
    logging.info("收到请求: %s %s, 参数: %s", request.method, request.path, dict(request.args))

def get_pc_name():
    """获取当前计算机的名称"""
    return socket.gethostname()

def simulate_keypress(key='f7'):
    """
    模拟按下指定的键盘按键（默认 F7）
    同时在控制台打印和写入日志
    """
    message = f"Simulating pressing the '{key}' key..."
    print(message)
    logging.info("模拟按键: %s", key)
    pyautogui.press(key)
    message2 = f"Key '{key}' pressed."
    print(message2)
    logging.info("按键 '%s' 执行完毕。", key)

def get_ip_addresses():
    """获取本机所有 IP 地址"""
    host_name = socket.gethostname()
    try:
        host_ips = socket.gethostbyname_ex(host_name)[2]
    except socket.error:
        host_ips = ['127.0.0.1']
    return host_ips

def get_client_ip():
    """
    从本机所有 IP 中选择一个符合 192.168.0.x 或 192.168.1.x 且不是 192.168.0.254 的 IP
    """
    ips = get_ip_addresses()
    for ip in ips:
        if (ip.startswith("192.168.0.") or ip.startswith("192.168.1.")) and ip != "192.168.0.254":
            return ip
    return None

def ocr_extract_amount(image):
    """
    对传入图像进行预处理和 OCR, 提取金额数字
    """
    logging.info("开始 OCR 处理图像...")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    alpha = 2.0  # 对比度因子
    beta = 0     # 亮度因子
    processed = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
    custom_config = r'--oem 3 --psm 7'
    text = pytesseract.image_to_string(processed, config=custom_config)
    found = re.findall(r'\d+\.?\d*', text)
    amount = found[0] if found else None
    logging.info("OCR 结果: %s, 提取金额: %s", text, amount)
    return amount, processed

def screenshot_extract_amount(rois, ld_index):
    """
    截屏一次，并对截图按照传入的 ROIs 进行 OCR 提取金额，
    将全屏截图及各 ROI 的处理结果保存并返回。
    截图文件名根据 ld_index 来命名，如 screenshot_ldplayer_1.png
    """
    folder = "screenshots"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    logging.info("开始截屏...")
    screenshot = pyautogui.screenshot()
    # 使用 ld_index 构造截图文件名
    filename = os.path.join(folder, f"screenshot_ldplayer_{ld_index}.png")
    screenshot.save(filename)
    logging.info("已保存截图到 %s", filename)
    
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    roi_results = []
    for roi in rois:
        try:
            x1, y1, x2, y2 = map(int, roi)
        except Exception as e:
            logging.error("无效 ROI 格式: %s, 错误: %s", roi, str(e))
            roi_results.append({
                "amount": None,
                "roi_img": None,
                "error": "Invalid ROI format"
            })
            continue
        
        roi_img = screenshot_cv[y1:y2, x1:x2]
        if roi_img.size == 0:
            logging.error("ROI 区域为空: %s", roi)
            roi_results.append({
                "amount": None,
                "roi_img": None,
                "error": "Empty ROI"
            })
            continue
        
        amount, processed_img = ocr_extract_amount(roi_img)
        _, buffer = cv2.imencode('.png', processed_img)
        roi_base64 = base64.b64encode(buffer).decode('utf-8')
        roi_results.append({
            "amount": amount,
            "roi_img": roi_base64
        })
    
    _, full_buffer = cv2.imencode('.png', screenshot_cv)
    full_b64 = base64.b64encode(full_buffer).decode('utf-8')
    
    result = {
        "full_screenshot": "full_b64",
        "roi_results": roi_results
    }
    logging.info("截屏处理完成。")
    return result

def find_ldplayer_windows(title_keyword="O-"):
    """
    查找所有标题中包含 title_keyword 的 LDPlayer 窗口，
    并按窗口标题按字母顺序排序后返回。
    """
    def enum_handler(hwnd, result_list):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_keyword.lower() in title.lower():
                result_list.append((hwnd, title))
    windows = []
    win32gui.EnumWindows(enum_handler, windows)
    sorted_windows = sorted(windows, key=lambda x: x[1])
    return sorted_windows

def activate_window(hwnd):
    """
    还原并激活指定窗口：
      1. 使用 AllowSetForegroundWindow 允许所有进程设置前台窗口；
      2. 尝试将目标窗口置前；
      3. 如果失败，模拟一次用户输入后重新尝试。
    """
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    ctypes.windll.user32.AllowSetForegroundWindow(-1)
    
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print("第一次 SetForegroundWindow 错误:", e)
        win32api.keybd_event(0, 0, 0, 0)
        win32api.keybd_event(0, 0, win32con.KEYEVENTF_KEYUP, 0)
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e2:
            print("第二次 SetForegroundWindow 错误:", e2)
    time.sleep(0.5)

def press_f11():
    """
    使用 keybd_event 模拟 F11 按键操作。
    """
    win32api.keybd_event(0x7A, 0, 0, 0)  # F11 key down
    time.sleep(0.1)
    win32api.keybd_event(0x7A, 0, win32con.KEYEVENTF_KEYUP, 0)  # F11 key up

# 定义路由

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
    用于测试连接的接口，只返回连接成功的响应
    """
    return "Connected", 200

@app.route('/run_extract_amount', methods=['POST'])
def run_extract_amount():
    """
    接收到 /run_extract_amount 请求后：
      1. 根据请求中的 ROIs 参数进行截屏及 OCR 处理，
      2. 对每个 LDPlayer 窗口进行激活、F11 最大化、截屏，
         并将截图结果返回给前端。
    """
    data = request.get_json() or {}
    rois = data.get("rois", [])
    logging.info(" /run_extract_amount 请求参数: rois=%s", rois)

    ldplayer_windows = find_ldplayer_windows("O-")

    screenshots_data = []  # 用于保存每个 LDPlayer 的截图结果

    for idx, (hwnd, title) in enumerate(ldplayer_windows, start=1):
        print(f"处理第 {idx} 个 LDPlayer 窗口，标题：{title}, 句柄：{hwnd}")
        activate_window(hwnd)
        time.sleep(1)
        press_f11()
        # 调用时传入当前窗口的序号，用以命名截图
        roi_results = screenshot_extract_amount(rois, idx)
        logging.info("当前窗口处理完成。")
        time.sleep(2)
        press_f11()  # 取消最大化状态

        screenshots_data.append({
            "iteration": idx,
            "full_screenshot": "",
            "window_title": title,
            "roi_results": roi_results
        })

    logging.info("/run_extract_amount 请求处理完成。")
    return jsonify({"status": "ok", "screenshots": screenshots_data})

@app.route('/capture', methods=['GET'])
def capture():
    """
    单次截屏接口：直接捕获当前屏幕，并返回 base64 编码的 PNG 图像，
    供前端预览截图使用。
    """
    logging.info("收到 /capture 请求。")
    try:
        screenshot = pyautogui.screenshot()
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.png', screenshot_cv)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        logging.info("/capture 请求处理成功。")
        return jsonify({'image': img_base64})
    except Exception as e:
        logging.error("/capture 截屏失败: %s", str(e))
        return jsonify({'error': f'截屏失败: {str(e)}'}), 500

if __name__ == "__main__":
    # 尝试自动发送本机 IP 和 PC 名称到主机服务器
    client_ip = get_client_ip()
    pc_name = get_pc_name()
    if client_ip:
        try:
            url = "http://192.168.0.254:5000/api/ips"
            payload = {"ip": client_ip, "pc_name": pc_name}
            response = requests.post(url, json=payload, timeout=2)
            if response.status_code != 200:
                print("\033[91m错误:发送IP和PC名称到主机失败,状态码:{}\033[0m".format(response.status_code))
        except Exception as e:
            print("\033[91m错误:发送IP和PC名称到主机失败:{}\033[0m".format(e))
    else:
        print("\033[91m错误:未找到符合条件的本机 IP。\033[0m")
    
    print("当前 PC 名称：", pc_name)
    print("Starting Flask server. Switch to the target application if needed.")
    
    ips = get_ip_addresses()
    print("Server is available on the following IP addresses:")
    for ip in ips:
        print(f" - {ip}:5000")
    
    app.run(host="0.0.0.0", port=5000)
