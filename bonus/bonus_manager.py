from threading import Thread
import win32gui
import win32con
import win32process
import win32api


class BonusTask(Thread):
    def __init__(self, state_update_callback: callable, telegram_window_handle: int):
        super().__init__()
        self.is_running = False
        self.state_update_callback = state_update_callback
        self.telegram_window_handle = telegram_window_handle

    def stop(self):
        self.is_running = False
        self.state_update_callback(self.state_update_callback(self.is_running.__str__()))
        pass

    def run(self):
        self.is_running = True
        self.state_update_callback(self.state_update_callback(self.is_running.__str__()))
        print(f"Bonus task running ...")
        # TODO: Implement bonus task logic
        # Click (to focus) Telegram window
        if set_foreground_window(self.telegram_window_handle):
            print(f"Telegram window focused.")
            # Send keyboard F5 key
            send_key_press(self.telegram_window_handle, win32con.VK_F5)  # Send F5 key press
        else:
            print(f"Failed to focus Telegram window.")
            return
        # Wait for Continue button to appear
        # Click Continue button
        # Wait for Home page to appear
        print(f"Bonus task completed.")
        pass


def set_foreground_window(hwnd):
    """
    Sets the specified window to the foreground.

    Args:
        hwnd (int): The window handle (hwnd) of the window to set to the foreground.

    Returns:
        bool: True if the window was set to the foreground successfully, False otherwise.
    """
    try:
        # Get the process ID of the target window
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]

        # Get the current thread ID
        current_thread_id = win32api.GetCurrentThreadId()

        # Attach the window to the calling thread
        win32process.AttachThreadInput(current_thread_id, pid, True)

        # Set the window to the foreground
        win32gui.SetForegroundWindow(hwnd)

        # Detach the window from the calling thread
        # win32process.AttachThreadInput(win32con.ATTACH_PARENT_PROCESS, None)
        win32process.AttachThreadInput(current_thread_id, pid, False)

        return True
    except Exception as e:
        print(f"Error setting window to foreground: {e}")
        return False


def send_key_press(hwnd, key_code):
    """
    Sends a key press to the specified window.

    Args:
        hwnd (int): The window handle (hwnd) of the window to send the key press to.
        key_code (int): The virtual key code of the key to send.
    """
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, key_code, 0)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, key_code, 0)

# Example usage
# target_hwnd = 0x12345  # Replace with the actual hwnd of the target window
# if set_foreground_window(target_hwnd):
#     print("Window set to foreground successfully")
#     # Send the F5 key to refresh the window
#     # ...
# else:
#     print("Failed to set window to foreground")

