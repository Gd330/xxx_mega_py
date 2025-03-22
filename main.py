import pyautogui
import time
import cv2
import pytesseract
import numpy as np
import base64
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

# 默认的 ROI 坐标（格式：[x1, y1, x2, y2]），可根据实际情况修改
DEFAULT_ROIS = [
    [100, 100, 300, 150]  # 示例ROI坐标
]

def simulate_key_press(key):
    """
    模拟按键操作
    """
    print(f"Simulating key press: {key}")
    pyautogui.press(key)

def maximize_window():
    """
    模拟窗口最大化操作（使用 Windows 快捷键）
    """
    print("Maximizing current window...")
    pyautogui.hotkey('win', 'up')

def wait_for(seconds):
    """
    等待指定秒数
    """
    print(f"Waiting for {seconds} seconds...")
    time.sleep(seconds)

def take_screenshot():
    """
    截取屏幕截图，并转换为 OpenCV 格式
    """
    screenshot = pyautogui.screenshot()
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot_cv

def process_roi(screenshot_cv, roi):
    """
    对单个 ROI 进行 OCR 处理
    参数:
      - screenshot_cv: 截图图像（OpenCV 格式）
      - roi: ROI 坐标 [x1, y1, x2, y2]
    返回:
      - 字典: { "roi": roi, "amount": 金额, "roi_img": base64编码的图像, "error": 错误信息（如有） }
    """
    x1, y1, x2, y2 = map(int, roi)
    roi_img = screenshot_cv[y1:y2, x1:x2]
    if roi_img.size == 0:
        return {"roi": roi, "amount": None, "roi_img": None, "error": "Empty ROI"}
    
    # 图像预处理：转换为灰度、增强对比度
    gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
    alpha = 2.0  # 对比度因子
    beta = 0     # 亮度因子
    processed = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
    
    # OCR识别
    custom_config = r'--oem 3 --psm 7'
    text = pytesseract.image_to_string(processed, config=custom_config)
    found = re.findall(r'\d+\.?\d*', text)
    amount = found[0] if found else None
    
    # 将处理后的ROI图像编码为 base64
    _, buffer = cv2.imencode('.png', processed)
    roi_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {"roi": roi, "amount": amount, "roi_img": roi_base64}

def display_roi_preview(rois):
    """
    捕获一次屏幕截图，绘制 ROI 框，并显示预览窗口，
    便于在 VSCode 中调整和确认 ROI 位置。
    """
    print("Displaying ROI preview. 请检查ROI位置，按任意键关闭预览窗口。")
    screenshot_cv = take_screenshot()
    preview = screenshot_cv.copy()
    for roi in rois:
        x1, y1, x2, y2 = map(int, roi)
        cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imshow("ROI Preview", preview)
    cv2.waitKey(0)  # 等待按键
    cv2.destroyWindow("ROI Preview")

def process_iteration(key, rois):
    """
    处理单次迭代的所有步骤：
      1. 模拟按键
      2. 最大化窗口
      3. 等待2秒
      4. 截图
      5. 针对每个 ROI 进行 OCR 处理
    返回:
      - 字典: { "ocr_results": [每个ROI的处理结果] }
    """
    simulate_key_press(key)
    maximize_window()
    wait_for(2)
    screenshot_cv = take_screenshot()
    
    iteration_results = []
    for roi in rois:
        result = process_roi(screenshot_cv, roi)
        iteration_results.append(result)
    
    return {"ocr_results": iteration_results}

@app.route('/process_loop', methods=['POST'])
def process_loop():
    """
    执行循环处理：
      1. 接收参数：按键（默认 f7）、ROI 坐标、循环次数（默认24次）、是否显示ROI预览（show_rois）
      2. 如果 show_rois 为 True，则在循环前显示一次ROI预览窗口
      3. 根据循环次数逐次执行 process_iteration，并将结果存储
      4. 返回所有迭代结果给主机
    请求示例 JSON：
    {
        "key": "f7",
        "rois": [[100, 100, 300, 150], [350, 100, 550, 150]],
        "count": 24,
        "show_rois": true
    }
    """
    data = request.get_json() or {}
    key = data.get("key", "f7")
    rois = data.get("rois", DEFAULT_ROIS)
    count = data.get("count", 24)
    show_rois = data.get("show_rois", False)
    
    # 如果设置显示ROI预览，则先显示一次
    if show_rois:
        display_roi_preview(rois)
    
    results = []
    for i in range(count):
        print(f"Iteration {i+1} processing...")
        iteration_result = process_iteration(key, rois)
        iteration_result["iteration"] = i + 1
        results.append(iteration_result)
    
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
