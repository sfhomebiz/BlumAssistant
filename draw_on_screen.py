import ctypes
import win32gui
import win32con
import win32api
import win32ui
from win32api import GetSystemMetrics

dc = win32gui.GetDC(0)
dcObj = win32ui.CreateDCFromHandle(dc)
hwnd = win32gui.WindowFromPoint((0, 0))
monitor = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))


def pixel_is_out(pixel: tuple, rectangle: tuple) -> bool:
    if (pixel[0] < rectangle[0] or pixel[0] >= rectangle[0] + rectangle[2]
            or pixel[1] < rectangle[1] or pixel[1] >= rectangle[1] + rectangle[3]):
        return True
    else:
        return False


def color_int(r: int, g: int, b: int) -> int:
    return win32api.RGB(r, g, b)
    # return r << 16 | g << 8 | b


def draw_rectangle_v1(mx, my, width, height, color):
    # global past_coordinates
    # rect = win32gui.CreateRoundRectRgn(*past_coordinates, 2, 2)
    # win32gui.RedrawWindow(hwnd, past_coordinates, rect, win32con.RDW_INVALIDATE)
    global dcObj
    # Draw the rectangle
    if ctypes.windll.user32.DrawFocusRect is None:
        # Python 2.x
        dcObj.Rectangle((mx, my, mx + width, my + height), color)
    else:
        # Python 3.x
        ctypes.windll.user32.DrawFocusRect(dcObj.GetHandleAttrib(),
                                           ctypes.byref(ctypes.c_int(mx)),
                                           ctypes.byref(ctypes.c_int(my)),
                                           ctypes.byref(ctypes.c_int(mx + width)),
                                           ctypes.byref(ctypes.c_int(my + height)), color)

    return


def draw_rectangle(area: tuple, color: int, pen_width: int = 1):
    global dc
    # hwnd = win32gui.GetDesktopWindow()
    # dc = win32gui.GetWindowDC(hwnd)
    # brush = win32gui.CreateSolidBrush(color)
    # brush = win32gui.CreateHatchBrush(win32con.HS_SOLID, color)
    pen = win32gui.CreatePen(win32con.PS_SOLID, pen_width, color)
    win32gui.SelectObject(dc, pen)
    # win32gui.SelectObject(dc, brush)
    win32gui.MoveToEx(dc, area[0], area[1])
    win32gui.DrawFocusRect(dc, (area[0], area[1], area[0] + area[2], area[1] + area[3]))
    win32gui.FrameRect(dc, (area[0], area[1], area[0] + area[2], area[1] + area[3]), pen)
    # win32gui.LineTo(dc, area[0] + area[2], area[1])
    # win32gui.LineTo(dc, area[0] + area[2], area[1] + area[3])
    # win32gui.LineTo(dc, area[0], area[1] + area[3])
    # win32gui.LineTo(dc, area[0], area[1])

    # win32gui.DeleteObject(brush)
    win32gui.DeleteObject(pen)
    # win32gui.ReleaseDC(hwnd, dc)

        # win32gui.SetPixel(dc, mx + height, my + y, draw_color)
    # end = time.perf_counter()
    # print(f"DRAW CROSS time lapse {end - start:.6f}")
    # sleep(3.0)
    # coordinates = (mx-20, my-20, mx+20, my+20)


def draw_rectangle_v1(left, top, right, bottom, color):
    hwnd = win32gui.GetDesktopWindow()
    hdc = win32gui.GetWindowDC(hwnd)
    brush = win32gui.CreateSolidBrush(color)
    win32gui.SelectObject(hdc, brush)
    win32gui.Rectangle(hdc, left, top, right, bottom)
    win32gui.DeleteObject(brush)
    win32gui.ReleaseDC(hwnd, hdc)


def draw_transp_rectangle(left, top, right, bottom, color, border_width=2):
    hwnd = win32gui.GetDesktopWindow()
    hdc = win32gui.GetWindowDC(hwnd)

    # Create a pen with the desired color and width
    # brush = {'Style': win32con.BS_SOLID, 'Color': color, 'Hatch': win32con.HS_SOLID}
    brush = {'Style': win32con.BS_SOLID, 'Color': color, 'Hatch': win32con.HS_SOLID}
    pen = win32gui.ExtCreatePen(win32con.PS_GEOMETRIC, border_width, brush)
    # pen = win32gui.ExtCreatePen(win32con.PS_SOLID & win32con.PS_GEOMETRIC, border_width, brush)
    win32gui.SelectObject(hdc, pen)

    # Draw the rectangle with the pen
    win32gui.Rectangle(hdc, left, top, right, bottom)


def draw_cross(x, y, size, color):
    global dc
    # hwnd = win32gui.GetDesktopWindow()
    # hdc = win32gui.GetWindowDC(hwnd)
    pen = win32gui.CreatePen(win32con.PS_SOLID, 2, color)
    win32gui.SelectObject(dc, pen)
    half_size = size // 2
    win32gui.MoveToEx(dc, x - half_size, y)
    win32gui.LineTo(dc, x + half_size, y)
    win32gui.MoveToEx(dc, x, y - half_size)
    win32gui.LineTo(dc, x, y + half_size)
    win32gui.DeleteObject(pen)
    # win32gui.ReleaseDC(hwnd, hdc)

# Example usage
# draw_rectangle(100, 100, 300, 200, win32api.RGB(255, 0, 0))  # Red rectangle
# draw_cross(400, 300, 20, win32api.RGB(0, 255, 0))  # Green cross
