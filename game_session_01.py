import threading
from datetime import datetime, date, timedelta, time as dtime
import time


class GameMonitoring:
    import threading
    from datetime import time as dtime

    def __init__(self, game_start_callback: callable, session_callback: callable, monitoring_callback: callable,
                 session_start_time: time = dtime(8, 0, 0),
                 session_games_no: int = 2,
                 pause_between_games_seconds: int = 10):
        self.session_games_no = session_games_no
        self.pause_between_games_seconds = pause_between_games_seconds
        self.session_start_time = session_start_time
        self.game_start_callback = game_start_callback
        self.session_callback = session_callback
        self.monitoring_callback = monitoring_callback
        self.monitoring_thread = None
        self.is_monitoring_running = False
        self.is_session_running = False
        self.is_game_running = False
        self.session_completed = False

    def start(self):
        self.monitoring_thread = threading.Thread(target=self.monitoring_thread)
        self.monitoring_thread.start()
        pass

    def stop(self):
        pass

    def monitoring_thread(self):
        self.is_monitoring_running = True
        self.monitoring_callback(self.is_monitoring_running)

        print(f"Game session monitoring thread started")
        midnight = dtime(0, 0, 0)
        midnight_plus = dtime(0, 0, 30)
        while self.is_monitoring_running:
            current_time = datetime.now().time()

            if self.session_completed:
                start_datetime = datetime.combine(date.today() + timedelta(days=1), self.session_start_time)
            else:
                start_datetime = datetime.combine(date.today(), self.session_start_time)

            # Reset session_completed flag if midnight has passed
            if (midnight <= current_time < midnight_plus) and self.session_completed:
                self.session_completed = False

            current_datetime = datetime.combine(date.today(), current_time)

            # difference_seconds = (game_session_start_time - current_time).total_seconds()
            difference_seconds = (start_datetime - current_datetime).total_seconds()
            print(f"Game session start in {difference_seconds} seconds", end="\r", flush=True)

            if current_datetime >= start_datetime and not session_completed:
                print(f"Game session starting (total games: {self.session_games_no})")
                # Start session
                self.is_session_running = True
                self.session_callback(self.is_session_running)
                for game_no in range(self.session_games_no):
                    print(f"Starting game no {game_no + 1}")
                    self.game_start_callback()
                    print(f"Game {game_no + 1} started")
                    self.wait_for_game_end()
                    print(f"Game {game_no + 1} finished.\nPause {self.pause_between_games_seconds} seconds")
                    time.sleep(self.pause_between_games_seconds)
                print(f"********* SESSION COMPLETED *********")
                self.session_completed = True
                self.is_session_running = False
                self.session_callback(self.is_session_running)
            else:
                # print(f"Game session pause for {difference_seconds} seconds")
                # time.sleep(abs(difference_seconds))
                time.sleep(1)
            print(f"------------------ AUTO GAME SESSION MONITORING ----------")
        # End monitoring
        self.is_monitoring_running = False
        self.monitoring_callback(self.is_monitoring_running)
        print(f"------------------ AUTO GAME MONITORING COMPLETE ----------")
        pass

    def wait_for_game_end(self):
        # from main import game_auto_running
        print(f"AUTO GAME SESSION: waiting for game END ...")
        while self.is_game_running:
            print(f"AUTO GAME SESSION: self.is_game_running: {self.is_game_running}", end="\r", flush=True)
            time.sleep(1)
            pass


game_session_thread = None
monitoring_thread_running = False
game_running = False
session_completed = False


def start_game_session_monitoring():
    global game_session_thread
    game_session_thread = threading.Thread(target=game_session_monitoring_thread)
    game_session_thread.start()


def stop_game_session_monitoring():
    from main import app
    global game_session_thread, monitoring_thread_running
    monitoring_thread_running = False
    if app is not None:
        app.update_game_session_monitoring_value(value=monitoring_thread_running.__str__())
    game_session_thread.join()


def game_session_monitoring_thread():
    global game_session_thread, monitoring_thread_running, session_completed
    from main import app, game_session_start_time, games_per_session_no,\
        pause_between_games_seconds, auto_start
    monitoring_thread_running = True
    if app is not None:
        app.update_game_session_monitoring_value(value=monitoring_thread_running.__str__())
    print(f"Game session monitoring thread started")
    midnight = dtime(0, 0, 0)
    midnight_plus = dtime(0, 0, 30)
    while monitoring_thread_running:
        current_time = datetime.now().time()

        if session_completed:
            start_datetime = datetime.combine(date.today() + timedelta(days=1), game_session_start_time)
        else:
            start_datetime = datetime.combine(date.today(), game_session_start_time)

        if (midnight <= current_time < midnight_plus) and session_completed:
            session_completed = False

        current_datetime = datetime.combine(date.today(), current_time)

        # difference_seconds = (game_session_start_time - current_time).total_seconds()
        difference_seconds = (start_datetime - current_datetime).total_seconds()
        print(f"Game session start in {difference_seconds} seconds")

        if current_datetime >= start_datetime and not session_completed:
            print(f"Game session starting (total games: {games_per_session_no})")
            # Start session
            for game_no in range(games_per_session_no):
                print(f"Starting game no {game_no + 1}")
                auto_start()
                print(f"Game {game_no + 1} started")
                wait_for_game_end()
                print(f"Game {game_no + 1} finished.\nPause {pause_between_games_seconds} seconds")
                time.sleep(pause_between_games_seconds)
            print(f"********* SESSION COMPLETED *********")
            session_completed = True
        else:
            # print(f"Game session pause for {difference_seconds} seconds")
            # time.sleep(abs(difference_seconds))
            time.sleep(1)
        print(f"------------------ AUTO GAME SESSION MONITORING ----------")
    # End session
    print(f"------------------ AUTO GAME SESSION COMPLETE ----------")
    monitoring_thread_running = False
    pass


def wait_for_game_end():
    # from main import game_auto_running
    print(f"AUTO GAME SESSION: waiting for game END ...")
    while game_running:
        print(f"AUTO GAME SESSION: game_auto_running: {game_running}")
        time.sleep(1)
        pass
