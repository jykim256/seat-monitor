# src/seat_monitor/main.py
import sys
from monitor import SeatMonitor


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <showtime_id> [log_file]")
        sys.exit(1)

    showtime_id = sys.argv[1]
    log_file = sys.argv[2] if len(sys.argv) > 2 else None

    monitor = SeatMonitor(showtime_id)
    monitor.monitor_seats(log_file=log_file, interval=15)


if __name__ == "__main__":
    main()
