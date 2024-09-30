import customtkinter as ctk
from settings_manager import SettingsManager
from customtkinter import StringVar


class CTkEntryEx(ctk.CTkEntry):
    def __init__(self, master, row: int, title: str, setting_name: str,
                 value_changed_callback: callable,
                 default_value: str = "",
                 **kw):
        lbl_font = ("Bahnschrift Light Condensed", 13)
        pady = 5
        padx = 5
        self.title_label = ctk.CTkLabel(master=master, text=title, font=lbl_font, height=20)
        self.title_label.grid(row=row, column=0, pady=pady * 0.5, padx=2 * padx, sticky="w")

        super().__init__(master=master, width=50, justify="center", **kw)
        self.grid(row=row, column=1, pady=pady * 0.5, padx=padx, sticky="e")
        self.settings = SettingsManager("settings.json")
        self.setting_name = setting_name
        self.value_changed_callback = value_changed_callback
        self.bind("<Return>", self.on_return)
        self.bind("<FocusIn>", self.on_focus)

        value = self.settings.get_setting(self.setting_name, default_value)
        self.update_value(value)

    def on_return(self, event):
        value = self.get()
        # Change variable
        self.value_changed_callback(value)
        # Save to settings
        self.settings.set_setting(self.setting_name, value)
        self.settings.save_settings()

    def on_focus(self, event):
        self.select_range(0, "end")
        # self.insert(0, self.settings.get(self.setting_name))

    def update_value(self, value: str, save_to_settings: bool = False):
        self.delete(0, "end")
        self.insert(0, value)
        # Change variable
        self.value_changed_callback(value)
        if save_to_settings:
            # Save to settings
            self.settings.set_setting(self.setting_name, value)
            self.settings.save_settings()


class CTkSwitchEx(ctk.CTkSwitch):
    def __init__(self, master, row: int, title: str, setting_name: str,
                 value_changed_callback: callable,
                 default_value: bool = False,
                 **kw):
        lbl_font = ("Bahnschrift Light Condensed", 13)
        pady = 5
        padx = 5

        self.title_label = ctk.CTkLabel(master=master, text=title, font=lbl_font, height=20)
        self.title_label.grid(row=row, column=0, pady=pady * 0.5, padx=2 * padx, sticky="w")

        self.settings = SettingsManager("settings.json")
        self.setting_name = setting_name
        self.value_changed_callback = value_changed_callback
        var_value = self.settings.get_setting(self.setting_name, "OFF")
        self.switch_variable = StringVar(value=var_value)
        self.switch_text = self.get_switch_text()

        super().__init__(master=master, variable=self.switch_variable, text=self.switch_text,
                         command=self.switch_event, height=56,
                         onvalue="ON", offvalue="OFF", **kw)
        self.grid(row=row, column=1, pady=pady * 0.5, padx=padx, sticky="e")
        # self.switch_event()
        # self.toggle()

    def get_switch_text(self):
        state = self.switch_variable.get()
        if state == 0 or state == "OFF":
            self.switch_text = "OFF"
        else:
            self.switch_text = "ON"
        return self.switch_text

    def switch_event(self):
        # state = self.get()
        state = self.switch_variable.get()
        print(f"Switch event triggered to {state}")
        if state == "OFF":
            self.configure(text="OFF")
            self.configure(fg_color="red")
        elif state == "ON":
            self.configure(text="ON")
            self.configure(fg_color="green")
        self.settings.set_setting(self.setting_name, state.__str__())
        self.settings.save_settings()
        self.value_changed_callback(state)


class CTkStateLabel(ctk.CTkLabel):
    def __init__(self, master, row: int, title: str, **kw):
        lbl_font = ("Bahnschrift Light Condensed", 13)
        pady = 5
        padx = 5
        self.title_label = ctk.CTkLabel(master=master, text=title, font=lbl_font, height=20, width=50)
        self.title_label.grid(row=row, column=0, pady=pady * 0.5, padx=2 * padx, sticky="w")
        super().__init__(master=master, text="...", font=lbl_font, height=24, corner_radius=11, **kw)
        self.grid(row=row, column=1, pady=pady * 0.5, padx=padx, sticky="e")

    def update_state(self, value: str):
        text = "Inactive"
        color = "grey"
        text_color = "light grey"

        match value:
            case "ON":
                text = "Active"
                color = "green"
                text_color = "light green"
                # self.update_autostart_status_label(f"Monitoring for\ngame session ...")
                # self.update_autostart_info_label("Press 'STOP' button\nto stop or 'q' to quit ...")

            case "OFF":
                text = "Inactive"
                color = "grey"
                text_color = "light grey"
                # self.update_autostart_status_label("Game sessions paused")
                # self.update_autostart_info_label("Press 'START' button\nto auto-start ...")

        self.configure(text=text, fg_color=color, text_color=text_color, corner_radius=5)
        # self.autostart_button.configure(text=button_text, fg_color=button_color, command=button_command)
