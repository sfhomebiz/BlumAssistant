import customtkinter as ctk
from customtkinter import CTkCanvas
from threading import Thread, get_ident
import queue
from bonus.bonus_ui import BonusesUI


class ScreenAreaAutoStatus:
    OK = "True"
    Failed = "False"
    Processing = "Processing"


class ScreenAreaAuto:
    # status = ScreenAreaAutoStatus.Failed
    def __init__(self):
        self.status = ScreenAreaAutoStatus.Failed


class App(ctk.CTk):
    # screen_area_options_value_label = None
    # screening_status_value_label = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        global threshold
        padx = 5
        pady = 5

        self.kwargs = kwargs["kwargs"]

        self.screen_area_auto = ScreenAreaAuto()

        self.title("BLUM Gaming Bot")
        self.geometry("800x500")
        self.grid_columnconfigure(0, weight=0, minsize=160, uniform="a")

        self.options_frame = ctk.CTkFrame(master=self, border_width=1)
        self.options_frame.grid(row=0, column=0, pady=pady, padx=padx, sticky="nw", columnspan=1)
        self.options_frame.grid_columnconfigure(0, weight=1, minsize=140)

        # self.options_label = ctk.CTkLabel(master=self.options_frame, text="OPTIONS")
        # self.options_label.grid(row=0, column=0, pady=pady, padx=padx, sticky="ew", columnspan=1)

        # Screen area
        self.screen_area_options_label = ctk.CTkLabel(master=self.options_frame, text="Screen area:",
                                                      bg_color="transparent", fg_color="grey", corner_radius=5,
                                                      text_color="yellow")
        self.screen_area_options_label.grid(row=0, column=0, pady=pady, padx=padx, sticky="ew")

        self.area_options = {"Left:": "left", "Top:": "top", "Width:": "width", "Height:": "height"}
        self.screen_area_options_label_title = {}
        self.screen_area_options_label_value = {}
        for i, (text, key) in enumerate(self.area_options.items()):
            self.screen_area_options_label_title[key] = ctk.CTkLabel(master=self.options_frame, text=text, width=60,
                                                                     compound="right", anchor="e")
            self.screen_area_options_label_value[key] = ctk.CTkLabel(master=self.options_frame, text=self.kwargs["monitor"][key],
                                                                     width=60, compound="left", anchor="w")
            self.screen_area_options_label_title[key].grid(row=i + 2, column=0, pady=0, padx=padx, sticky="w")
            self.screen_area_options_label_value[key].grid(row=i + 2, column=0, pady=0, padx=padx, sticky="e")
        row_screen_area = i + 3
        self.screen_area_auto_title = ctk.CTkLabel(master=self.options_frame, text="Auto", width=40, compound="right",
                                                   anchor="e")
        self.screen_area_auto_value = ctk.CTkLabel(master=self.options_frame, text=self.screen_area_auto.status, width=20,
                                                   compound="center", anchor="e", height=24, corner_radius=11)
        self.screen_area_auto_button = ctk.CTkButton(master=self.options_frame, text="Get", width=40, compound="left",
                                                     anchor="w", command=self.kwargs["get_telegram_window"])
        self.screen_area_auto_title.grid(row=row_screen_area, column=0, pady=0, padx=padx, sticky="w")
        self.screen_area_auto_value.grid(row=row_screen_area, column=0, pady=0, padx=padx)
        self.screen_area_auto_button.grid(row=row_screen_area, column=0, pady=0, padx=padx, sticky="e")
        self.update_auto_area_value(self.screen_area_auto.status)
        # self.screen_area_options_value_label.grid(row=2, column=0, pady=pady, padx=padx, sticky="ew")

        row_screen_area += 3
        self.get_screen_area_options_button = ctk.CTkButton(master=self.options_frame, text="Get manually",
                                                            command=self.kwargs["get_screen_area"])
        self.get_screen_area_options_button.grid(row=row_screen_area, column=0, pady=pady, padx=padx, sticky="ew")

        # Autostart area
        autostart_row = 0
        self.autostart_frame = ctk.CTkFrame(master=self, border_width=1)
        self.autostart_frame.grid(row=autostart_row, column=1, pady=pady, padx=padx, sticky="nsew", columnspan=2)
        self.autostart_frame.grid_columnconfigure(0, weight=1)

        autostart_row += 1
        self.autostart_title_label = ctk.CTkLabel(master=self.autostart_frame, text="Automatic control:",
                                                  bg_color="transparent", fg_color="grey", corner_radius=5,
                                                  text_color="yellow")
        self.autostart_title_label.grid(row=autostart_row, column=0, pady=pady, padx=padx, sticky="ew")

        # ---------------------------------
        # Autostart options
        # ---------------------------------
        # game_session_start_time
        autostart_row += 1
        lbl_font = ("Bahnschrift Light Condensed", 13)
        self.game_session_start_time_label = ctk.CTkLabel(master=self.autostart_frame, text="Session start:", font=lbl_font, height=20)
        self.game_session_start_time_label.grid(row=autostart_row, column=0, pady=pady * 0.5, padx=2 * padx, sticky="w")
        # self.screening_threshold_value = ctk.CTkEntry(master=self.screening_frame, width=5)
        self.game_session_start_time_value = ctk.CTkEntry(master=self.autostart_frame, width=50, justify="center")
        # self.game_session_start_time_value.insert(0, threshold.__str__())
        self.game_session_start_time_value.grid(row=autostart_row, column=0, pady=pady * 0.5, padx=padx, sticky="e")
        self.game_session_start_time_value.bind("<Return>", self.kwargs["on_game_session_start_time_change"])
        self.game_session_start_time_value.bind("<FocusIn>", self.kwargs["on_entry_enter"])

        # games_per_session_no
        autostart_row += 1
        self.games_per_session_no_label = ctk.CTkLabel(master=self.autostart_frame, text="Games per session:", font=lbl_font, height=20)
        self.games_per_session_no_label.grid(row=autostart_row, column=0, pady=pady * 0.5, padx=2 * padx, sticky="w")
        # self.screening_threshold_value = ctk.CTkEntry(master=self.screening_frame, width=5)
        self.games_per_session_no_value = ctk.CTkEntry(master=self.autostart_frame, width=50, justify="center")
        # self.games_per_session_no_value.insert(0, threshold.__str__())
        self.games_per_session_no_value.grid(row=autostart_row, column=0, pady=pady * 0.5, padx=padx, sticky="e")
        self.games_per_session_no_value.bind("<Return>", self.kwargs["on_games_per_session_no_change"])
        self.games_per_session_no_value.bind("<FocusIn>", self.kwargs["on_entry_enter"])

        # pause_between_games
        autostart_row += 1
        self.pause_between_games_label = ctk.CTkLabel(master=self.autostart_frame, text="Games pause, s:", font=lbl_font, height=20)
        self.pause_between_games_label.grid(row=autostart_row, column=0, pady=pady * 0.5, padx=2 * padx, sticky="w")
        # self.screening_threshold_value = ctk.CTkEntry(master=self.screening_frame, width=5)
        self.pause_between_games_value = ctk.CTkEntry(master=self.autostart_frame, width=50, justify="center")
        # self.pause_between_games_value.insert(0, threshold.__str__())
        self.pause_between_games_value.grid(row=autostart_row, column=0, pady=pady * 0.5, padx=padx, sticky="e")
        self.pause_between_games_value.bind("<Return>", self.kwargs["on_pause_between_games_change"])
        self.pause_between_games_value.bind("<FocusIn>", self.kwargs["on_entry_enter"])

        # AUTOMATIC START button
        autostart_row += 1
        self.autostart_button = ctk.CTkButton(master=self.autostart_frame, text="START", command=self.kwargs["start_game_session"], height=56)
        self.autostart_button.grid(row=autostart_row, column=0, pady=pady, padx=padx, sticky="ew")

        # Monitoring running
        autostart_row += 1
        self.game_session_monitoring_label_title = ctk.CTkLabel(master=self.autostart_frame, text="Monitoring", width=60,
                                                                compound="right", anchor="e")
        self.game_session_monitoring_label_value = ctk.CTkLabel(master=self.autostart_frame,
                                                                text="getting value ...", width=60, compound="left",
                                                                anchor="w", height=24, corner_radius=11)
        self.game_session_monitoring_label_title.grid(row=autostart_row, pady=0, padx=padx, sticky="w")
        self.game_session_monitoring_label_value.grid(row=autostart_row, pady=0, padx=padx, sticky="e")

        # Games session running
        autostart_row += 1
        self.game_session_label_title = ctk.CTkLabel(master=self.autostart_frame, text="Session", width=60,
                                                                compound="right", anchor="e")
        self.game_session_label_value = ctk.CTkLabel(master=self.autostart_frame,
                                                                text="...", width=60, compound="left",
                                                                anchor="w", height=24, corner_radius=11)
        self.game_session_label_title.grid(row=autostart_row, pady=0, padx=padx, sticky="w")
        self.game_session_label_value.grid(row=autostart_row, pady=0, padx=padx, sticky="e")

        # Game running
        autostart_row += 1
        self.game_label_title = ctk.CTkLabel(master=self.autostart_frame, text="Game", width=60,
                                                                compound="right", anchor="e")
        self.game_label_value = ctk.CTkLabel(master=self.autostart_frame,
                                                                text="...", width=60, compound="left",
                                                                anchor="w", height=24, corner_radius=11)
        self.game_label_title.grid(row=autostart_row, pady=0, padx=padx, sticky="w")
        self.game_label_value.grid(row=autostart_row, pady=0, padx=padx, sticky="e")

        autostart_row += 1
        self.auto_start_running_label_title = ctk.CTkLabel(master=self.autostart_frame, text="Auto Start", width=60,
                                                           compound="right", anchor="e")
        self.auto_start_running_label_value = ctk.CTkLabel(master=self.autostart_frame,
                                                           text="getting value ...", width=60, compound="left",
                                                           anchor="w", height=24, corner_radius=11)
        self.auto_start_running_label_title.grid(row=autostart_row, pady=0, padx=padx, sticky="w")
        self.auto_start_running_label_value.grid(row=autostart_row, pady=0, padx=padx, sticky="e")

        autostart_row += 1
        self.auto_end_running_label_title = ctk.CTkLabel(master=self.autostart_frame, text="Auto End", width=60,
                                                         compound="right", anchor="e")
        self.auto_end_running_label_value = ctk.CTkLabel(master=self.autostart_frame, text="getting value ...",
                                                         width=60, compound="left", anchor="w", height=24,
                                                         corner_radius=11)
        self.auto_end_running_label_title.grid(row=autostart_row, pady=0, padx=padx, sticky="w")
        self.auto_end_running_label_value.grid(row=autostart_row, pady=0, padx=padx, sticky="e")

        autostart_row += 1
        self.autostart_status_label = ctk.CTkLabel(master=self.autostart_frame, text="Status", bg_color="transparent",
                                                   text_color="blue", compound="left", anchor="w")
        self.autostart_status_label.grid(row=autostart_row, column=0, pady=pady, padx=padx, sticky="ew")

        autostart_row += 1
        self.autostart_info_label = ctk.CTkLabel(master=self.autostart_frame, text="Info", bg_color="transparent",
                                                 compound="left", anchor="w")
        self.autostart_info_label.grid(row=autostart_row, column=0, pady=pady, padx=padx, sticky="ew")

        self.update_game_session_monitoring_value(self.kwargs["is_game_session_monitoring_running"].__str__())
        self.update_auto_start_value(self.kwargs["auto_start_running"].__str__())
        self.update_auto_end_value(self.kwargs["auto_end_running"].__str__())

        # Bonuses FRAME
        self.bonus_frame = BonusesUI(master=self)
        self.bonus_frame.grid(row=0, column=3, pady=pady, padx=padx, sticky="nsew")
        self.bonus_frame.grid_columnconfigure(0, weight=1)

        # Manual start area
        self.manual_start_frame = ctk.CTkFrame(master=self, border_width=1)
        self.manual_start_frame.grid(row=0, column=4, pady=pady, padx=padx, sticky="nsew")
        self.manual_start_frame.grid_columnconfigure(0, weight=1)

        self.manual_start_title_label = ctk.CTkLabel(master=self.manual_start_frame, text="Manual control:",
                                                     bg_color="transparent", fg_color="grey", corner_radius=5,
                                                     text_color="yellow", compound="center", anchor="center")
        self.manual_start_title_label.grid(column=0, pady=pady, padx=padx, sticky="ew", columnspan=2)

        # Start screening cycle
        self.screening_frame = ctk.CTkFrame(master=self.manual_start_frame)
        self.screening_frame.grid(row=1, column=0, pady=pady, padx=padx, sticky="nsew")
        self.screening_frame.grid_columnconfigure(0, weight=1)

        screening_row = 0
        self.screening_label = ctk.CTkLabel(master=self.screening_frame, text="Screening")
        self.screening_label.grid(row=screening_row, column=0, pady=pady, padx=padx, sticky="ew")

        screening_row += 1
        self.screening_status_value_label = ctk.CTkLabel(master=self.screening_frame, text="getting value ...")
        self.update_screening_status_value(self.kwargs["screening_running"].__str__())
        self.screening_status_value_label.grid(row=screening_row, column=0, pady=pady, padx=padx, sticky="ew")

        screening_row += 1
        # Screening threshold value
        self.screening_threshold_label = ctk.CTkLabel(master=self.screening_frame, text="Threshold:")
        self.screening_threshold_label.grid(row=screening_row, column=0, pady=pady, padx=2 * padx, sticky="w")
        # self.screening_threshold_value = ctk.CTkEntry(master=self.screening_frame, width=5)
        self.screening_threshold_value = ctk.CTkEntry(master=self.screening_frame, width=50, justify="center")
        self.screening_threshold_value.insert(0, "getting value ...")
        self.screening_threshold_value.grid(row=screening_row, column=0, pady=pady, padx=padx, sticky="e")
        # Bind the function to the <<CTkEntry.value_changed>> event
        # self.screening_threshold_value.bind("<<CTkEntry.value_changed>>", on_threshold_changed)
        self.screening_threshold_value.bind("<Return>", self.kwargs["on_threshold_changed"])
        self.screening_threshold_value.bind("<FocusIn>", self.kwargs["on_entry_enter"])

        screening_row += 1
        # Screening unite tolerance
        self.screening_unite_tolerance_label = ctk.CTkLabel(master=self.screening_frame, text="Unite tolerance:")
        self.screening_unite_tolerance_label.grid(row=screening_row, column=0, pady=pady, padx=2 * padx, sticky="w")
        # self.screening_unite_tolerance_value = ctk.CTkEntry(master=self.screening_frame, width=5)
        self.screening_unite_tolerance_value = ctk.CTkEntry(master=self.screening_frame, width=50, justify="center")
        self.screening_unite_tolerance_value.insert(0, "getting value ...")
        self.screening_unite_tolerance_value.grid(row=screening_row, column=0, pady=pady, padx=padx, sticky="e")
        # Bind the function to the <<CTkEntry.value_changed>> event
        self.screening_unite_tolerance_value.bind("<Return>", self.kwargs["on_unite_tolerance_changed"])
        self.screening_unite_tolerance_value.bind("<FocusIn>", self.kwargs["on_entry_enter"])

        screening_row += 1
        # Start screening cycle button
        self.start_screening_cycle_button = ctk.CTkButton(master=self.screening_frame, text="Start",
                                                          command=self.kwargs["start_screening"])
        self.start_screening_cycle_button.grid(row=screening_row, column=0, pady=pady, padx=padx, sticky="ew")

        screening_row += 1
        self.stop_screening_cycle_button = ctk.CTkButton(master=self.screening_frame, text="Stop",
                                                         command=self.kwargs["stop_screening"])
        self.stop_screening_cycle_button.grid(row=screening_row, column=0, pady=pady, padx=padx, sticky="ew")

        # Clicker
        clicker_row = 0
        self.clicker_frame = ctk.CTkFrame(master=self.manual_start_frame)
        self.clicker_frame.grid(row=1, column=1, pady=pady, padx=padx, sticky="nsw")
        self.clicker_frame.grid_columnconfigure(0, weight=1)

        self.clicker_label = ctk.CTkLabel(master=self.clicker_frame, text="Clicker")
        self.clicker_label.grid(row=clicker_row, column=0, pady=pady, padx=padx, sticky="ew")

        clicker_row += 1
        self.clicker_status_value_label = ctk.CTkLabel(master=self.clicker_frame, text="getting value ...")
        self.update_clicker_status_value(self.kwargs["clicker_running"].__str__())
        self.clicker_status_value_label.grid(row=clicker_row, column=0, pady=pady, padx=padx, sticky="ew")

        clicker_row += 1
        # Clicker threads number
        self.clicker_threads_no_label = ctk.CTkLabel(master=self.clicker_frame, text="Threads no.:")
        self.clicker_threads_no_label.grid(row=clicker_row, column=0, pady=pady, padx=2 * padx, sticky="w")
        # self.clicker_threads_no_value = ctk.CTkEntry(master=self.screening_frame, width=5)
        self.clicker_threads_no_value = ctk.CTkEntry(master=self.clicker_frame, width=40, justify="center")
        self.clicker_threads_no_value.grid(row=clicker_row, column=0, pady=pady, padx=padx, sticky="e")
        self.update_clicker_threads_no_value(str(int(self.kwargs["clicker_threads_no"])))
        # Bind the function to the <<CTkEntry.value_changed>> event
        # self.clicker_threads_no_value.bind("<<CTkEntry.value_changed>>", on_threshold_changed)
        self.clicker_threads_no_value.bind("<Return>", self.kwargs["on_clicker_threads_no_changed"])
        self.clicker_threads_no_value.bind("<FocusIn>", self.kwargs["on_entry_enter"])

        clicker_row += 1
        self.start_clicker_cycle_button = ctk.CTkButton(master=self.clicker_frame, text="Start clicker",
                                                        command=self.kwargs["start_clicker"])
        self.start_clicker_cycle_button.grid(row=clicker_row, column=0, pady=pady, padx=padx, sticky="ew")

        clicker_row += 1
        self.stop_clicker_cycle_button = ctk.CTkButton(master=self.clicker_frame, text="Stop clicker",
                                                       command=self.kwargs["stop_clicker"])
        self.stop_clicker_cycle_button.grid(row=clicker_row, column=0, pady=pady, padx=padx, sticky="ew")

        # Test area
        self.test_frame = ctk.CTkFrame(master=self)
        self.test_frame.grid(row=1, column=0, pady=pady, padx=padx, sticky="nsew", columnspan=1)
        self.test_frame.grid_columnconfigure(0, weight=1)

        self.test_label = ctk.CTkLabel(master=self.test_frame, text="Test")
        self.test_label.grid(row=0, column=0, pady=pady, padx=padx, sticky="ew")

        # self.test_button = ctk.CTkButton(master=self.test_frame, text="Test", command=test_click_confirmed)
        # self.test_button = ctk.CTkButton(master=self.test_frame, text="Test", command=get_objects_locations_by_hsv_mask)
        # self.test_button = ctk.CTkButton(master=self.test_frame, text="Test", command=self.kwargs["get_back_to_home_page"])
        # self.test_button = ctk.CTkButton(master=self.test_frame, text="Test", command=self.kwargs["is_home_page"])
        self.test_button = ctk.CTkButton(master=self.test_frame, text="Test", command=self.kwargs["test_function"])

        self.test_button.grid(row=1, column=0, pady=pady, padx=padx, sticky="ew")

    # def is_main_thread(self):
    #     return get_ident() == self.main_thread_id
    #
    # def safe_update(self, func, *args, **kwargs):
    #     if self.is_main_thread():
    #         func(*args, **kwargs)
    #     else:
    #         self.after(0, lambda: func(*args, **kwargs))
    #
    # def process_update_queue(self):
    #     try:
    #         while True:
    #             func, args, kwargs = self.update_queue.get_nowait()
    #             func(*args, **kwargs)
    #     except queue.Empty:
    #         pass
    #     finally:
    #         self.after(100, self.process_update_queue)
    #
    # def schedule_gui_update(self, func, *args, **kwargs):
    #     self.update_queue.put((func, args, kwargs))

    def update_values(self):
        self.update_auto_area_value(value=self.screen_area_auto.status)
        self.update_screen_area_value(self.kwargs["monitor"])
        self.update_game_session_monitoring_value(value=self.kwargs["is_game_session_monitoring_running"].__str__())
        self.update_game_session_value(value=self.kwargs["is_game_session_running"].__str__())
        self.update_game_value(value=self.kwargs["is_game_running"].__str__())
        self.update_auto_end_value(value=self.kwargs["auto_end_running"].__str__())
        self.update_auto_start_value(value=self.kwargs["auto_start_running"].__str__())
        self.update_screening_status_value(value=self.kwargs["screening_running"].__str__())
        self.update_clicker_status_value(value=self.kwargs["clicker_running"].__str__())
        self.update_clicker_threads_no_value(value=str(int(self.kwargs["clicker_threads_no"])))
        self.update_game_session_start_time_value(value=str(self.kwargs["game_session_start_time"].strftime("%H:%M")))
        self.update_games_per_session_no_value(value=str(int(self.kwargs["games_per_session_no"])))
        self.update_pause_between_games_seconds_value(value=str(int(self.kwargs["pause_between_games_seconds"])))
        self.update_threshold_value(value=str(self.kwargs["threshold"]))
        self.update_unite_tolerance_value(value=str(self.kwargs["unite_tolerance"]))

    def update_screen_area_value(self, value: dict):
        for i, (text, key) in enumerate(self.area_options.items()):
            self.screen_area_options_label_value[key].configure(text=value[key])

        # self.screen_area_options_value_label.configure(text=value)

    def update_screening_status_value(self, value: str):
        text = "Running" if value == "True" else "Stopped"
        color = "#4CAF50" if value == "True" else "#FF5252"
        text_color = "white"
        self.screening_status_value_label.configure(text=text, fg_color=color, text_color=text_color, corner_radius=5)

    def update_clicker_status_value(self, value: str):
        text = "Running" if value == "True" else "Stopped"
        color = "#4CAF50" if value == "True" else "#FF5252"
        text_color = "white"
        self.clicker_status_value_label.configure(text=text, fg_color=color, text_color=text_color, corner_radius=5)

    def update_game_session_monitoring_value(self, value: str):
        text = "Inactive"
        color = "grey"
        text_color = "light grey"

        button_text = "START"
        button_color = "green"
        button_command = self.kwargs["start_game_session"]

        match value:
            case 'True':
                text = "Active"
                color = "green"
                text_color = "light green"
                self.update_autostart_status_label(f"Monitoring for\ngame session ...")
                self.update_autostart_info_label("Press 'STOP' button\nto stop or 'q' to quit ...")
                button_text = "STOP"
                button_color = "red"
                button_command = self.kwargs["stop_game_session"]

                pass
            case 'False':
                text = "Inactive"
                color = "grey"
                text_color = "light grey"
                self.update_autostart_status_label("Game sessions paused")
                self.update_autostart_info_label("Press 'START' button\nto auto-start ...")

                button_text = "START"
                button_color = "green"
                button_command = self.kwargs["start_game_session"]
                pass
            # case _:
            #     text = value
            #     color = "grey"
            #     text_color = "light grey"
            #     self.update_autostart_status_label(f"Game session starts in {value}")
            #     # self.update_autostart_info_label("Press 'START' button\nto auto-start ...")
            #     pass
        self.game_session_monitoring_label_value.configure(text=text, fg_color=color, text_color=text_color, corner_radius=5)
        self.autostart_button.configure(text=button_text, fg_color=button_color, command=button_command)

    def update_game_session_value(self, value: str):
        text = "Inactive"
        color = "grey"
        text_color = "light grey"
        match value:
            case 'True':
                text = "Active"
                color = "green"
                text_color = "light green"
                # self.update_autostart_status_label("Game session active...")
                # self.update_autostart_info_label("Press 'Play' button to start\n or 'q' to quit ...")
                pass
            case 'False':
                text = "Inactive"
                color = "grey"
                text_color = "light grey"
                # self.update_autostart_status_label("Game sessions paused")
                # self.update_autostart_info_label("Press 'START' button\nto auto-start ...")
                pass
            case _:
                text = value
                color = "grey"
                text_color = "light grey"
                self.update_autostart_status_label(f"Game session starts\nin {value}")
                self.update_autostart_info_label("Press 'START' button\nto auto-start ...")
                pass
        self.game_session_label_value.configure(text=text, fg_color=color, text_color=text_color, corner_radius=5)

    def update_game_value(self, value: str):
        text = "Inactive"
        color = "grey"
        text_color = "light grey"
        match value:
            case 'True':
                text = "Active"
                color = "green"
                text_color = "light green"
                # self.update_autostart_status_label("Monitoring for game session ...")
                # self.update_autostart_info_label("Press 'Play' button to start\n or 'q' to quit ...")
                pass
            case 'False':
                text = "Inactive"
                color = "grey"
                text_color = "light grey"
                # self.update_autostart_status_label("Game sessions paused")
                # self.update_autostart_info_label("Press 'START' button\nto auto-start ...")
                pass
            case _:
                text = value
                color = "green"
                text_color = "light green"

        self.game_label_value.configure(text=text, fg_color=color, text_color=text_color, corner_radius=5)

    def update_auto_start_value(self, value: str):
        text = "Inactive"
        color = "grey"
        text_color = "light grey"
        match value:
            case 'True':
                text = "Active"
                color = "green"
                text_color = "light green"
                self.update_autostart_status_label("Waiting for game start ...")
                # self.update_autostart_status_label("Waiting for game start ...")
                self.update_autostart_info_label("Press 'Play' button to start\n or 'q' to quit ...")
                pass
            case 'False':
                text = "Inactive"
                color = "grey"
                text_color = "light grey"
                self.update_autostart_status_label("Paused")
                self.update_autostart_info_label("Press 'START' button\nto auto-start ...")
                # self.update_autostart_info_label("Press 'START' button\nto auto-start ...")
                pass

        self.auto_start_running_label_value.configure(text=text, fg_color=color, text_color=text_color, corner_radius=5)

    def update_auto_end_value(self, value: str):
        text = "Inactive"
        color = "grey"
        text_color = "light grey"

        match value:
            case 'True':
                text = "Active"
                color = "green"
                text_color = "light green"
                self.update_autostart_status_label("Waiting for game end ...")
                self.update_autostart_info_label("Press 'q' to\ncancel auto-end ...")
                pass
            case 'False':
                text = "Inactive"
                color = "grey"
                text_color = "light grey"
                self.update_autostart_status_label("Paused")
                self.update_autostart_info_label("Press 'START' button\nto auto-start ...")
                pass

        self.auto_end_running_label_value.configure(text=text, fg_color=color, text_color=text_color, corner_radius=5)

    def update_auto_area_value(self, value: ScreenAreaAutoStatus):
        text = "/"
        color = "grey"
        text_color = "light grey"
        match value:
            case ScreenAreaAutoStatus.OK:
                text = "OK"
                color = "green"
                text_color = "light green"
                # self.update_autostart_status_label("Waiting for game start ...")
                # self.update_autostart_info_label("Press 'Play' button to start\n or 'q' to quit ...")
                pass
            case ScreenAreaAutoStatus.Failed:
                text = "Failed"
                color = "red"
                text_color = "yellow"
                # self.update_autostart_status_label("Paused")
                # self.update_autostart_info_label("Press 'START' button\nto auto-start ...")
                pass
            case ScreenAreaAutoStatus.Processing:
                text = "..."
                color = "yellow"
                text_color = "light yellow"

        self.screen_area_auto_value.configure(text=text, fg_color=color, text_color=text_color, corner_radius=5)

    def update_threshold_value(self, value: str):
        self.screening_threshold_value.delete(0, "end")
        self.screening_threshold_value.insert(0, value)

    def update_unite_tolerance_value(self, value: str):
        self.screening_unite_tolerance_value.delete(0, "end")
        self.screening_unite_tolerance_value.insert(0, value)

    def update_autostart_status_label(self, value: str):
        self.autostart_status_label.configure(text=value)

    def update_autostart_info_label(self, value: str):
        self.autostart_info_label.configure(text=value)

    def update_clicker_threads_no_value(self, value: str):
        self.clicker_threads_no_value.delete(0, "end")
        self.clicker_threads_no_value.insert(0, value)

    def update_game_session_start_time_value(self, value: str):
        self.game_session_start_time_value.delete(0, "end")
        self.game_session_start_time_value.insert(0, value)

    def update_games_per_session_no_value(self, value: str):
        self.games_per_session_no_value.delete(0, "end")
        self.games_per_session_no_value.insert(0, value)

    def update_pause_between_games_seconds_value(self, value: str):
        self.pause_between_games_value.delete(0, "end")
        self.pause_between_games_value.insert(0, value)
