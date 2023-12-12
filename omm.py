from enum import Enum
import time
from typing import Optional, Tuple
import os
from datetime import datetime
import re
import threading


class TeamsState(Enum):
    AVAILABLE = 'Available'
    AWAY = 'Away'
    BUSY = 'Busy'
    BERIGHTBACK = 'Be Right Back'
    OFFLINE = 'Offline'
    DONOTDISTURB = 'Do Not Disturb'
    ONTHEPHONE = 'On The Phone'
    PRESENTING = 'Presenting'
    NEWACTIVITY = 'New Activity'
    UNKNOWN = 'Unknown'
    START = 'Start'

    @classmethod
    def from_string(cls, state_string: str) -> 'TeamsState':
        """
        Get the TeamsState enum option from a string.

        Args:
            state_string (str): The string to convert to a TeamsState option.

        Returns:
            TeamsState: The corresponding enum option.

        Raises:
            ValueError: If the input string is not a valid TeamsState option.
        """
        try:
            return cls[state_string.upper()]
        except KeyError:
            print(f"Not known state: {state_string}")
            return cls.UNKNOWN


class TeamsStateWatchdog():
    def __init__(self,
                 file_path: str = f"{os.getenv('APPDATA')}/Microsoft/Teams/logs.txt",
                 update_hook = None) -> None:
        self._file_path: str = file_path
        self._last_state_change: datetime = datetime.now()
        self.state: TeamsState = TeamsState.START
        self.old_state: TeamsState = TeamsState.START
        self.timestamp: datetime = datetime.now()
        self._internal_loop: bool = False
        self._internal_loop_thread: threading.Thread
        self.update_hook = update_hook

    def _parse_date_string(self, date_string: str) -> datetime:
        """
        Parse a date string into a datetime object.

        Args:
            date_string (str): The date string to parse.

        Returns:
            datetime: The parsed datetime object.
        """
        # Define the format of the input date string
        date_format = "%a %b %d %Y %H:%M:%S GMT%z"

        # Parse the date string into a datetime object
        parsed_datetime = datetime.strptime(date_string, date_format)

        return parsed_datetime

    def _extract_date_from_log(self, log_line: str) -> str:
        """
        Extract the date string from a log line.

        Args:
            log_line (str): The log line containing the date string.

        Returns:
            str: The extracted date string.
        """
        # Define a regular expression pattern to match the date string
        date_pattern = r"\b[a-zA-Z]{3} [a-zA-Z]{3} \d{2} \d{4} \d{2}:\d{2}:\d{2} GMT[+-]\d{4}\b"

        # Search for the pattern in the log line
        match = re.search(date_pattern, log_line)

        # Extract the matched date string
        date_string = match.group() if match else None

        return date_string

    def _parse_log_line(self, line: str) -> Tuple[TeamsState, datetime]:
        """
        Parse a log line to extract relevant information.

        Args:
            line (str): The log line to parse.

        Returns:
            Tuple[str, str, str]: A tuple containing the values extracted. (new_state, old_state, datetime)
        """
        # Split the line based on whitespace
        parts = line.split()

        if "StatusIndicatorStateService:" not in parts:
            return

        if "Added" not in parts:
            return

        if not "current state" in line:
            return

        return (TeamsState.from_string(parts[-6]), 
                self._parse_date_string(self._extract_date_from_log(line)))

        # Return None for lines that do not match the pattern
        return None

    def _process_log_file(self, file_path: str) -> None:
        """
        Process a log file, checking for the specified pattern.

        Args:
            file_path (str): The path to the log file.
        """
        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Iterate over each line in the file
            lines = file.readlines()

            # Iterate over each line in reverse order
            for line_number, log_line in enumerate(reversed(lines), start=1):
                # Parse the log line
                result = self._parse_log_line(log_line)

                # Check if the line matches the pattern
                if result:
                    new_state, timestamp = result
                    print(f"Match found on line {line_number}:")
                    print(f"New State: {new_state}")
                    print(f"Old State: {self.state}")
                    print(f"Timestamp: {timestamp}")
                    print("=" * 40)
                    return

    def state_has_changed(self) -> bool:
        return self._last_state_change != self.timestamp

    def update(self):
        """
        Let's the Watchdog know that the newest state has been acknowledged
        """
        self._last_state_change = self.timestamp
        return

    def refresh(self):
        """
        Gets the newest state from the log files
        """
        print('REFRESH')
        with open(self._file_path, 'r') as file:
            # Iterate over each line in the file
            lines = file.readlines()

            # Iterate over each line in reverse order
        for line_number, log_line in enumerate(reversed(lines), start=1):
            # Parse the log line
            result = self._parse_log_line(log_line)

            # Check if the line matches the pattern
            if result:
                new_state, timestamp = result
                self.old_state = self.state
                self.state = new_state
                self.timestamp = timestamp
                break
        if self.state_has_changed() and self.update_hook is not None:
            self.update_hook()
                
    def loop (self, wait_time):
        while self._internal_loop:
            self.refresh()
            if self.state_has_changed():
                print(self.state)
                self.update()
            time.sleep(wait_time)
                
    def start(self, wait_time: int = 10):
        self._internal_loop = True
        self._internal_loop_thread = threading.Thread(target=self.loop, args=(wait_time,),daemon=True)
        self._internal_loop_thread.start()
        

    def stop(self):
        self._internal_loop = False
        print('STOP')



# Example usage:
if __name__ == "__main__":
    teams_watchdog = TeamsStateWatchdog(
        file_path=f"{os.getenv('APPDATA')}/Microsoft/Teams/logs.txt")
    teams_watchdog.start()
