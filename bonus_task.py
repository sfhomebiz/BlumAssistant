
from threading import Thread, Event
import customtkinter as ctk
from settings_manager import SettingsManager
from datetime import datetime, date, timedelta, time as dtime
import time
import schedule


class BonusMonitoring(Thread):
    def __init__(self, state_update_callback: callable):
        super().__init__(target=self.bonus_monitoring_thread)
        self.is_monitoring_running = False
        # self.bonus_task_callback = bonus_task_callback
        self.state_update_callback = state_update_callback

    def run(self):
        self.is_monitoring_running = True
        self.state_update_callback(self.is_monitoring_running.__str__())
        while self.is_monitoring_running:
            schedule.run_pending()
            time.sleep(1)
        pass

    def stop(self):
        self.is_monitoring_running = False
        self.state_update_callback(self.is_monitoring_running.__str__())
        self.join()
        pass


class BonusTask(Thread):
    def __init__(self, start_time: dtime, state_update_callback: callable):
        self.start_time = start_time
        self.is_bonus_task_running = False
        self.state_update_callback = state_update_callback

    def stop(self):
        self.is_bonus_task_running = False
        self.state_update_callback(self.state_update_callback(self.is_bonus_task_running.__str__()))
        pass

    def run(self):
        self.is_bonus_task_running = True
        self.state_update_callback(self.state_update_callback(self.is_bonus_task_running.__str__()))
        print(f"Bonus task running ...")
        # TODO: Implement bonus task logic
        # Click (to focus) Telegram window
        # Send keyboard F5 key
        # Wait for Continue button to appear
        # Click Continue button
        # Wait for Home page to appear
        print(f"Bonus task completed.")
        pass


class BonusesUI(ctk.CTkFrame):
    def __init__(self, master, border_width=1):
        super().__init__(master=master, border_width=border_width)
        self.settings = SettingsManager("settings.json")
        autostart_row = 0
        pady = 5
        padx = 5
        self.bonus_title_label = ctk.CTkLabel(master=self, text="Daily bonus",
                                              bg_color="transparent", fg_color="grey", corner_radius=5,
                                              text_color="yellow")
        self.bonus_title_label.grid(row=autostart_row, column=0, pady=pady, padx=padx, sticky="ew", columnspan=2)

        # ---------------------------------
        # Autostart options
        # ---------------------------------
        # game_session_start_time
        autostart_row += 1
        lbl_font = ("Bahnschrift Light Condensed", 13)
        self.bonus_start_time_label = ctk.CTkLabel(master=self, text="Session start:", font=lbl_font, height=20)
        self.bonus_start_time_label.grid(row=autostart_row, column=0, pady=pady * 0.5, padx=2 * padx, sticky="w")
        # self.screening_threshold_value = ctk.CTkEntry(master=self.screening_frame, width=5)
        self.bonus_start_time_value = ctk.CTkEntry(master=self, width=50, justify="center")
        # self.game_session_start_time_value.insert(0, threshold.__str__())
        self.bonus_start_time_value.grid(row=autostart_row, column=1, pady=pady * 0.5, padx=padx, sticky="e")
        self.bonus_start_time_value.bind("<Return>", self.on_start_time_return)
        self.bonus_start_time_value.bind("<FocusIn>", self.on_focus)

        self.monitoring_button = ctk.CTkButton(master=self, text="START", command=self.start_monitoring, height=56)
        self.monitoring_button.grid(row=autostart_row, column=0, pady=pady, padx=padx, sticky="ew")

        # Monitoring running
        autostart_row += 1
        self.bonus_task_monitoring_label_title = ctk.CTkLabel(master=self, text="Monitoring", width=60,
                                                                compound="right", anchor="e")
        self.bonus_task_monitoring_label_value = ctk.CTkLabel(master=self,
                                                                text="getting value ...", width=60, compound="left",
                                                                anchor="w", height=24, corner_radius=11)
        self.bonus_task_monitoring_label_title.grid(row=autostart_row, pady=0, padx=padx, sticky="w")
        self.bonus_task_monitoring_label_value.grid(row=autostart_row, pady=0, padx=padx, sticky="e")

        # Bonus task running
        autostart_row += 1
        self.bonus_task_label_title = ctk.CTkLabel(master=self, text="Session", width=60,
                                                                compound="right", anchor="e")
        self.bonus_task_label_value = ctk.CTkLabel(master=self,
                                                                text="...", width=60, compound="left",
                                                                anchor="w", height=24, corner_radius=11)
        self.bonus_task_label_title.grid(row=autostart_row, pady=0, padx=padx, sticky="w")
        self.bonus_task_label_value.grid(row=autostart_row, pady=0, padx=padx, sticky="e")


    def start_monitoring(self, event):

        # Schedule the task to run daily at 08:00
        schedule.every().day.at("08:00").do(self.task_to_run)

        global app, game_session_start_time
        # app = App()
        print(f"Event occured: {event}")
        try:
            time_str = app.game_session_start_time_value.get()
            game_session_start_time = datetime.strptime(time_str, "%H:%M").time()
            self.settings.set_setting('game_session_start_time', time_str)
            self.settings.save_settings()
            print(f"game_session_start_time value set to {time_str}.")
            # Update the result or perform any other actions
            # game_monitoring.session_start_time = game_session_start_time
        except ValueError:
            print(f"Invalid value entered. game_session_start_time value set to {str(game_session_start_time.strftime('%H:%M'))}.")
            # Handle the case when the input is not a valid number
            pass


    def on_start_time_return(self):

        pass

    def on_focus(self):
        pass


def seconds_to_time_string(seconds: int) -> str:
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def load_last_run(self):
    # print(f"Loading last run ...")
    result = self.settings.get_setting('bonus_task_last_run')
    if result is None:
        print(f"bonus_task_last_run is None.")
        return None
    # print(f"last run is {datetime.fromisoformat(result)}")
    return datetime.fromisoformat(result)
    pass


def save_last_run(self):
    print(f"Saving last run ... {datetime.now().isoformat()}")
    self.settings.set_setting('bonus_task_last_run', datetime.now().isoformat())
    self.settings.save_settings()
    print(f"save_last_run() completed.")
    pass
