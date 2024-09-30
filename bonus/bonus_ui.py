import schedule
import customtkinter as ctk
from settings_manager import SettingsManager
from datetime import datetime, date, timedelta, time as dtime
import ctk_widgets


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

        self.session_start_entry = ctk_widgets.CTkEntryEx(master=self, row=autostart_row,
                                                     title="Session start:",
                                                     setting_name="bonus_start_time",
                                                     value_changed_callback=self.on_start_time_return,
                                                     default_value="08:00")

        # autostart_row += 2
        lbl_font = ("Bahnschrift Light Condensed", 13)

        # self.monitoring_button = ctk.CTkButton(master=self, text="START", command=self.start_monitoring, height=56)
        # self.monitoring_button.grid(row=autostart_row, column=0, pady=pady, padx=padx, sticky="ew")

        autostart_row += 1
        self.session_switch = ctk_widgets.CTkSwitchEx(master=self, row=autostart_row, title="Monitoring:",
                                                 setting_name="bonus_monitoring",
                                                 value_changed_callback=self.monitoring_switched,
                                                 default_value="OFF")


        # Monitoring running
        autostart_row += 1
        self.session_monitoring_state = ctk_widgets.CTkStateLabel(master=self, row=autostart_row, title="Monitoring:")

        self.session_switch.switch_event()
        # autostart_row += 1

    def monitoring_switched(self, state):
        # state = self.session_switch.switch_variable.get()
        if state == "OFF":
            self.stop_monitoring(None)
        elif state == "ON":
            self.start_monitoring(None)
        self.session_monitoring_state.update_state(state)

    def start_monitoring(self, event):
        print(f"start_monitoring event: {event}")

        return

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

    def stop_monitoring(self, event):
        print(f"stop_monitoring event: {event}")
        return


    def on_start_time_return(self, event):

        pass

    def on_focus(self, event):
        print(f"on_focus event: {event}")
        pass
