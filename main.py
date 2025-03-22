import pygetwindow as gw

# 根据窗口标题获取 LD Player 窗口对象（请确保窗口标题包含 "LDPlayer"）
ld_windows = gw.getWindowsWithTitle('LDPlayer')
if ld_windows:
    ld_window = ld_windows[0]
    ld_window.maximize()
    print("LD Player 已最大化")
else:
    print("未找到 LD Player 窗口")