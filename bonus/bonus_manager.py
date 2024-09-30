from threading import Thread
import win32gui
import win32con


class BonusTask(Thread):
    def __init__(self, state_update_callback: callable):
        self.is_running = False
        self.state_update_callback = state_update_callback

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
        # Send keyboard F5 key
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
        # Attach the window to the calling thread
        win32gui.AttachThreadInput(win32con.ATTACH_PARENT_PROCESS, win32gui.GetWindowThreadProcessId(hwnd, None)[1])

        # Set the window to the foreground
        win32gui.SetForegroundWindow(hwnd)

        # Detach the window from the calling thread
        win32gui.AttachThreadInput(win32con.ATTACH_PARENT_PROCESS, None)

        return True
    except Exception as e:
        print(f"Error setting window to foreground: {e}")
        return False

# Example usage
# target_hwnd = 0x12345  # Replace with the actual hwnd of the target window
# if set_foreground_window(target_hwnd):
#     print("Window set to foreground successfully")
#     # Send the F5 key to refresh the window
#     # ...
# else:
#     print("Failed to set window to foreground")

