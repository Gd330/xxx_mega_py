import pyautogui
import time
from flask import Flask, request, jsonify
import cv2
import pytesseract
import numpy as np
import base64
import re

app = Flask(__name__)

# 默认的 ROI 坐标（格式：[x1, y1, x2, y2]），可根据需要调整
DEFAULT_ROIS = [
    [100, 100, 300, 150]  # 示例 ROI 坐标，请根据实际情况修改
]

def ocr_extract_amount(image):
    """
    对传入图像进行预处理和 OCR，提取金额数字
    """
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 增强对比度
    alpha = 2.0  # 对比度因子
    beta = 0     # 亮度因子
    processed = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
    # 使用 pytesseract 进行 OCR 识别
    custom_config = r'--oem 3 --psm 7'
    text = pytesseract.image_to_string(processed, config=custom_config)
    # 提取数字（可能包含小数点）
    found = re.findall(r'\d+\.?\d*', text)
    amount = found[0] if found else None
    return amount, processed

@app.route('/process', methods=['POST'])
def process_request():
    """
    接收主机请求，执行以下步骤：
      1. 接收需要模拟的按键（默认 f7）
      2. 触发该按键
      3. 模拟 shudaxia 录制的操作（最大化当前 LD Player）
      4. 等待 2 秒
      5. 截图当前屏幕
      6. 根据默认或传入 ROI 坐标进行 OCR 提取金额
      7. 将每个 ROI 内的金额和处理后的 ROI 图像存入数组
      8. 返回结果给主机
    """
    data = request.get_json() or {}
    key_to_press = data.get("key", "f7")
    rois = data.get("rois", DEFAULT_ROIS)
    
    # Step 2：触发指定按键
    print(f"Simulating key press: {key_to_press}")
    pyautogui.press(key_to_press)
    
    # Step 3：模拟 shudaxia 录制的操作，最大化当前 LD Player 窗口（这里使用 Windows 快捷键 'win+up'）
    print("Maximizing current window...")
    pyautogui.hotkey('win', 'up')
    
    # Step 4：等待 2 秒
    time.sleep(2)
    
    # Step 5：截图当前屏幕，并转换为 OpenCV 格式
    screenshot = pyautogui.screenshot()
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Step 6 & 7：对每个 ROI 进行 OCR 识别，存储金额和 ROI 图像（base64 编码）
    results = []
    for roi in rois:
        x1, y1, x2, y2 = map(int, roi)
        roi_img = screenshot_cv[y1:y2, x1:x2]
        if roi_img.size == 0:
            results.append({
                "amount": None,
                "roi_img": None,
                "error": "Empty ROI"
            })
            continue
        amount, processed_img = ocr_extract_amount(roi_img)
        # 将处理后的 ROI 图像编码为 base64
        _, buffer = cv2.imencode('.png', processed_img)
        roi_base64 = base64.b64encode(buffer).decode('utf-8')
        results.append({
            "amount": amount,
            "roi_img": roi_base64
        })
    
    # Step 8：返回结果给主机
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
