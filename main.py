import time
from datetime import datetime
import math

import numpy as np
from mss import mss
import cv2
import win32gui, win32api, win32con
from ctypes import windll, Structure, c_ulong, byref, sizeof

# import clicker
# import opencv
from pynput import keyboard
from settings_manager import SettingsManager
import customtkinter as ctk
from customtkinter import CTkCanvas
from threading import Thread, get_ident

# from game_session import start_game_session_monitoring, stop_game_session_monitoring, game_session_monitoring_thread_running
import game_session
import bonus_task
import user_interface
from app_variables import kwargs


screening_running = False
clicker_running = False
auto_running = False
auto_start_running = False
auto_end_running = False
game_auto_running = False

settings = SettingsManager("settings.json")

monitor = {'left': 1450, 'top': 370, 'width': 380, 'height': 660}
get_screen_rectangle_manually = True
screening_thread = None
click_distance = 20
threshold = 0.305
unite_tolerance = 20
telegram_window = None


# settings.set_setting('monitor', monitor)
# settings.set_setting('get_screen_rectangle_manually', get_screen_rectangle_manually)
# settings.save_settings()

# Retrieve settings
monitor = settings.get_setting('monitor', monitor)
get_screen_rectangle_manually = settings.get_setting('get_screen_rectangle_manually', get_screen_rectangle_manually)
threshold = settings.get_setting('threshold', threshold)
unite_tolerance = settings.get_setting('unite_tolerance', unite_tolerance)
clicker_threads_no: int = settings.get_setting('clicker_threads_no', 1)

time_str = settings.get_setting("game_session_start_time", "08:00")
game_session_start_time = datetime.strptime(time_str, "%H:%M").time()
games_per_session_no = int(settings.get_setting('games_per_session_no', 1))
pause_between_games_seconds = int(settings.get_setting('pause_between_games_seconds', 5))

# print(f"\nMonitor rectangle coordinates: {monitor}")
# print(f"Get coordinates manually: {get_screen_rectangle_manually}")


# Define the CURSORINFO structure
class CURSORINFO(Structure):
    _fields_ = [("cbSize", c_ulong),
                ("flags", c_ulong),
                ("hCursor", c_ulong),
                ("ptScreenPos", c_ulong)]


def current_time() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")


def on_game_session_start_time_change(event):
    global app, game_session_start_time
    # app = App()
    print(f"Event occured: {event}")
    try:
        time_str = app.game_session_start_time_value.get()
        game_session_start_time = datetime.strptime(time_str, "%H:%M").time()
        settings.set_setting('game_session_start_time', time_str)
        settings.save_settings()
        print(f"game_session_start_time value set to {time_str}.")
        # Update the result or perform any other actions
        game_monitoring.session_start_time = game_session_start_time
    except ValueError:
        print(f"Invalid value entered. game_session_start_time value set to {str(game_session_start_time.strftime('%H:%M'))}.")
        # Handle the case when the input is not a valid number
        pass


def on_games_per_session_no_change(event):
    global app, games_per_session_no
    # app = App()
    print(f"Event occured: {event}")
    try:
        # time_str = app.game_session_start_time_value.get()
        games_per_session_no = int(app.games_per_session_no_value.get())
        settings.set_setting('games_per_session_no', games_per_session_no.__str__())
        settings.save_settings()
        print(f"games_per_session_no value set to {games_per_session_no}.")
        # Update the result or perform any other actions
        game_monitoring.session_games_no = games_per_session_no
    except ValueError:
        print(f"Invalid value entered. games_per_session_no value set to {games_per_session_no.__str__()}.")
        # Handle the case when the input is not a valid number
        pass


def on_pause_between_games_change(event):
    global app, pause_between_games_seconds
    # app = App()
    print(f"Event occured: {event}")
    try:
        pause_between_games_seconds = app.pause_between_games_value.get()
        settings.set_setting('pause_between_games_seconds', pause_between_games_seconds)
        settings.save_settings()
        print(f"pause_between_games_seconds value set to {pause_between_games_seconds}.")
        # Update the result or perform any other actions
        game_monitoring.pause_between_games_seconds = pause_between_games_seconds
    except ValueError:
        print(f"Invalid value entered. pause_between_games_seconds value set to {str(pause_between_games_seconds)}.")
        # Handle the case when the input is not a valid number
        pass


def on_threshold_changed(event):
    global app, threshold
    # app = App()
    print(f"Event occured: {event}")
    try:
        threshold = float(app.screening_threshold_value.get())
        settings.set_setting('threshold', threshold)
        settings.save_settings()
        print(f"Threshold value set to {threshold}.")
        # Update the result or perform any other actions
    except ValueError:
        print(f"Invalid threshold value entered. Threshold value set to {threshold}.")
        # Handle the case when the input is not a valid number
        pass


def on_entry_enter(event):
    print(f"Event occured: {event}")

    pass
    # print(f"Press Enter to confirm entered value.")


def on_unite_tolerance_changed(event):
    global app, unite_tolerance
    # app = App()
    print(f"Event occured: {event}")
    try:
        unite_tolerance = float(app.screening_unite_tolerance_value.get())
        settings.set_setting('unite_tolerance', unite_tolerance)
        settings.save_settings()
        print(f"Unite tolerance value set to {unite_tolerance}.")
        # Update the result or perform any other actions
    except ValueError:
        print(f"Invalid Unite tolerance value entered. Unite tolerance value set to {unite_tolerance}.")
        # Handle the case when the input is not a valid number
        pass


def on_clicker_threads_no_changed(event):
    global app, clicker_threads_no
    # app = App()
    print(f"Event occured: {event}")
    try:
        clicker_threads_no = float(app.clicker_threads_no_value.get())
        settings.set_setting('clicker_threads_no', clicker_threads_no)
        settings.save_settings()
        print(f"Clicker threads no value set to {clicker_threads_no}.")
        # Update the result or perform any other actions
    except ValueError:
        print(f"Invalid clicker threads no value entered. Threads no value set to {clicker_threads_no}.")
        # Handle the case when the input is not a valid number
        pass


def get_telegram_window() -> user_interface.ScreenAreaAutoStatus:
    global monitor, app, telegram_window
    import telegram_app_window as tgwin

    app.screen_area_auto.status = user_interface.ScreenAreaAutoStatus.Processing
    # app = App()
    if app is not None:
        app.update_auto_area_value(app.screen_area_auto.status)

    telegram_window = tgwin.get_blum_window("telegram.blum.codes")
    if telegram_window is None:
        print("Telegram window not found")
        app.screen_area_auto.status = user_interface.ScreenAreaAutoStatus.Failed
        if app is not None:
            app.update_auto_area_value(app.screen_area_auto.status)
        return app.screen_area_auto.status

    window_handle = telegram_window["hwnd"]
    monitor = telegram_window["monitor"]
    # app = App()
    if app is not None:
        app.update_screen_area_value(monitor)
    settings.set_setting('monitor', monitor)
    settings.save_settings()
    if window_handle is None:
        print("Telegram window has no handle")
        app.screen_area_auto.status = user_interface.ScreenAreaAutoStatus.Failed
        app.update_auto_area_value(app.screen_area_auto.status)
        return app.screen_area_auto.status

    app.screen_area_auto.status = user_interface.ScreenAreaAutoStatus.OK
    if app is not None:
        app.update_auto_area_value(app.screen_area_auto.status)

    return app.screen_area_auto.status


def get_screen_area():
    global monitor, app

    # app = App()
    rectangle_coords = None
    if get_screen_rectangle_manually:
        print(f"\nWaiting for rectangle coordinates...")
        # Call the function to get the screen rectangle coordinates
        # rectangle_coords = get_screen_rectangle()
        rectangle_coords = get_screen_rectangle()

    if rectangle_coords:
        print(f"Rectangle coordinates obtained: {rectangle_coords}")
        monitor = {'left': rectangle_coords[0],
                   'top': rectangle_coords[1],
                   'width': rectangle_coords[2],
                   'height': rectangle_coords[3]}
        settings.set_setting('monitor', monitor)
        settings.save_settings()
        if app is not None:
            app.update_screen_area_value(monitor)

    else:
        # monitor = {'left': 1450, 'top': 370, 'width': 380, 'height': 660}
        print(f"No rectangle coordinates obtained. Using previously set coordinates at {monitor}.")


def start_game_session():
    game_monitoring.start()


def stop_game_session():
    game_monitoring.stop()


def start_screening():
    global screening_thread, screening_running, track_id_max
    print(f"Starting screening thread ...")
    track_id_max = 0
    screening_thread = Thread(target=main)
    screening_thread.start()
    print(f"Screening thread started")


def stop_screening():
    global screening_thread, screening_running, app
    print(f"Stopping screening thread ...")
    screening_running = False
    # screening_thread.join()
    # app = App()
    if app is not None:
        app.update_screening_status_value(value=screening_running.__str__())
    print(f"Screening thread stopped")


def load_ui():
    global monitor, app, screen_area_auto
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("dark-blue")

    # app = App()
    app.screen_area_auto.status = get_telegram_window()


def update_ui():
    global app
    # app = App()
    if app is not None:
        app.update_values()


def get_screen_rectangle() -> tuple[int, int, int, int]:
    global monitor
    # Initialize variables for rectangle coordinates
    rect_start = (0, 0)
    rect_end = (0, 0)
    rect_drawn = False
    rectangle_coords = None

    # Get the screen dimensions
    root = ctk.CTkToplevel()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.overrideredirect(True)  # Remove window decorations
    root.geometry(f"{screen_width}x{screen_height}+0+0")  # Set window size and position
    root.attributes("-alpha", 0.5)  # Set window transparency (0.0 = fully transparent, 1.0 = opaque)

    canvas = CTkCanvas(root, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    canvas.create_rectangle(monitor["left"], monitor["top"], monitor["left"] + monitor["width"],
                            monitor["top"] + monitor["height"], outline="blue",
                            width=2, tags="screen_rectangle")

    def on_key_press(event):
        nonlocal rect_drawn
        if event.keysym == "q" or event.keysym == "Escape" or event.keysym == "w":
            print(f"{event.keysym} pressed")
            root.destroy()
            rect_drawn = True

    def draw_rect(event):
        nonlocal rect_start, rect_end, rect_drawn, rectangle_coords
        is_mouse_button_up = False
        if event.type == "4":  # Left mouse button down
            # print(f"Left mouse button down")
            rect_start = (event.x, event.y)
            rect_end = (event.x, event.y)
            rect_drawn = False
        elif event.type == "6":  # Mouse move
            # print(f"Mouse moving ...")
            if rect_drawn is False:
                rect_end = (event.x, event.y)
        elif event.type == "5":  # Left mouse button up
            # print(f"Left mouse button up")
            rect_end = (event.x, event.y)
            rect_drawn = True
            top_left = (min(rect_start[0], rect_end[0]), min(rect_start[1], rect_end[1]))
            bottom_right = (max(rect_start[0], rect_end[0]), max(rect_start[1], rect_end[1]))
            width = bottom_right[0] - top_left[0]
            height = bottom_right[1] - top_left[1]
            rectangle_coords = (top_left[0], top_left[1], width, height)
            root.destroy()  # Destroy the window after getting the rectangle coordinates
            is_mouse_button_up = True
        # elif event.type == "Escape":
        #     root.destroy()  # Destroy the window after getting the rectangle coordinates
        #     is_mouse_button_up = True

        if canvas and not is_mouse_button_up:
            canvas.delete("rectangle")
            if rect_drawn or (rect_start != rect_end):
                canvas.create_rectangle(rect_start[0], rect_start[1], rect_end[0], rect_end[1], outline="green",
                                        width=2, tags="rectangle")

    canvas.bind("<ButtonPress-1>", draw_rect)
    canvas.bind("<B1-Motion>", draw_rect)
    canvas.bind("<ButtonRelease-1>", draw_rect)
    # canvas.bind("<Escape>", lambda event: root.destroy())  # Bind Esc key to destroy the window
    canvas.bind("<Key>", on_key_press)  # Bind Esc key to destroy the window
    print(f"Press 'q' to quit (in this case no coordinates will be obtained) ...")
    canvas.focus_set()

    while not rect_drawn:
        root.update()

    return rectangle_coords


def on_press(key):
    """
    Function to handle keyboard input.
    """
    global app, screening_running, clicker_running, auto_start_running, auto_end_running
    # app = App()
    if key == keyboard.Key.esc:
        # Stop the threads when the Esc key is pressed
        print(f"Esc pressed. Stopping screening ...")
        screening_running = False
        if app is not None:
            app.update_screening_status_value(screening_running.__str__())

        return False
    if key == keyboard.Key.ctrl_l:
        print(f"Ctrl pressed. Stopping clicker ...")
        clicker_running = False
        if app is not None:
            app.update_clicker_status_value(clicker_running.__str__())
        # app.update()
        return False

    if key.__str__() == 'q':
        print(f"'q' pressed. Stopping auto mode ...")
        auto_start_running = False
        if app is not None:
            app.update_auto_start_value(auto_start_running.__str__())
            app.update_auto_end_value(auto_end_running.__str__())
        auto_end_running = False


track_id_max = 0
current_objects = {"objects": [], "timestamp": 0.0}
previous_objects = {"objects": [], "timestamp": 0.0}
click_points = {"flakes": [], "bombs": [], "bluebirds": [], "timestamp": 0.0}
click_cycle_done = False


def get_click_points(boxes, name_ids, screenshot_timestamp):
    global click_points, monitor

    click_points["flakes"] = []
    click_points["bombs"] = []
    click_points["bluebirds"] = []
    click_points["timestamp"] = screenshot_timestamp
    for box, name_id in zip(boxes, name_ids):
        x, y, w, h = box
        square = w * h
        match name_id:
            case 0:
                click_points["flakes"].append((x + monitor['left'], y + monitor['top'], square, w, h))
            case 1:
                click_points["bombs"].append((x + monitor['left'], y + monitor['top'], square, w, h))
            case 2:
                click_points["bluebirds"].append((x + monitor['left'], y + monitor['top'], square, w, h))

    return click_points


def auto_start() -> bool:  # autostart screening and clicker on counter image appearing on screen
    global game_auto_running
    game_auto_running = True
    # Start auto start screening
    print(f"Starting START SCREENING ...")
    start_game_start_screening()
    # Waiting for screening start
    while not auto_start_running:
        time.sleep(1)
    print(f"START SCREENING launched successfully.")

    # Check for home page
    print(f"Checking for home page ...")
    while not is_home_page():
        get_back_to_home_page()
        time.sleep(1)
    game_monitoring.is_home_page = True

    # Start game
    print(f"Navigating to play ...")
    while not navigate_to_play_game():
        time.sleep(1)
    print(f"Navigated successfully.")
    return True


def start_game_start_screening():
    global screening_running, app, clicker_running, auto_running
    # app = App()
    print(f"Starting game start screening thread ...")
    game_start_screening = Thread(target=game_start_screening_thread, daemon=True)
    game_start_screening.start()
    print(f"Game start screening thread started")


def game_start_screening_thread():
    global screening_running, app, clicker_running, auto_running, auto_start_running

    # Create a listener to monitor keyboard input
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    # app = App()
    # time.sleep(25)
    auto_start_running = True
    # app.update_auto_start_value(auto_start_running.__str__())
    app.update_auto_start_value(auto_start_running.__str__())

    time.sleep(1)

    print(f"SCREENING START thread started ...")
    print(f"Waiting for game start ...")
    img_to_wait_path = r"images/Counter_01.png"
    wait_result, img_location = wait_for_image_on_screen(img_to_wait_path, threshold=0.6, start_detection=True)
    listener.stop
    if wait_result:
        print(f"Game start detected. Starting clicker and screening ...")
        game_monitoring.is_game_running = True
        app.update_game_value(True.__str__())

        start_screening()
        start_clicker()

        auto_start_running = False
        app.update_auto_start_value(auto_start_running.__str__())

        time.sleep(28)
        start_game_end_screening()
        print(f"Clicker and screening are started")
    else:
        auto_start_running = False
        app.update_auto_start_value(auto_start_running.__str__())
        app.update_game_value(False.__str__())
        # game_monitoring.stop()
        print(f"Start detection failed")


def start_game_end_screening():
    global screening_running, app, clicker_running, auto_running
    # app = App()
    print(f"Starting game end screening thread ...")
    game_end_screening = Thread(target=game_end_screening_thread)
    game_end_screening.start()
    print(f"Game end screening thread started")


def game_end_screening_thread():
    global screening_running, app, clicker_running, auto_running, auto_end_running, game_auto_running
    # app = App()
    # time.sleep(25)
    auto_end_running = True
    if app is not None:
        app.update_auto_end_value(auto_end_running.__str__())
    print(f"Thread started ...")
    img_to_wait_path = r"images/Share_you_win.png"
    # app.update_autostart_status_label("Waiting for game start ...")
    # app.update_autostart_info_label("Press 'Play' button to start\n or 'Esc' or 'q' to quit ...")
    wait_result, img_location = wait_for_image_on_screen(img_to_wait_path, threshold=0.6, start_detection=False, timeout=90)
    if wait_result:
        print(f"Game end detected. Stopping clicker and screening ...")
        auto_end_running = False
        app.update_auto_end_value(auto_end_running.__str__())
        game_auto_running = False
        game_monitoring.is_game_running = False
        app.update_game_value(False.__str__())

        stop_clicker()
        stop_screening()
        time.sleep(2)
        print(f"Getting back to home ...")
        while not is_home_page():
            get_back_to_home_page()
            time.sleep(1)
        game_monitoring.is_home_page = True
        print(f"Clicker and screening are stopped")

    else:
        print(f"Game end TIMEOUT. Stopping clicker and screening ...")
        auto_end_running = False
        app.update_auto_end_value(auto_end_running.__str__())
        game_auto_running = False
        game_monitoring.is_game_running = False
        app.update_game_value(False.__str__())
        stop_clicker()
        stop_screening()
        time.sleep(2)
        print(f"Getting back to home ...")
        while not is_home_page():
            get_back_to_home_page()
            time.sleep(1)
        game_monitoring.is_home_page = True
        print(f"Clicker and screening are stopped by TIMEOUT")

        print(f"End detection cancelled")


def get_back_to_home_page():
    global telegram_window

    def convert_points_area_size_area(point_area: tuple) -> tuple:
        x_l, y_t, x_r, y_b = point_area
        return x_l, y_t, x_r - x_l, y_b - y_t

    if telegram_window is not None:
        screen_area = telegram_window["rect"]
        screen_area = convert_points_area_size_area(screen_area)
        back_button_location = get_image_location(img_path="images/blum_back_game_page.png", screen_area=screen_area)
        if back_button_location:
            x, y = back_button_location
            click(int(x - 30), int(y), click_pause=0.1)
            # win32api.SetCursorPos((x, y))
            # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            time.sleep(0.5)
        pass


def is_home_page() -> bool:
    global telegram_window

    def convert_points_area_size_area(point_area: tuple) -> tuple:
        x_l, y_t, x_r, y_b = point_area
        return x_l, y_t, x_r - x_l, y_b - y_t

    if telegram_window is not None:
        screen_area = telegram_window["rect"]
        screen_area = convert_points_area_size_area(screen_area)
        # back_button_location = get_image_location(img_path="images/blum_back_game_page.png", screen_area=screen_area)
        home_menu_location = get_image_location(img_path="images/main_menu_home_page.png", screen_area=screen_area)
        if home_menu_location:
            # It's a home page
            # click(home_menu_location[0], home_menu_location[1], just_move=True)
            return True

        return False


def click(x, y, just_move=False, change_cursor=False, click_pause=0.01):
    win32api.SetCursorPos((x, y))
    time.sleep(click_pause)
    if change_cursor:
        # Get the current cursor
        cursor_info = CURSORINFO()
        cursor_info.cbSize = sizeof(CURSORINFO)
        windll.user32.GetCursorInfo(byref(cursor_info))
        current_cursor = cursor_info.hCursor
        # Load a custom cursor from a file
        # custom_cursor = win32api.LoadCursor(r"cursors/Basic Green Light.cur")
        custom_cursor = win32api.LoadCursor(None, win32con.IDC_HAND)

        # Set the custom cursor
        win32api.SetCursor(custom_cursor)

    if not just_move:
        # if not scroll:
        # Click the mouse button
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(click_pause)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        # else:
        #     # Scroll the mouse wheel
        #     win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 0, 1)
        #     time.sleep(0.01)
        #     win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 0, -1)
        #     time.sleep(0.01)

    if change_cursor:
        # Restore the previous cursor
        win32api.SetCursor(current_cursor)


def scroll(x: int, y: int, clicks):
    win32api.SetCursorPos((x, y))
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, clicks * 120, 0)


def grab_screen_area():
    global monitor
    area = {"left": monitor["left"] + 100,
            "top": monitor["top"] + 100,
            "width": 10,
            "height": 100}
    start = time.perf_counter()
    with mss() as sct:
        screenshot = sct.grab(area)
        end = time.perf_counter()
        print(f"grab_screen_area() -> sct.grab() time: {end - start:0.6f} seconds")
        frame = np.array(screenshot)
        end = time.perf_counter()
        print(f"grab_screen_area() -> with np.array() time: {end - start:0.6f} seconds")
        screen = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        end = time.perf_counter()
        print(f"grab_screen_area() -> with cv2.cvtColor() time: {end - start:0.6f} seconds")
        return screen


def test_click_confirmed():
    click_point = (1820, 420)
    # click_point = (1813, 376)
    # click_point = (1745, 338)
    # click_point = (1600, 475)
    click_confirmed = is_click_confirmed(click_point)
    print(f"test_click_confirmed() -> click_confirmed: {click_confirmed}")


def navigate_to_play_game() -> bool:
    global monitor, app, telegram_window
    import win32gui
    import win32ui
    import win32api
    import win32con
    import win32process
    import win32com.client
    import time
    import telegram_app_window as tgwin

    telegram_window = tgwin.get_blum_window("telegram.blum.codes")
    if telegram_window is None:
        print("Telegram window not found")
        return False

    window_handle = telegram_window["hwnd"]
    monitor = telegram_window["monitor"]
    # app = App()
    if app is not None:
        app.update_screen_area_value(monitor)
    settings.set_setting('monitor', monitor)
    settings.save_settings()
    if window_handle is None:
        print("Telegram window has no handle")
        return False

    # Find Play button
    play_button_location = get_play_button_location(threshold=0.7)
    if play_button_location is None:
        # Try to scroll down
        scroll_location = int(monitor["left"] + monitor["width"] / 2), int(monitor["top"] + monitor["height"] / 2)
        scroll(scroll_location[0], scroll_location[1], -10)
        time.sleep(0.2)
        start = time.perf_counter()
        timeout = 5
        while play_button_location is None:
            play_button_location = get_play_button_location(threshold=0.7)
            end = time.perf_counter()
            time_interval = end - start
            if time_interval > timeout:
                # print(f"Play button not found in {timeout} seconds")
                break
            time.sleep(0.2)

        if play_button_location is None:
            print("Play button not found")
            return False

    click(play_button_location[0], play_button_location[1], just_move=False, click_pause=0.2)
    return True


def is_click_confirmed(click_point: tuple) -> bool:
    global monitor
    whole_distance = monitor["height"]  # pixels
    whole_time_min = 2  # seconds
    whole_time_max = 2.5  # seconds
    speed_min = whole_distance / whole_time_max
    speed_max = whole_distance / whole_time_min
    check_time = 0.05
    safe_distance = 30
    # speed_distance_min = check_time * speed_min
    speed_distance_max = check_time * speed_max
    area_left = int(click_point[0] - safe_distance)
    area_top = int(click_point[1] - safe_distance - speed_distance_max)
    area_width = int(2 * safe_distance)
    area_height = int(2 * safe_distance + speed_distance_max)

    divider = 1
    bottom_area = {"left": area_left,
                   "top": (area_top + area_height - area_height / divider),
                   "width": area_width,
                   "height": (area_height / divider)}
    # Specify the screen area to capture
    # area = {"left": monitor["left"] + area_left,
    #         "top": monitor["top"] + area_top,
    #         "width": area_width,
    #         "height": area_height}
    some_shift_from_top = 0
    area = {"left": area_left,
            "top": area_top + some_shift_from_top,
            "width": area_width,
            "height": area_height}

    start = time.perf_counter()

    # Define the color range for green shades (in BGR format)
    # FLAKES
    # Lower green range: (21, 172, 158)
    # Upper green range: (91, 255, 255)

    # Lower green range: (46, 102, 142)
    # Upper green range: (59, 250, 240)

    # Lower green range: (32, 61, 69)
    # Upper green range: (87, 255, 246)

    # BOMB
    # Lower green range: (0, 0, 0)
    # Upper green range: (74, 42, 255)

    # Lower green range: (0, 0, 123)
    # Upper green range: (179, 43, 255)

    # Lower green range: (0, 0, 60)
    # Upper green range: (20, 30, 229)

    # Lower green range: (0, 0, 101)
    # Upper green range: (26, 25, 253)

    # BOMB FUSE
    # Lower green range: (0, 58, 74)
    # Upper green range: (30, 202, 207)

    # BLUE BIRD
    # Lower hsv range: (90, 35, 94)
    # Upper hsv range: (105, 255, 255)

    def point_in_area(point: tuple, check_area) -> bool:
        # print(f"point: {point}")
        # print(f"area: {area}")
        if point[0] < check_area["left"] or point[0] > check_area["left"] + check_area["width"] or \
                point[1] < check_area["top"] or point[1] > check_area["top"] + check_area["height"]:
            return False
        return True

    point_in_bottom_half = point_in_area(click_point, bottom_area)

    lower_flake = np.array([32, 61, 69])  # Lower bound of the color range
    upper_flake = np.array([87, 255, 246])  # Upper bound of the color range

    lower_bomb = np.array([0, 0, 101])  # Lower bound of the color range
    upper_bomb = np.array([26, 25, 240])  # Upper bound of the color range

    lower_bomb_fuze = np.array([0, 58, 74])  # Lower bound of the color range
    upper_bomb_fuze = np.array([30, 202, 207])  # Upper bound of the color range

    lower_bird = np.array([90, 35, 94])  # Lower bound of the color range
    upper_bird = np.array([105, 255, 255])  # Upper bound of the color range

    # Grab the screen area using mss
    with mss() as sct:
        screenshot = sct.grab(area)
        img_np = np.array(screenshot)  # Convert the screenshot to a NumPy array

    # Convert the image to the HSV color space
    # img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)

    # Create a mask for the flake color range
    mask_flake = cv2.inRange(img_bgr, lower_flake, upper_flake)

    # Create a mask for the bomb color range
    mask_bomb = cv2.inRange(img_bgr, lower_bomb, upper_bomb)

    # Create a mask for the bomb fuze color range
    mask_bomb_fuze = cv2.inRange(img_bgr, lower_bomb_fuze, upper_bomb_fuze)

    # Create a mask for the bird color range
    # mask_bird = cv2.inRange(img_bgr, lower_bird, upper_bird)

    # Check if any pixels in the mask are non-zero (i.e., if green shades exist)
    flake_exist = cv2.countNonZero(mask_flake) > 0
    bomb_exist = cv2.countNonZero(mask_bomb) > 0
    bomb_fuze_exist = cv2.countNonZero(mask_bomb_fuze) > 0
    # bird_exist = cv2.countNonZero(mask_bird) > 0 and not point_in_bottom_half

    # if flake_exist:
    #     print("Flake exist in the screen area.")
    # else:
    #     print("Flake DOES NOT exist in the screen area.")
    # if bomb_exist:
    #     print("Bomb exist in the screen area.")
    # else:
    #     print("Bomb DOES NOT exist in the screen area.")
    # if bomb_exist:
    #     print("Bomb Fuze exist in the screen area.")
    # else:
    #     print("Bomb Fuze DOES NOT exist in the screen area.")

    end = time.perf_counter()
    print(f"is_click_confirmed() -> general time: {end - start:0.6f} seconds")
    # res = cv2.imwrite(r'images\screenshot.png', screenshot)
    # print(f"screenshot.png res = {res}")
    # res = cv2.imwrite(r'images\img_np.png', img_np)
    # print(f"img_np.png res = {res}")
    # res = cv2.imwrite(r'images\img_bgr.png', img_bgr)
    # print(f"img_bgr.png res = {res}")
    # res = cv2.imwrite(r'images\mask_flake.png', mask_flake)
    # print(f"mask_flake.png res = {res}")
    # res = cv2.imwrite(r'images\mask_bomb.png', mask_bomb)
    # print(f"mask_bomb.png res = {res}")
    # res = cv2.imwrite(r'images\mask_bomb_fuze.png', mask_bomb_fuze)
    # print(f"mask_bomb_fuze.png res = {res}")
    # print(f"grab_screen_area_green() -> images saved.")

    # return flake_exist and not bomb_exist and not bomb_fuze_exist and not bird_exist
    return flake_exist and not bomb_exist and not bomb_fuze_exist


def is_click_confirmed_without_blue_bird(click_point: tuple) -> bool:
    global monitor
    whole_distance = monitor["height"]  # pixels
    whole_time_min = 2  # seconds
    whole_time_max = 2.5  # seconds
    speed_min = whole_distance / whole_time_max
    speed_max = whole_distance / whole_time_min
    check_time = 0.05
    safe_distance = 30
    # speed_distance_min = check_time * speed_min
    speed_distance_max = check_time * speed_max
    area_left = int(click_point[0] - safe_distance)
    area_top = int(click_point[1] - safe_distance - speed_distance_max)
    area_width = int(2 * safe_distance)
    area_height = int(2 * safe_distance + speed_distance_max)

    # Specify the screen area to capture
    # area = {"left": monitor["left"] + area_left,
    #         "top": monitor["top"] + area_top,
    #         "width": area_width,
    #         "height": area_height}

    area = {"left": area_left,
            "top": area_top,
            "width": area_width,
            "height": area_height}

    start = time.perf_counter()

    # Define the color range for green shades (in BGR format)
    # FLAKES
    # Lower green range: (21, 172, 158)
    # Upper green range: (91, 255, 255)

    # Lower green range: (46, 102, 142)
    # Upper green range: (59, 250, 240)

    # Lower green range: (32, 61, 69)
    # Upper green range: (87, 255, 246)

    # BOMB
    # Lower green range: (0, 0, 0)
    # Upper green range: (74, 42, 255)

    # Lower green range: (0, 0, 123)
    # Upper green range: (179, 43, 255)

    # Lower green range: (0, 0, 60)
    # Upper green range: (20, 30, 229)

    # Lower green range: (0, 0, 101)
    # Upper green range: (26, 25, 253)

    # BOMB FUSE
    # Lower green range: (0, 58, 74)
    # Upper green range: (30, 202, 207)

    lower_flake = np.array([32, 61, 69])  # Lower bound of the color range
    upper_flake = np.array([87, 255, 246])  # Upper bound of the color range

    lower_bomb = np.array([0, 0, 101])  # Lower bound of the color range
    upper_bomb = np.array([26, 25, 240])  # Upper bound of the color range

    lower_bomb_fuze = np.array([0, 58, 74])  # Lower bound of the color range
    upper_bomb_fuze = np.array([30, 202, 207])  # Upper bound of the color range

    # Grab the screen area using mss
    with mss() as sct:
        screenshot = sct.grab(area)
        img_np = np.array(screenshot)  # Convert the screenshot to a NumPy array

    # Convert the image to the HSV color space
    # img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)

    # Create a mask for the flake color range
    mask_flake = cv2.inRange(img_bgr, lower_flake, upper_flake)

    # Create a mask for the bomb color range
    mask_bomb = cv2.inRange(img_bgr, lower_bomb, upper_bomb)

    # Create a mask for the bomb fuze color range
    mask_bomb_fuze = cv2.inRange(img_bgr, lower_bomb_fuze, upper_bomb_fuze)

    # Check if any pixels in the mask are non-zero (i.e., if green shades exist)
    flake_exist = cv2.countNonZero(mask_flake) > 0
    bomb_exist = cv2.countNonZero(mask_bomb) > 0
    bomb_fuze_exist = cv2.countNonZero(mask_bomb_fuze) > 0

    # if flake_exist:
    #     print("Flake exist in the screen area.")
    # else:
    #     print("Flake DOES NOT exist in the screen area.")
    # if bomb_exist:
    #     print("Bomb exist in the screen area.")
    # else:
    #     print("Bomb DOES NOT exist in the screen area.")
    # if bomb_exist:
    #     print("Bomb Fuze exist in the screen area.")
    # else:
    #     print("Bomb Fuze DOES NOT exist in the screen area.")

    end = time.perf_counter()
    print(f"is_click_confirmed() -> general time: {end - start:0.6f} seconds")
    # res = cv2.imwrite(r'images\screenshot.png', screenshot)
    # print(f"screenshot.png res = {res}")
    # res = cv2.imwrite(r'images\img_np.png', img_np)
    # print(f"img_np.png res = {res}")
    # res = cv2.imwrite(r'images\img_bgr.png', img_bgr)
    # print(f"img_bgr.png res = {res}")
    # res = cv2.imwrite(r'images\mask_flake.png', mask_flake)
    # print(f"mask_flake.png res = {res}")
    # res = cv2.imwrite(r'images\mask_bomb.png', mask_bomb)
    # print(f"mask_bomb.png res = {res}")
    # res = cv2.imwrite(r'images\mask_bomb_fuze.png', mask_bomb_fuze)
    # print(f"mask_bomb_fuze.png res = {res}")
    # print(f"grab_screen_area_green() -> images saved.")

    return flake_exist and not bomb_exist and not bomb_fuze_exist


def get_objects_locations_by_hsv_mask() -> tuple:
    global monitor

    area = {"left": monitor["left"],
            "top": monitor["top"],
            "width": monitor["width"],
            "height": monitor["height"]}

    start = time.perf_counter()

    # Define the color range for green shades (in BGR format)
    # FLAKES
    # Lower green range: (32, 61, 69)
    # Upper green range: (87, 255, 246)

    # BOMB
    # Lower green range: (0, 0, 101)
    # Upper green range: (26, 25, 253)

    # BOMB FUSE
    # Lower green range: (0, 58, 74)
    # Upper green range: (30, 202, 207)

    lower_flake = np.array([32, 61, 69])  # Lower bound of the color range
    upper_flake = np.array([87, 255, 246])  # Upper bound of the color range

    lower_bomb = np.array([0, 0, 101])  # Lower bound of the color range
    upper_bomb = np.array([26, 25, 240])  # Upper bound of the color range

    lower_bomb_fuze = np.array([0, 58, 74])  # Lower bound of the color range
    upper_bomb_fuze = np.array([30, 202, 207])  # Upper bound of the color range

    # Grab the screen area using mss
    with mss() as sct:
        screenshot = sct.grab(area)
        img_np = np.array(screenshot)  # Convert the screenshot to a NumPy array
        screen = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

    # Convert the image to the HSV color space
    # img_hsv = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
    img_hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)

    # Create a mask for the flake color range
    mask_flake = cv2.inRange(img_hsv, lower_flake, upper_flake)

    # Create a mask for the bomb color range
    mask_bomb = cv2.inRange(img_hsv, lower_bomb, upper_bomb)

    # Create a mask for the bomb fuze color range
    mask_bomb_fuze = cv2.inRange(img_hsv, lower_bomb_fuze, upper_bomb_fuze)

    # Check if any pixels in the mask are non-zero (i.e., if green shades exist)
    flake_exist = cv2.countNonZero(mask_flake) > 0
    bomb_exist = cv2.countNonZero(mask_bomb) > 0
    bomb_fuze_exist = cv2.countNonZero(mask_bomb_fuze) > 0

    end = time.perf_counter()
    print(f"is_click_confirmed() -> general time: {end - start:0.6f} seconds")

    # Find the coordinates of the non-zero pixels (areas within the HSV range)
    coords_flakes = np.where(mask_flake != 0)

    # coords_bombs = np.where(mask_bomb != 0)
    # coords_bomb_fuzes = np.where(mask_bomb_fuze != 0)

    def unite_close_points(x_coords, y_coords, tolerance):
        clusters = {}

        for x, y in zip(x_coords, y_coords):
            found_cluster = False

            # Check if a cluster exists within the tolerance
            for cluster_center, cluster_points in clusters.items():
                cx, cy = cluster_center
                if math.sqrt((x - cx) ** 2 + (y - cy) ** 2) <= tolerance:
                    cluster_points.append((x, y))
                    new_center_x = sum(p[0] for p in cluster_points) / len(cluster_points)
                    new_center_y = sum(p[1] for p in cluster_points) / len(cluster_points)
                    clusters[cluster_center] = cluster_points
                    clusters[(new_center_x, new_center_y)] = clusters.pop(cluster_center)
                    found_cluster = True
                    break

            # If no cluster found, create a new cluster
            if not found_cluster:
                clusters[(x, y)] = [(x, y)]

        # Extract the center coordinates of each cluster
        # new_x_coords = []
        # new_y_coords = []
        new_coords = []
        for center, points in clusters.items():
            # new_x_coords.append(center[0])
            # new_y_coords.append(center[1])
            new_coords.append((int(center[0]), int(center[1])))

        # return new_x_coords, new_y_coords
        return new_coords

        # # Example usage
        # x_coords = [29, 29, 29, 29, 29, 29, 30, 30, 30, 30, 30, 30, 30, 30, 31, 31, 31, 31, 31, 31, 31, 31, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 34, 34, 34, 34, 34, 34, 34, 34, 34, 35, 35, 35, 35, 35, 35, 35, 35, 35, 36, 36, 36, 36, 36, 36, 36, 37, 37, 37, 37, 37, 139, 139, 139, 139, 139, 139, 139, 140, 140, 140, 140, 140, 140, 140, 140, 140, 141, 141, 141, 141, 141, 141, 141, 141, 141, 141, 142, 142]
        # y_coords = [211, 212, 213, 214, 215, 216, 210, 211, 212, 213, 214, 215, 216, 217, 210, 211, 212, 213, 214, 215, 216, 217, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 209, 210, 211, 212, 213, 214, 215, 216, 217, 209, 210, 211, 212, 213, 214, 215, 216, 217, 210, 211, 212, 213, 214, 215, 216, 211, 212, 213, 214, 215, 288, 289, 290, 291, 292, 293, 294, 287, 288, 289, 290, 291, 292, 293, 294, 295, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 285, 286]
        #
        # tolerance = 2
        #
        # new_x_coords, new_y_coords = unite_close_points(x_coords, y_coords, tolerance)
        # print("New x coordinates:", new_x_coords)
        # print("New y coordinates:", new_y_coords)

    def get_center_coords(points: tuple, size: tuple) -> list:
        c_points = []
        if len(points) > 0:
            for point in points:
                c_points.append(tuple([int(point[0] + size[0] / 2), int(point[1] + size[1] / 2)]))
        return c_points

    # loc = np.where((res >= threshold) & (res < threshold + threshold_gap))
    # loc = np.where((mask_flake >= 1) & (mask_flake < 2))
    # loc = np.where((mask_flake >= 1))

    global unite_tolerance
    # unite_tolerance = 20
    s_t = time.perf_counter()
    # print(f"unite_tolerance = {unite_tolerance}")
    new_points_flakes = unite_close_points(coords_flakes[1], coords_flakes[0], unite_tolerance)
    e_t = time.perf_counter()
    print(f"unite_close_points time = {e_t - s_t:0.6f}")
    # s_t = time.perf_counter()
    w = 70
    h = 70
    center_points_flakes = get_center_coords(new_points_flakes, (w, h))
    # e_t = time.perf_counter()
    # print(f"get_center_coords time = {e_t - s_t:0.6f}")
    # s_t = time.perf_counter()
    # e_t = time.perf_counter()
    # print(f"drawing rectangles time = {e_t - s_t:0.6f}")
    # s_t = time.perf_counter()
    # cv2.imwrite(r'images\res.png', screen)
    # e_t = time.perf_counter()
    # print(f"saving image time = {e_t - s_t:0.6f}")

    for pt in center_points_flakes:
        # cv2.rectangle(screen, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 0)
        # Draw cross
        cv2.line(screen, (pt[0] - int(0.25 * w), pt[1]), (pt[0] + int(0.25 * w), pt[1]), (0, 0, 255), 1)
        cv2.line(screen, (pt[0], pt[1] - int(0.25 * w)), (pt[0], pt[1] + int(0.25 * w)), (0, 0, 255), 1)

    res = cv2.imwrite(r'images\screenshot.png', screen)
    print(f"screenshot.png res = {res}")
    res = cv2.imwrite(r'images\img_np.png', img_np)
    print(f"img_np.png res = {res}")
    res = cv2.imwrite(r'images\img_hsv.png', img_hsv)
    print(f"img_hsv.png res = {res}")
    res = cv2.imwrite(r'images\mask_flake.png', mask_flake)
    print(f"mask_flake.png res = {res}")
    res = cv2.imwrite(r'images\mask_bomb.png', mask_bomb)
    print(f"mask_bomb.png res = {res}")
    res = cv2.imwrite(r'images\mask_bomb_fuze.png', mask_bomb_fuze)
    print(f"mask_bomb_fuze.png res = {res}")
    print(f"get_objects_locations_by_hsv_mask() -> images saved.")

    return flake_exist and not bomb_exist and not bomb_fuze_exist


# def get_image_location(img_path: str, threshold: float = 0.7) -> tuple:
#     global monitor
#     # Replace 'image.png' with the path to your image file
#     template = cv2.imread(img_path, 0)
#     assert template is not None, "Image file could not be read, check with image path"
#     template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
#     template = cv2.Canny(template, 50, 200)
#     # w, h = template.shape[::-1]
#     # w, h = template.shape[0], template.shape[1]
#
#     # start = time.perf_counter()
#     # -----------------------------------------------------
#     with mss() as sct:
#         screenshot = sct.grab(monitor)
#         frame = np.array(screenshot)
#         screen = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         screen = cv2.Canny(screen, 50, 200)
#
#     # -----------------------------------------------------
#
#     # Find the location of the image on the screen
#     res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#
#     if max_val > threshold:  # Adjust the threshold as needed
#         # Get the center coordinates of the image
#         height, width = template.shape[:2]
#         center_x = max_loc[0] + (width / 2) + monitor["left"]
#         center_y = max_loc[1] + (height / 2) + monitor["top"]
#         # print(f"Image center coordinates: ({center_x}, {center_y})")
#         return int(center_x), int(center_y)
#     else:
#         # print("Image not found on the screen.")
#         return None


def get_image_location(img_path: str, screen_area: tuple, threshold: float = 0.5) -> tuple:

    def tuple_area_to_dictionary(area: tuple) -> dict:
        return {"left": area[0], "top": area[1], "width": area[2], "height": area[3]}

    lower_threshold = 50    # 50
    upper_threshold = 200   # 200
    screen_area_dict = tuple_area_to_dictionary(screen_area)
    # Replace 'image.png' with the path to your image file
    template = cv2.imread(img_path, 0)
    assert template is not None, "Image file could not be read, check with image path"
    template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    template = cv2.Canny(template, lower_threshold, upper_threshold)
    # w, h = template.shape[::-1]
    # w, h = template.shape[0], template.shape[1]

    # start = time.perf_counter()
    # -----------------------------------------------------
    with mss() as sct:
        screenshot = sct.grab(screen_area_dict)
        frame = np.array(screenshot)
        screen = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        screen = cv2.Canny(screen, lower_threshold, upper_threshold)

    # -----------------------------------------------------

    # Find the location of the image on the screen
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:  # Adjust the threshold as needed
        # Get the center coordinates of the image
        height, width = template.shape[:2]
        center_x = max_loc[0] + (width / 2) + screen_area_dict["left"]
        center_y = max_loc[1] + (height / 2) + screen_area_dict["top"]
        # print(f"Image center coordinates: ({center_x}, {center_y})")
        return int(center_x), int(center_y)
    else:
        # print("Image not found on the screen.")
        return None


def get_play_button_location(threshold: float = 0.8) -> tuple:
    global monitor
    # Replace 'image.png' with the path to your image file
    template = cv2.imread(r'images/play_button_00.png', 0)
    assert template is not None, "Image file could not be read, check with image path"
    template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    template = cv2.Canny(template, 50, 200)
    # w, h = template.shape[::-1]
    # w, h = template.shape[0], template.shape[1]

    # start = time.perf_counter()
    # -----------------------------------------------------
    with mss() as sct:
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        screen = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        screen = cv2.Canny(screen, 50, 200)

    # -----------------------------------------------------

    # Find the location of the image on the screen
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:  # Adjust the threshold as needed
        # Get the center coordinates of the image
        height, width = template.shape[:2]
        center_x = max_loc[0] + (width / 2) + monitor["left"]
        center_y = max_loc[1] + (height / 2) + monitor["top"]
        print(f"Center coordinates: ({center_x}, {center_y})")
        return int(center_x), int(center_y)
    else:
        print("Image not found on the screen.")
        return None


def get_image_points_test() -> tuple:  # TEST FUNCTION
    global monitor, app, threshold, unite_tolerance
    # Replace 'image.png' with the path to your image file
    # template = cv2.imread(r'images/play_button_00.png', 0)
    template = cv2.imread(r'images/Blum-01.png', 0)
    assert template is not None, "Image file could not be read, check with image path"
    template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    # template = cv2.Canny(template, 50, 200)
    # w, h = template.shape[::-1]
    w, h = template.shape[0], template.shape[1]

    start = time.perf_counter()
    # -----------------------------------------------------
    with mss() as sct:
        # Monitor 1 would be sct.monitors[1]
        # monitor = sct.monitors[2]  # Adjust the monitor index as needed
        # monitor = {'left': 1450, 'top': 370, 'width': 380, 'height': 660}

        s_t = time.perf_counter()
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        screen = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        e_t = time.perf_counter()
        print(f"grabbing screenshot time = {e_t - s_t:0.6f}")
        # screen = cv2.Canny(screen, 50, 200)

        # img = sct.grab(mon)
        # gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        # edged = cv2.Canny(gray, 50, 200)
    # -----------------------------------------------------

    # Find the location of the image on the screen
    # result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
    # (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
    # res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    s_t = time.perf_counter()
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    e_t = time.perf_counter()
    print(f"cv2.matchTemplate time = {e_t - s_t:0.6f}")
    # app = App()
    # threshold = float(app.screening_threshold_value.get())
    s_t = time.perf_counter()
    threshold_gap = 0.01
    # loc = np.where(res >= threshold and res < threshold + threshold_gap)
    loc = np.where((res >= threshold) & (res < threshold + threshold_gap))
    e_t = time.perf_counter()
    print(f"np.where time = {e_t - s_t:0.6f}")
    print(f"loc array length: {len(loc[0])}")

    # ------- Alternative way to use np.where() -------
    # res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    # threshold = 0.5
    # threshold_gap = 0.05
    # loc_lower = np.where(res >= threshold)
    # loc_upper = np.where(res < threshold + threshold_gap)
    # loc = np.intersect1d(loc_lower[0], loc_upper[0]), np.intersect1d(loc_lower[1], loc_upper[1])

    def unite_close_points(x_coords, y_coords, tolerance):
        clusters = {}

        for x, y in zip(x_coords, y_coords):
            found_cluster = False

            # Check if a cluster exists within the tolerance
            for cluster_center, cluster_points in clusters.items():
                cx, cy = cluster_center
                if math.sqrt((x - cx) ** 2 + (y - cy) ** 2) <= tolerance:
                    cluster_points.append((x, y))
                    new_center_x = sum(p[0] for p in cluster_points) / len(cluster_points)
                    new_center_y = sum(p[1] for p in cluster_points) / len(cluster_points)
                    clusters[cluster_center] = cluster_points
                    clusters[(new_center_x, new_center_y)] = clusters.pop(cluster_center)
                    found_cluster = True
                    break

            # If no cluster found, create a new cluster
            if not found_cluster:
                clusters[(x, y)] = [(x, y)]

        # Extract the center coordinates of each cluster
        # new_x_coords = []
        # new_y_coords = []
        new_coords = []
        for center, points in clusters.items():
            # new_x_coords.append(center[0])
            # new_y_coords.append(center[1])
            new_coords.append((int(center[0]), int(center[1])))

        # return new_x_coords, new_y_coords
        return new_coords

        # # Example usage
        # x_coords = [29, 29, 29, 29, 29, 29, 30, 30, 30, 30, 30, 30, 30, 30, 31, 31, 31, 31, 31, 31, 31, 31, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 34, 34, 34, 34, 34, 34, 34, 34, 34, 35, 35, 35, 35, 35, 35, 35, 35, 35, 36, 36, 36, 36, 36, 36, 36, 37, 37, 37, 37, 37, 139, 139, 139, 139, 139, 139, 139, 140, 140, 140, 140, 140, 140, 140, 140, 140, 141, 141, 141, 141, 141, 141, 141, 141, 141, 141, 142, 142]
        # y_coords = [211, 212, 213, 214, 215, 216, 210, 211, 212, 213, 214, 215, 216, 217, 210, 211, 212, 213, 214, 215, 216, 217, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 209, 210, 211, 212, 213, 214, 215, 216, 217, 209, 210, 211, 212, 213, 214, 215, 216, 217, 210, 211, 212, 213, 214, 215, 216, 211, 212, 213, 214, 215, 288, 289, 290, 291, 292, 293, 294, 287, 288, 289, 290, 291, 292, 293, 294, 295, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 285, 286]
        #
        # tolerance = 2
        #
        # new_x_coords, new_y_coords = unite_close_points(x_coords, y_coords, tolerance)
        # print("New x coordinates:", new_x_coords)
        # print("New y coordinates:", new_y_coords)

    def get_center_coords(points: tuple, size: tuple) -> list:
        center_points = []
        if len(points) > 0:
            for point in points:
                center_points.append(tuple([int(point[0] + size[0] / 2), int(point[1] + size[1] / 2)]))

        return center_points

    # unite_tolerance = 20
    s_t = time.perf_counter()
    print(f"unite_tolerance = {unite_tolerance}")
    new_points = unite_close_points(loc[1], loc[0], unite_tolerance)
    e_t = time.perf_counter()
    print(f"unite_close_points time = {e_t - s_t:0.6f}")
    s_t = time.perf_counter()
    center_points = get_center_coords(new_points, (w, h))
    e_t = time.perf_counter()
    print(f"get_center_coords time = {e_t - s_t:0.6f}")
    # test_rects = []
    # for pt in zip(*loc[::-1]):
    s_t = time.perf_counter()
    for pt in center_points:
        # cv2.rectangle(screen, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 0)
        # Draw cross
        cv2.line(screen, (pt[0] - int(0.25 * w), pt[1]), (pt[0] + int(0.25 * w), pt[1]), (0, 0, 255), 1)
        cv2.line(screen, (pt[0], pt[1] - int(0.25 * w)), (pt[0], pt[1] + int(0.25 * w)), (0, 0, 255), 1)

        # test_rects.append(pt)
    e_t = time.perf_counter()
    print(f"drawing rectangles time = {e_t - s_t:0.6f}")
    s_t = time.perf_counter()
    cv2.imwrite(r'images\res.png', screen)
    e_t = time.perf_counter()
    print(f"saving image time = {e_t - s_t:0.6f}")

    end = time.perf_counter()
    print(
        f"new_points length = {len(new_points)}, unite_tolerance = {unite_tolerance}, threshold = {threshold}, time = {end - start:0.6f}")

    return center_points

    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #
    # if max_val > threshold:  # Adjust the threshold as needed
    #     # Get the center coordinates of the image
    #     height, width = template.shape[:2]
    #     center_x = max_loc[0] + (width / 2) + monitor["left"]
    #     center_y = max_loc[1] + (height / 2) + monitor["top"]
    #     print(f"Center coordinates: ({center_x}, {center_y})")
    #     return int(center_x), int(center_y)
    # else:
    #     print("Image not found on the screen.")
    #     return None


class ObjectType:
    flake = "flake"
    bomb = "bomb"
    bluebird = "bluebird"


class DropObject:
    x = 0
    y = 0
    track_id = 0
    speed = 0.0

    def __init__(self, object_type: ObjectType, track_id: int, current_x: int, current_y: int, current_timestamp: time,
                 prev_x: int, prev_y: int, prev_timestamp: time):
        self.object_type = object_type
        self.x: int = current_x
        self.y: int = current_y
        # self.timestamp = current_timestamp
        self.track_id: int = track_id
        self.speed, self.vector = self.calculate_speed(current_timestamp, prev_x, prev_y, prev_timestamp)

    def calculate_speed(self, current_timestamp: time, prev_x: int, prev_y: int, prev_time: time) -> tuple:
        time_interval = current_timestamp - prev_time
        delta_x = self.x - prev_x
        delta_y = self.y - prev_y
        vector_length = math.sqrt(delta_x ** 2 + delta_y ** 2)
        speed = math.sqrt((self.x - prev_x) ** 2 + (self.y - prev_y) ** 2) / time_interval
        if vector_length > 0:
            vector = (delta_x / vector_length, delta_y / vector_length)
        else:
            vector = (0.0, 0.0)
        return speed, vector

    def get_click_position(self, current_timestamp: time):
        click_time = time.perf_counter()
        time_interval = click_time - current_timestamp

        # Calculate the current coordinates
        x_current = int(self.x + self.speed * time_interval * self.vector[0])
        y_current = int(self.y + self.speed * time_interval * self.vector[1])

        return x_current, y_current


def get_image_points() -> tuple:  # WORKING FUNCTION
    global monitor, app, threshold, unite_tolerance

    def multi_scale_template_matching(screen, template, scales):
        global threshold
        threshold_gap = 0.01
        results = []
        for scale in scales:
            resized = cv2.resize(template, None, fx=scale, fy=scale)
            res = cv2.matchTemplate(screen, resized, cv2.TM_CCOEFF_NORMED)
            # locations = np.where(res >= threshold)
            locations = np.where((res >= threshold) & (res < threshold + threshold_gap))
            for pt in zip(*locations[::-1]):
                t_width = int(template.shape[1] * scale)
                t_height = int(template.shape[0] * scale)
                results.append((pt, (t_width, t_height)))
        return results

    template = cv2.imread(r'images/Blum-01.png', 0)
    # template = cv2.imread(r'images/blum_flake_01.png', 0)
    assert template is not None, "Image file could not be read, check with image path"
    template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    # w, h = template.shape[0], template.shape[1]

    # start = time.perf_counter()
    with mss() as sct:
        # s_t = time.perf_counter()
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        screen = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # e_t = time.perf_counter()
        # print(f"grabbing screenshot time = {e_t - s_t:0.6f}")

    # Define scales and threshold
    scales = np.linspace(0.5, 1.1, 4)

    # Perform multi-scale template matching
    matches = multi_scale_template_matching(screen, template, scales)

    # res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    # threshold_gap = 0.01
    # loc = np.where((res >= threshold) & (res < threshold + threshold_gap))

    def unite_close_points(matches: tuple, tolerance):
        clusters = {}

        for coord, size in matches:
            found_cluster = False
            x = coord[0]
            y = coord[1]
            # Check if a cluster exists within the tolerance
            for cluster_center, cluster_points in clusters.items():
                (cx, cy), cs = cluster_center
                # if math.sqrt((x - cx) ** 2 + (y - cy) ** 2) <= tolerance and size[0] == cs[0] and size[1] == cs[1]:
                if math.sqrt((x - cx) ** 2 + (y - cy) ** 2) <= tolerance:
                    cluster_points.append(((x, y), size))
                    new_center_x, new_size_x = sum(p[0] for p, _ in cluster_points) / len(cluster_points), sum(
                        s[0] for _, s in cluster_points) / len(cluster_points)
                    new_center_y, new_size_y = sum(p[1] for p, _ in cluster_points) / len(cluster_points), sum(
                        s[1] for _, s in cluster_points) / len(cluster_points)
                    clusters[cluster_center] = cluster_points
                    clusters[((new_center_x, new_center_y), (new_size_x, new_size_y))] = clusters.pop(cluster_center)
                    found_cluster = True
                    break

            # If no cluster found, create a new cluster
            if not found_cluster:
                clusters[((x, y), size)] = [((x, y), size)]

        # Extract the center coordinates of each cluster
        # new_x_coords = []
        # new_y_coords = []
        new_coords = []
        for center, points in clusters.items():
            # new_x_coords.append(center[0])
            # new_y_coords.append(center[1])
            new_coords.append(((int(center[0][0]), int(center[0][1])), (int(center[1][0]), int(center[1][1]))))

        # return new_x_coords, new_y_coords
        return new_coords

        # # Example usage
        # x_coords = [29, 29, 29, 29, 29, 29, 30, 30, 30, 30, 30, 30, 30, 30, 31, 31, 31, 31, 31, 31, 31, 31, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 34, 34, 34, 34, 34, 34, 34, 34, 34, 35, 35, 35, 35, 35, 35, 35, 35, 35, 36, 36, 36, 36, 36, 36, 36, 37, 37, 37, 37, 37, 139, 139, 139, 139, 139, 139, 139, 140, 140, 140, 140, 140, 140, 140, 140, 140, 141, 141, 141, 141, 141, 141, 141, 141, 141, 141, 142, 142]
        # y_coords = [211, 212, 213, 214, 215, 216, 210, 211, 212, 213, 214, 215, 216, 217, 210, 211, 212, 213, 214, 215, 216, 217, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 209, 210, 211, 212, 213, 214, 215, 216, 217, 209, 210, 211, 212, 213, 214, 215, 216, 217, 210, 211, 212, 213, 214, 215, 216, 211, 212, 213, 214, 215, 288, 289, 290, 291, 292, 293, 294, 287, 288, 289, 290, 291, 292, 293, 294, 295, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 285, 286]
        #
        # tolerance = 2
        #
        # new_x_coords, new_y_coords = unite_close_points(x_coords, y_coords, tolerance)
        # print("New x coordinates:", new_x_coords)
        # print("New y coordinates:", new_y_coords)

    def get_center_coords(points: tuple) -> list:
        c_points = []
        if len(points) > 0:
            for point, size in points:
                # w = int(template.shape[1] * scale)
                # h = int(template.shape[0] * scale)
                c_points.append(tuple([int(point[0] + size[0] / 2), int(point[1] + size[1] / 2)]))
        return c_points

    # unite_tolerance = 20
    # s_t = time.perf_counter()
    # print(f"unite_tolerance = {unite_tolerance}")
    # new_points = unite_close_points(loc[1], loc[0], unite_tolerance)
    new_points = unite_close_points(matches=matches, tolerance=unite_tolerance)
    # new_points = matches
    # e_t = time.perf_counter()
    # print(f"unite_close_points time = {e_t - s_t:0.6f}")
    # s_t = time.perf_counter()
    center_points = get_center_coords(new_points)
    # e_t = time.perf_counter()
    # print(f"get_center_coords time = {e_t - s_t:0.6f}")
    # s_t = time.perf_counter()
    # e_t = time.perf_counter()
    # print(f"drawing rectangles time = {e_t - s_t:0.6f}")
    # s_t = time.perf_counter()
    # cv2.imwrite(r'images\res.png', screen)
    # e_t = time.perf_counter()
    # print(f"saving image time = {e_t - s_t:0.6f}")

    # end = time.perf_counter()
    # print(f"new_points length = {len(new_points)}, unite_tolerance = {unite_tolerance}, threshold = {threshold}, time = {end - start:0.6f}")

    return center_points, frame


def wait_for_image_on_screen(img_path: str, to_appear: bool = True, threshold: float = 0.7,
                             start_detection: bool = True, timeout: int = 10) -> tuple:
    global auto_start_running, auto_end_running, monitor

    # def convert_dict_area_to_tuple(d: dict) -> tuple:
    #     return tuple([tuple(d[k]) for k in d])

    def convert_dict_area_to_tuple(d: dict) -> tuple:
        top_addition = 0    # 65
        res = (d["left"], d["top"] - top_addition, d["width"], d["height"])
        return res

    screen_area = convert_dict_area_to_tuple(monitor)

    if to_appear:
        # Wait for image to appear on screen
        image_location = get_image_location(img_path, screen_area=screen_area, threshold=threshold)
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        print(f"Waiting for image to appear on screen ...")
        # while not image_location and running:
        timeout_start = time.perf_counter()
        waiting_time_seconds = 0
        while not image_location and waiting_time_seconds < timeout:
            match start_detection:
                case True:
                    if not auto_start_running:
                        break
                case False:
                    if not auto_end_running:
                        break
            image_location = get_image_location(img_path, screen_area=screen_area, threshold=threshold)
            time.sleep(0.1)
            timeout_end = time.perf_counter()
            waiting_time_seconds = timeout_end - timeout_start

        listener.stop()
        if image_location:
            print(f"Detection successful at {image_location}")
            return True, image_location
        elif not (start_detection and auto_start_running) or not (not start_detection and auto_end_running):
            print(f"Detection canceled")
            return False, None
    else:
        # Wait for image to disappear from screen
        # Wait for image to appear on screen
        image_location = get_image_location(img_path, screen_area=screen_area, threshold=threshold)
        print(f"Waiting for image to disappear on screen at {image_location} ...")
        while image_location:
            match start_detection:
                case True:
                    if not auto_start_running:
                        break
                case False:
                    if not auto_end_running:
                        break
            image_location = get_image_location(img_path, screen_area=screen_area, threshold=threshold)
            time.sleep(0.001)
        if not image_location:
            print(f"Detection successful")
            return True, None
        elif not (start_detection and auto_start_running) or not (not start_detection and auto_end_running):
            print(f"Detection canceled")
            return False, None


def start_clicker(use_click_button: bool = False):
    # global clicker_thread_1, clicker_thread_2, clicker_thread_3, clicker_thread_4
    # global clicker_thread_5, clicker_thread_6, clicker_thread_7, clicker_thread_8, \
    global click_distance, clicker_threads_no
    # -----------------------------
    if use_click_button:
        play_button_location = get_play_button_location(threshold=0.7)
        if play_button_location:
            # print(f"Clicking Play button to start ...")
            x, y = play_button_location
            click(x, y, just_move=True)
            print(f"Click Play button to start ...")

            # print(f"Click Play button to start ...")
            # Wait until button disappear
            while play_button_location:
                play_button_location = get_play_button_location(threshold=0.7)
                # x, y = play_button_location
                #     pyautogui.click(x, y)
                #     # click_2(x, y)
                time.sleep(0.2)
                # win32api.SetCursorPos((x, y))
                # click(x, y, just_move=True)
        else:
            print(f"Play button not found. Exiting clicker ...")
            return
    # -----------------------------
    print(f"Starting clicker ...")
    # clicker_running = True
    threads_no = int(clicker_threads_no)
    click_shifts = []
    for i in range(threads_no):
        if i % 2 == 0:
            click_shifts.append((0, int(i * click_distance)))
        else:
            click_shifts.append((int(click_distance / 2), int(i * click_distance)))

    clicker_threads = []
    for i, click_shift in enumerate(click_shifts):
        clicker_threads.append(Thread(target=start_click_thread, args=(click_shift, i + 1)))

    print("Starting clicker threads...")
    if len(clicker_threads) > 0:
        for thread in clicker_threads:
            thread.start()
            time.sleep(0.01)
    # print("Starting clicker thread_2...")
    # clicker_thread_2.start()
    print("Clicker threads started")


def stop_clicker():
    global clicker_running
    print("Stopping clicker ...")
    # app.update_clicker_status_value(value=clicker_running.__str__())
    # app.update()
    # time.sleep(2)
    clicker_running = False
    # app = App()
    app.update_clicker_status_value(value=clicker_running.__str__())
    # app.update()
    # print(f"Clicker status updated to {clicker_running}")


def start_click_thread(click_shift: tuple = (0, 0), thread_no: int = 0):
    global clicker_running, click_points, test_frame_window, current_objects, previous_objects, monitor
    thread_no = thread_no
    dc = win32gui.GetDC(0)
    clicker_running = True
    # app = App()
    if app is not None:
        app.update_clicker_status_value(value=clicker_running.__str__())
        app.update()
    # click_interval = 0.01

    # Create a listener to monitor keyboard input
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    class RGBColor:
        def __init__(self, red=0, green=0, blue=0):
            self.red = red
            self.green = green
            self.blue = blue

    def is_even(num: int):
        return num % 2 == 0

    def get_rgb_color(int_color: int) -> RGBColor:
        # Extract the RGB components from the pixel color value
        red = int_color & 0xff
        green = (int_color >> 8) & 0xff
        blue = (int_color >> 16) & 0xff

        color = RGBColor(red, green, blue)

        return color

    def pixel_is_out_of_monitor(pixel: tuple) -> bool:
        global monitor
        some_area_to_exclude = 75
        some_area_to_include = 20
        if (pixel[0] < monitor["left"] or pixel[0] >= monitor["left"] + monitor["width"]
                or pixel[1] < monitor["top"] + some_area_to_exclude or pixel[1] >= monitor["top"] + monitor["height"] + some_area_to_include):
            return True
        else:
            return False

    # click_coordinates = get_click_coordinates(click_shift[0], click_shift[1])

    while clicker_running:
        cur_timestamp = current_objects["timestamp"]
        c_obj = current_objects["objects"].copy()
        # c_obj.sort(key=lambda dropobj: dropobj.y, reverse=True)
        sorted_objects = sorted(c_obj, key=lambda dropobj: dropobj.y, reverse=True)
        # if not is_even(thread_no):
        #     sorted_objects = reversed(sorted_objects)

        for obj in sorted_objects:
            # obj = DropObject()
            click_point = obj.get_click_position(cur_timestamp)
            click_point = click_point[0] + monitor["left"], click_point[1] + monitor["top"]
            # click_point[0], click_point[1] = int(check_point[0]), int(check_point[1])
            pixel_out = pixel_is_out_of_monitor(click_point)
            if not pixel_out:
                print(f"pixel is IN monitor at x={click_point[0]}, y={click_point[1]}")
                click_confirmed = is_click_confirmed(click_point)
                if click_confirmed and clicker_running:
                    print(f"******** CLICKING ******** at x={click_point[0]}, y={click_point[1]}")
                    # -------------------------------------
                    click(click_point[0], click_point[1], just_move=False, change_cursor=False)
                    # draw_cross_frm(test_frame_window, click_point, (0, 255, 255), 2)
                    # cv2.imshow("frm",test_frame_window)
                    # -------------------------------------
                else:
                    print(f"!!!!!!!!! BOMB detected !!!!!!!!!!! at x={click_point[0]}, y={click_point[1]}")
            else:
                pass
                # print(f"pixel is OUT of monitor at x={click_point[0]}, y={click_point[1]}")

        # click_coordinates = click_points["flakes"]
        # screening_timestamp = click_points["timestamp"]
        # # print(f"click_coordinates length = {len(click_coordinates)}")
        # for coordinate in click_coordinates:
        #     click_point = recalculate_click_position(coordinate, screening_timestamp)
        #     pixel_out = pixel_is_out_of_monitor(click_point)
        #     if not pixel_out:
        #         print(f"pixel is IN monitor at x={click_point[0]}, y={click_point[1]}")
        #         click_confirmed = is_click_confirmed(click_point)
        #         if click_confirmed:
        #             print(f"******** CLICKING ******** at x={click_point[0]}, y={click_point[1]}")
        #             # -------------------------------------
        #             click(click_point[0], click_point[1], just_move=False, change_cursor=False)
        #             # -------------------------------------
        #         else:
        #             print(f"!!!!!!!!! BOMB detected !!!!!!!!!!! at x={click_point[0]}, y={click_point[1]}")
        #     else:
        #         print(f"pixel is OUT of monitor at x={click_point[0]}, y={click_point[1]}")
        # click(coordinate[0], coordinate[1], just_move=True)
        # time.sleep(click_interval / 100)
        # end = time.perf_counter()
        # print(f"==================== Thread {thread_no}: {current_time()} LINE CYCLE timelapse ... ({end - start:.6f})")
    # Stop the keyboard listener
    listener.stop()
    print("Clicker listener stopped.")
    print(f"Clicker stopped")


def get_square_extremums():
    global click_points

    flakes_points_no = len(click_points["flakes"])
    bombs_points_no = len(click_points["bombs"])
    bluebirds_points_no = len(click_points["bluebirds"])

    min_flake_square = 10000
    max_flake_square = 0
    if flakes_points_no > 0:
        for flake_point in click_points["flakes"]:
            square = flake_point[2]
            if min_flake_square > square:
                min_flake_square = square
            if max_flake_square < square:
                max_flake_square = square

    min_bomb_square = 10000
    max_bomb_square = 0
    if bombs_points_no > 0:
        for bomb_point in click_points["bombs"]:
            square = bomb_point[2]
            if min_bomb_square > square:
                min_bomb_square = square
            if max_bomb_square < square:
                max_bomb_square = square

    min_bluebird_square = 10000
    max_bluebird_square = 0
    if bluebirds_points_no > 0:
        for bluebird_point in click_points["bluebirds"]:
            square = bluebird_point[2]
            if min_bluebird_square > square:
                min_bluebird_square = square
            if max_bluebird_square < square:
                max_bluebird_square = square

    return {"flakes": {"min": min_flake_square, "max": max_flake_square},
            "bombs": {"min": min_bomb_square, "max": max_bomb_square},
            "bluebirds": {"min": min_bluebird_square, "max": max_bluebird_square}}


def update_square_extremums(final_extremums: dict, current_extremums: dict):
    if final_extremums["flakes"]["min"] > current_extremums["flakes"]["min"]:
        final_extremums["flakes"]["min"] = current_extremums["flakes"]["min"]
    if final_extremums["flakes"]["max"] < current_extremums["flakes"]["max"]:
        final_extremums["flakes"]["max"] = current_extremums["flakes"]["max"]

    if final_extremums["bombs"]["min"] > current_extremums["bombs"]["min"]:
        final_extremums["bombs"]["min"] = current_extremums["bombs"]["min"]
    if final_extremums["bombs"]["max"] < current_extremums["bombs"]["max"]:
        final_extremums["bombs"]["max"] = current_extremums["bombs"]["max"]

    if final_extremums["bluebirds"]["min"] > current_extremums["bluebirds"]["min"]:
        final_extremums["bluebirds"]["min"] = current_extremums["bluebirds"]["min"]
    if final_extremums["bluebirds"]["max"] < current_extremums["bluebirds"]["max"]:
        final_extremums["bluebirds"]["max"] = current_extremums["bluebirds"]["max"]

    return final_extremums


# Using opencv image search
def main_v_approximate_speed():
    global screening_running, monitor, click_points, click_cycle_done

    screening_running = True
    # app = App()
    if app is not None:
        app.update_screening_status_value(screening_running.__str__())
        app.update()

    # Create a listener to monitor keyboard input
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    print("Press 'Esc' to quit.")

    # -------------- TEST IMAGE SEARCH BY OPENCV -----------------
    print(f"\n**************** Starting screening cycle ... ****************")
    while screening_running:
        cycle_start = time.perf_counter()
        image_points = get_image_points()
        image_points_no = len(image_points)
        print(f"image_points_no: {image_points_no}")
        if image_points_no > 0:
            click_points["flakes"] = image_points
            click_points["timestamp"] = cycle_start

        # ------------------------------------------------------------
        cycle_end = time.perf_counter()
        print(f"Time of cycle: {cycle_end - cycle_start:0.6f} sec")
        print(f"----------------------------------------------------")

    # cv2.destroyAllWindows()
    # Stop the keyboard listener
    listener.stop()
    print("Screening listener stopped.")
    print(f"----------------- FINISHED ---------------------")


test_frame_window = None


def main():
    global screening_running, monitor, click_points, click_cycle_done, current_objects, previous_objects
    global test_frame_window

    screening_running = True
    # app = App()
    if app is not None:
        app.update_screening_status_value(screening_running.__str__())
        app.update()

    # Create a listener to monitor keyboard input
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    print("Press 'Esc' to quit.")

    # -------------- TEST IMAGE SEARCH BY OPENCV -----------------
    def get_track_id_valid_area(point: tuple, timestamp: time, prev_timestamp: time) -> tuple:
        # Calculate approximate speed and area height
        min_overall_time = 2.0
        max_overall_distance = 600
        max_overall_speed = max_overall_distance / min_overall_time
        cur_time = timestamp  # time.perf_counter()
        time_delta = cur_time - prev_timestamp
        area_height = max_overall_speed * time_delta
        area_width = 20
        area_width_delta = int(area_width / 2)
        height_addition = 5
        x, y = point[0], point[1]
        area = (x - area_width_delta, y - area_height - height_addition, area_width, y + height_addition)
        return area

    def is_point_in_area(point: tuple, area: tuple) -> bool:
        x, y = point[0], point[1]
        x_min, y_min, width, height = area
        if x_min < x < x_min + width and y_min < y < y_min + height:
            return True
        return False

    def get_track_id(point: tuple, timestamp: time) -> tuple:
        global previous_objects, track_id_max
        track_id = track_id_max + 1
        track_id_point = point
        point_found = False
        if len(previous_objects["objects"]) > 0:
            prev_timestamp = previous_objects['timestamp']
            check_area = get_track_id_valid_area(point, timestamp, prev_timestamp)
            # Get the nearest object to point in previous_objects
            min_distance = math.sqrt(check_area[2] ** 2 + check_area[3] ** 2)
            for prev_obj in previous_objects["objects"]:
                prev_point = (prev_obj.x, prev_obj.y)
                if is_point_in_area(prev_point, check_area):
                    point_found = True
                    cur_distance = math.sqrt((prev_point[0] - point[0]) ** 2 + (prev_point[1] - point[1]) ** 2)
                    if cur_distance < min_distance:
                        min_distance = cur_distance
                        track_id = prev_obj.track_id
                        track_id_point = prev_point
            if point_found:
                return track_id, track_id_point, point_found
            else:
                track_id_max += 1
                return track_id_max, track_id_point, point_found
        else:
            return track_id_max, track_id_point, point_found

    def get_current_objects(points: list, timestamp: time):
        global current_objects, previous_objects
        current_objects = {"objects": [], "timestamp": 0.0}
        for point in points:
            # Search for track_id in previous_objects
            track_id, track_id_point, track_id_point_found = get_track_id(point, timestamp)
            if track_id_point_found:
                pass
            current_objects["objects"].append(DropObject(object_type=ObjectType.flake,
                                                         track_id=track_id,
                                                         current_x=point[0],
                                                         current_y=point[1],
                                                         current_timestamp=timestamp,
                                                         prev_x=track_id_point[0],
                                                         prev_y=track_id_point[1],
                                                         prev_timestamp=previous_objects["timestamp"]))
            current_objects["timestamp"] = timestamp
        return

    def draw_cross_frm(frm, point: tuple, color: tuple, thickness: int):
        x, y = point[0], point[1]
        cv2.line(frm, (x - 10, y), (x + 10, y), color, thickness)
        cv2.line(frm, (x, y - 10), (x, y + 10), color, thickness)

    def draw_text(frm, point: tuple, text: str, color: tuple = (255, 255, 255), font_scale: int = 0.5,
                  thickness: int = 1):

        # font = cv2.FONT_HERSHEY_SIMPLEX
        font = cv2.FONT_HERSHEY_TRIPLEX
        # Get the size of the text
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)

        size = 10
        # Calculate position to place the text (slightly offset from the cross center)
        text_x = point[0] + size + 5
        text_y = point[1] + text_height // 2

        x, y = text_x, text_y
        cv2.putText(frm, text, (x, y), font, font_scale, color, thickness)

    print(f"\n**************** Starting screening cycle ... ****************")
    # *************************** TESTING ********************************
    # cap = cv2.VideoCapture("video/XRecorder_13072024_173115.mp4")
    while screening_running:
        cycle_start = time.perf_counter()
        image_points, frame = get_image_points()
        image_points_no = len(image_points)
        # print(f"image_points_no: {image_points_no}")
        # ret, frame = cap.read()
        # Convert RGB to BGR (OpenCV uses BGR)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        test_frame_window = frame
        if image_points_no > 0:
            previous_objects = current_objects.copy()
            # click_points["flakes"] = image_points
            # click_points["timestamp"] = cycle_start
            # Convert image_points to DropObjects
            get_current_objects(points=image_points, timestamp=cycle_start)

            # for obj in current_objects["objects"]:
            #     # Draw the object
            #     draw_cross_frm(frame, (obj.x, obj.y), (0, 0, 255), 1)
            #     draw_text(frame, (obj.x, obj.y), f"{obj.track_id}")
        # ------------------------------------------------------------
        #     cv2.imshow("Screenshot frame", frame)
        cycle_end = time.perf_counter()
        # print(f"Time of cycle: {cycle_end - cycle_start:0.6f} sec")
        # print(f"----------------------------------------------------")

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    cv2.destroyAllWindows()
    # Stop the keyboard listener
    listener.stop()
    print("Screening listener stopped.")
    print(f"----------------- FINISHED ---------------------")


def on_game_status_change(game_status: bool):
    app.update_game_value(game_status.__str__())
    pass


def on_session_status_change(session_status: bool):
    app.update_game_session_value(session_status.__str__())
    pass
    # app.


def on_monitoring_status_change(monitoring_status: bool):
    app.update_game_session_monitoring_value(monitoring_status.__str__())
    pass
    # app.


def init_kwargs():
    # Functions
    kwargs["get_telegram_window"] = get_telegram_window
    kwargs["get_screen_area"] = get_screen_area
    kwargs["on_game_session_start_time_change"] = on_game_session_start_time_change
    kwargs["on_games_per_session_no_change"] = on_games_per_session_no_change
    kwargs["on_pause_between_games_change"] = on_pause_between_games_change
    kwargs["on_threshold_changed"] = on_threshold_changed
    kwargs["on_unite_tolerance_changed"] = on_unite_tolerance_changed
    kwargs["on_clicker_threads_no_changed"] = on_clicker_threads_no_changed
    kwargs["on_entry_enter"] = on_entry_enter
    kwargs["start_game_session"] = start_game_session
    kwargs["stop_game_session"] = stop_game_session
    kwargs["start_screening"] = start_screening
    kwargs["stop_screening"] = stop_screening
    kwargs["start_clicker"] = start_clicker
    kwargs["stop_clicker"] = stop_clicker
    kwargs["get_back_to_home_page"] = get_back_to_home_page
    kwargs["is_home_page"] = is_home_page
    # Variables
    kwargs["monitor"] = monitor
    kwargs["threshold"] = threshold
    kwargs["unite_tolerance"] = unite_tolerance
    kwargs["clicker_threads_no"] = clicker_threads_no
    kwargs["games_per_session_no"] = games_per_session_no
    kwargs["pause_between_games_seconds"] = pause_between_games_seconds
    kwargs["game_session_start_time"] = game_session_start_time
    kwargs["telegram_window"] = telegram_window
    
    # Statuses
    kwargs["clicker_running"] = clicker_running
    kwargs["is_game_session_monitoring_running"] = game_monitoring.is_monitoring_running
    kwargs["is_game_session_running"] = game_monitoring.is_session_running
    kwargs["is_game_running"] = game_monitoring.is_game_running
    kwargs["auto_start_running"] = auto_start_running
    kwargs["auto_end_running"] = auto_end_running
    kwargs["screening_running"] = screening_running


game_monitoring = game_session.GameMonitoring(auto_start, on_game_status_change, on_session_status_change, on_monitoring_status_change,
                                              game_session_start_time, games_per_session_no, pause_between_games_seconds)
init_kwargs()
app = user_interface.App(kwargs=kwargs)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # app = App()
    # global screening_thread
    # init_kwargs()
    load_ui()
    update_ui()

    app.mainloop()

    # if screening_thread is not None:
    #     if screening_thread.is_alive():
    #         screening_thread.join()
    print(f"__main__ FINISHED")
    # main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
