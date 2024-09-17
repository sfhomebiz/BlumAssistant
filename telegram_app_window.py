import win32gui


def get_detailed_window_info(hwnd):
    text = win32gui.GetWindowText(hwnd)
    rect = win32gui.GetWindowRect(hwnd)
    client_rect = win32gui.GetClientRect(hwnd)
    monitor = get_client_monitor_area(hwnd, client_rect)
    child_texts = []

    def enum_child_callback(child_hwnd, _):
        child_text = win32gui.GetWindowText(child_hwnd)
        if child_text:
            child_texts.append(child_text)

    win32gui.EnumChildWindows(hwnd, enum_child_callback, None)

    return {
        "hwnd": hwnd,
        "text": text,
        "rect": rect,
        "client_rect": client_rect,
        "monitor": monitor,
        "child_texts": child_texts
    }


def enum_telegram_windows():
    result = []

    def callback(hwnd, _):
        w_name = str(win32gui.GetClassName(hwnd))
        if w_name.__contains__("Qt5") and w_name.__contains__("QWindow") and not w_name.__contains__("QWindowIcon"):
            result.append(get_detailed_window_info(hwnd))
        # if win32gui.GetClassName(hwnd) == "Qt51513QWindow":
        #     result.append(get_detailed_window_info(hwnd))
        # QWindowIcon - opened Telegram group, QWindowToolSaveBits - Telegram alert small window

    win32gui.EnumWindows(callback, None)
    return result


def get_client_monitor_area(hwnd: int, client_rect: tuple):
    client_left, client_top, client_right, client_bottom = client_rect

    side_border = 25
    top_border = 70
    bottom_border = 123
    screen_top_left = win32gui.ClientToScreen(hwnd, (client_left, client_top))
    screen_right_bottom = win32gui.ClientToScreen(hwnd, (client_right, client_bottom))

    client_left = screen_top_left[0] + side_border
    client_top = screen_top_left[1] + top_border
    client_right = screen_right_bottom[0] - side_border
    client_bottom = screen_right_bottom[1] - bottom_border

    # Create a monitor dictionary with the client area coordinates
    monitor = {
        'left': client_left,
        'top': client_top,
        'width': client_right - client_left,
        'height': client_bottom - client_top
    }
    return monitor


def get_blum_window(child_text: str) -> dict:
    telegram_windows = enum_telegram_windows()
    for i, window in enumerate(telegram_windows):
        if str(window['child_texts']).__contains__(child_text):
            return window
    return None

# Usage
# telegram_windows = enum_telegram_windows()
# for i, window in enumerate(telegram_windows):
#     print(f"Window {i+1}:")
#     print(f"  Text: {window['text']}")
#     print(f"  Rect: {window['rect']}")
#     print(f"  Client Rect: {window['client_rect']}")
#     print(f"  Monitor: {window['monitor']}")
#     print(f"  Child texts: {window['child_texts']}")
#     print()
