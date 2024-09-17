import json


class SettingsManager:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as file:
                self.settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as file:
                json.dump(self.settings, file, indent=4)
        except IOError as e:
            print(f"Error writing settings file: {e}")

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value

# # Example usage
# settings_manager = SettingsManager('settings.json')
#
# # Save settings
# settings_manager.set_setting('window_size', (800, 600))
# settings_manager.set_setting('options', {'fulscreen': False, 'show_cursor': True})
# settings_manager.save_settings()
#
# # Retrieve settings
# window_size = settings_manager.get_setting('window_size', (640, 480))
# options = settings_manager.get_setting('options', {})
#
# print(f"Window size: {window_size}")
# print(f"Options: {options}")

