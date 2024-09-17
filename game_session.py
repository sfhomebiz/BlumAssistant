from threading import Thread, Event
from settings_manager import SettingsManager
from datetime import datetime, date, timedelta, time as dtime
import time


def seconds_to_time_string(seconds: int) -> str:
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class GameMonitoring:
    # import threading
    # from datetime import time as dtime
    # import time

    def __init__(self, game_start_callback: callable,
                 game_status_callback: callable,
                 session_status_callback: callable,
                 monitoring_status_callback: callable,
                 session_start_time: time = dtime(8, 0, 0),
                 session_games_no: int = 2,
                 pause_between_games_seconds: int = 10):
        self.session_games_no = session_games_no
        self.pause_between_games_seconds = pause_between_games_seconds
        self.session_start_time = session_start_time
        self.game_start_callback = game_start_callback
        self.game_status_callback = game_status_callback
        self.session_status_callback = session_status_callback
        self.monitoring_status_callback = monitoring_status_callback
        self.monitoring_thread = None
        self.thread_started = Event()
        self.is_monitoring_running = False
        self.is_session_running = False
        self.is_game_running = False
        self.is_home_page = True
        self.session_completed = False
        self.settings = SettingsManager("settings.json")
        # self.last_run = self.settings.get_setting('game_session_last_run')
        self.last_run = self.load_last_run()

    def start(self):
        print(f"Game session monitoring thread starting ...")
        self.monitoring_thread = Thread(target=self.session_monitoring_thread)
        # print("Thread created, about to start...")
        self.monitoring_thread.start()
        # print("Thread.start() called, waiting for thread to start...")
        # self.thread_started.wait(timeout=5)  # Wait for the thread to start
        started = self.thread_started.wait(timeout=5)
        print(f"Thread started: {started}")
        print(f"Monitoring thread start completed")
        # time.sleep(0.1)  # Give the thread a moment to start
        # pass

    def stop(self):
        self.is_game_running = False
        self.game_status_callback(self.is_game_running)
        self.is_session_running = False
        self.session_status_callback(self.is_session_running)
        self.is_monitoring_running = False
        self.monitoring_status_callback(self.is_monitoring_running)
        # pass

    def session_monitoring_thread(self):
        # try:
        print(f"Game session monitoring thread started")
        self.thread_started.set()  # Signal that the thread has started
        print("Thread start signal set")
        self.is_monitoring_running = True
        self.monitoring_status_callback(self.is_monitoring_running)
        print(f"------------------ AUTO GAME SESSION MONITORING ----------", end="\n", flush=False)

        midnight = dtime(0, 0, 0)
        midnight_plus = dtime(0, 0, 30)
        self.last_run = self.load_last_run()
        while self.is_monitoring_running:
            current_time = datetime.now().time()

            if self.last_run is None or self.last_run.date() < datetime.now().date():
                start_datetime = datetime.combine(date.today(), self.session_start_time)
            else:
                start_datetime = datetime.combine(date.today() + timedelta(days=1), self.session_start_time)
            # if self.session_completed:
            #     start_datetime = datetime.combine(date.today() + timedelta(days=1), self.session_start_time)
            # else:
            #     start_datetime = datetime.combine(date.today(), self.session_start_time)
            #
            # # Reset session_completed flag if midnight has passed
            # if (midnight <= current_time < midnight_plus) and self.session_completed:
            #     self.session_completed = False
            #
            current_datetime = datetime.combine(date.today(), current_time)

            # difference_seconds = (game_session_start_time - current_time).total_seconds()
            difference_seconds = (start_datetime - current_datetime).total_seconds()
            # difference_seconds = (self.session_start_time - current_time).total_seconds()
            if type(difference_seconds) == str:
                difference_seconds = 0
            diff_str = seconds_to_time_string(int(difference_seconds))
            print(f"Game session starts in {diff_str}", end="\r", flush=True)
            self.session_status_callback(f"{diff_str}")

            # if current_datetime >= start_datetime and not self.session_completed:
            #     self.run_game_task()
            # else:
            #     # print(f"Game session pause for {difference_seconds} seconds")
            #     # time.sleep(abs(difference_seconds))
            #     pass
            if (current_time >= self.session_start_time and
               (self.last_run is None or self.last_run.date() < datetime.now().date())):
                self.run_game_task()
            time.sleep(1)
            # print(f"------------------ AUTO GAME SESSION MONITORING ----------", end="\r", flush=False)
            # print(f"------------------ AUTO GAME SESSION MONITORING ----------", end="\n", flush=True)
            # print(f"-", end="\n", flush=False)
        # End monitoring
        self.is_monitoring_running = False
        self.monitoring_status_callback(self.is_monitoring_running)
        print(f"------------------ AUTO GAME MONITORING COMPLETE ----------")
        # except Exception as e:
        #     print(f"Error in monitoring thread: {e}")

    def run_game_task(self):
        print(f"Game session starting (total games: {self.session_games_no})")
        # Start session
        self.is_session_running = True
        self.session_status_callback(self.is_session_running)
        for game_no in range(self.session_games_no):
            print(f"Starting game no {game_no + 1}")
            print(f"And checking for home page ...")
            while not self.is_home_page:
                time.sleep(1)
            print(f"game_session -- check for home page successful. Starting ...")
            self.game_start_callback()
            print(f"game_session -- game_start_callback() sent. Waiting for start ...")
            while not self.wait_for_game_start():
                self.game_start_callback()
                time.sleep(2)
            self.game_status_callback(f"{game_no + 1}/{self.session_games_no}")
            print(f"Game {game_no + 1} started")
            # if self.wait_for_game_start():
            #     self.game_status_callback(f"{game_no + 1}/{self.session_games_no}")
            #     print(f"Game {game_no + 1} started")
            # else:
            #     print(f"Starting game attempt failed. Restarting ...")

            print(f"game_session -- Waiting for game end ...")
            self.wait_for_game_end()
            print(f"Game {game_no + 1} finished.\nPause {self.pause_between_games_seconds} seconds")
            time.sleep(self.pause_between_games_seconds)
        self.session_completed = True
        self.is_session_running = False
        self.session_status_callback(self.is_session_running)
        self.save_last_run()
        self.last_run = self.load_last_run()
        print(f"********* SESSION COMPLETED *********")
        # print(f"Session control is updated ...")

    def wait_for_game_start(self, timeout=10) -> bool:
        start_timeout = time.perf_counter()
        while not self.is_game_running:
            time.sleep(1)
            end_timeout = time.perf_counter()
            if end_timeout - start_timeout >= timeout:
                break
        return self.is_game_running

    def wait_for_game_end(self):
        # from main import game_auto_running
        print(f"AUTO GAME SESSION: waiting for game END ...")
        while self.is_game_running:
            print(f"AUTO GAME SESSION: self.is_game_running: {self.is_game_running}", end="\r", flush=True)
            time.sleep(1)
            pass

    def load_last_run(self):
        # print(f"Loading last run ...")
        result = self.settings.get_setting('game_session_last_run')
        if result is None:
            # print(f"last run is None.")
            return None
        # print(f"last run is {datetime.fromisoformat(result)}")
        try:
            res = datetime.fromisoformat(result)
        except():
            res = datetime.strptime(result, "%H:%M").time()
        return res
        pass

    def save_last_run(self):
        print(f"Saving last run ... {datetime.now().isoformat()}")
        self.settings.set_setting('game_session_last_run', datetime.now().isoformat())
        self.settings.save_settings()
        print(f"save_last_run() completed.")
        pass
