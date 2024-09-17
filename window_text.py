import win32gui

def get_telegram_window_text(hwnd):
    class_name = win32gui.GetClassName(hwnd)
    if class_name == "Qt51513QWindow":
        window_text = win32gui.GetWindowText(hwnd)
        return window_text
    return None

def enum_telegram_windows():
    result = []
    def callback(hwnd, _):
        if get_telegram_window_text(hwnd):
            result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    return result

# Usage
telegram_windows = enum_telegram_windows()
for window in telegram_windows:
    text = get_telegram_window_text(window)
    print(f"Window text: {text}")
