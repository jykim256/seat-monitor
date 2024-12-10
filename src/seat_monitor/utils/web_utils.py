# src/seat_monitor/utils/web_utils.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Set
from consts import ROW_CHARS, MAX_SEATS_PER_ROW


def get_available_seats(showtime_id: str, chrome_options) -> Set[str]:
    """Get current available seats"""
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # Load page
        url = f"https://www.amctheatres.com/showtimes/{showtime_id}/seats"
        driver.get(url)

        # Wait for seats to load
        wait = WebDriverWait(driver, 3)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="mx-1"]')))
        seats = driver.find_elements(By.CSS_SELECTOR, '[class*="mx-1"]')

        # Initialize variables
        row_seats = {}
        current_row = 0
        seat_num = MAX_SEATS_PER_ROW

        # Collect seats into rows
        for i, seat in enumerate(seats):
            if seat_num == 0:
                current_row += 1
                seat_num = MAX_SEATS_PER_ROW
            row_letter = ROW_CHARS[current_row]
            if row_letter not in row_seats:
                row_seats[row_letter] = []

            classes = seat.get_attribute("class")
            is_available = "cursor-not-allowed" not in classes
            is_invisible = "invisible" in classes

            row_seats[row_letter].append(
                {
                    "position": seat_num,
                    "is_invisible": is_invisible,
                    "is_available": is_available,
                }
            )
            seat_num -= 1

        # Process rows and normalize seat numbers
        normalized_seat_map = {}
        for row_letter, seats in row_seats.items():
            seats = seats[::-1]  # Reverse list since counted backwards

            # Count invisible seats on left
            left_invisible = 0
            for seat in seats:
                if seat["is_invisible"]:
                    left_invisible += 1
                else:
                    break

            # Count invisible seats on right
            right_invisible = 0
            for seat in reversed(seats):
                if seat["is_invisible"]:
                    right_invisible += 1
                else:
                    break

            # Create normalized mapping
            new_seat_num = 1
            for i, seat in enumerate(seats):
                if i < left_invisible or i >= (len(seats) - right_invisible):
                    continue
                normalized_seat_map[f"{row_letter}{new_seat_num:02d}"] = seat[
                    "is_available"
                ]
                new_seat_num += 1

        # Get available seats
        available_seats = {
            seat_id
            for seat_id, is_available in normalized_seat_map.items()
            if is_available
        }

        return available_seats

    finally:
        driver.quit()
