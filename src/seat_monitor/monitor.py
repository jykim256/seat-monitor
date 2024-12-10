# src/seat_monitor/monitor.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import json
import os
import webbrowser
from typing import Set, Dict, List

from .utils.web_utils import get_available_seats
from .utils.notifications import notify_mac
from .utils.seat_formatter import format_seats_by_row
from .templates.report_template import generate_html_report


class SeatMonitor:
    def __init__(self, showtime_id: str, headless: bool = True):
        """
        Initialize the seat monitor for a specific showtime

        Args:
            showtime_id (str): AMC showtime identifier
            headless (bool): Whether to run browser in headless mode
        """
        self.showtime_id = showtime_id
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.previous_seats: Set[str] = set()
        self.change_history: List[Dict] = []

    def monitor_seats(self, interval: int = 1, log_file: str = None):
        """
        Monitor seats for changes

        Args:
            interval (int): Number of seconds between checks
            log_file (str): Optional file path to save change history
        """
        print(f"Starting seat monitor for showtime {self.showtime_id}")
        print("Press Ctrl+C to stop monitoring\n")

        html_path = os.path.join(
            os.path.expanduser("~"), f"seat_history_{self.showtime_id}.html"
        )

        try:
            while True:
                current_time = datetime.now()
                try:
                    current_seats = get_available_seats(
                        self.showtime_id, self.chrome_options
                    )

                    if not self.previous_seats:
                        # First run
                        print(f"Initial state ({current_time}):")
                        print(
                            f"Available seats:\n{format_seats_by_row(current_seats)}\n"
                        )
                        self.change_history.append(
                            {
                                "timestamp": current_time.isoformat(),
                                "event": "initial",
                                "available_seats": sorted(list(current_seats)),
                            }
                        )
                        # Test notification after first check
                        notify_mac(
                            "Seat Monitor Started",
                            f"Monitoring showtime {self.showtime_id} - Initial seats: {len(current_seats)}",
                        )
                        # Open HTML report in browser
                        webbrowser.open(f"file://{html_path}")
                    else:
                        # Check for changes
                        new_seats = current_seats - self.previous_seats
                        removed_seats = self.previous_seats - current_seats

                        # Clear the previous status line
                        print("\033[F\033[K")
                        print("\033[F\033[K")

                        if new_seats or removed_seats:
                            # Print change notification (permanent)
                            print(f"\nChange detected at {current_time}:")
                            if new_seats:
                                print(
                                    f"New seats available:\n{format_seats_by_row(new_seats)}"
                                )
                            if removed_seats:
                                print(
                                    f"Seats no longer available:\n{format_seats_by_row(removed_seats)}"
                                )
                            print(
                                f"Total available seats:\n{format_seats_by_row(current_seats)}\n"
                            )

                            # Update notification message
                            notification_msg = f"New seats:\n{format_seats_by_row(new_seats) if new_seats else 'None'}\nRemoved:\n{format_seats_by_row(removed_seats) if removed_seats else 'None'}"
                            notify_mac("Seats Changed!", notification_msg)

                            # Record change
                            self.change_history.append(
                                {
                                    "timestamp": current_time.isoformat(),
                                    "event": "change",
                                    "new_seats": sorted(list(new_seats)),
                                    "removed_seats": sorted(list(removed_seats)),
                                    "available_seats": sorted(list(current_seats)),
                                }
                            )
                        else:
                            # Record regular check
                            self.change_history.append(
                                {
                                    "timestamp": current_time.isoformat(),
                                    "event": "check",
                                    "available_seats": sorted(list(current_seats)),
                                }
                            )

                        # Print current status (will be overwritten next iteration)
                        print(f"Current state ({current_time}):")
                        print(f"Available seats:\n{format_seats_by_row(current_seats)}")

                        # Save to log file if specified
                        if log_file:
                            with open(log_file, "w") as f:
                                json.dump(self.change_history, f, indent=2)

                    # Always generate and save HTML report
                    html_content = generate_html_report(self)
                    with open(html_path, "w") as f:
                        f.write(html_content)

                    self.previous_seats = current_seats

                except Exception as e:
                    print(f"\nError occurred: {e}")
                    self.change_history.append(
                        {
                            "timestamp": current_time.isoformat(),
                            "event": "error",
                            "error": str(e),
                        }
                    )

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            if log_file:
                print(f"Change history saved to {log_file}")
