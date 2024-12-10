# src/seat_monitor/utils/seat_formatter.py
from typing import Set


def format_seats_by_row(seats: Set[str]) -> str:
    """Format seats grouped by row"""
    if not seats:
        return "None"

    # Group seats by row
    rows = {}
    for seat in sorted(seats):
        row = seat[0]  # First character is row letter
        if row not in rows:
            rows[row] = []
        rows[row].append(seat)

    # Format each row
    formatted_rows = []
    for row in sorted(rows.keys()):
        seats_in_row = sorted(
            rows[row], key=lambda x: int(x[1:])
        )  # Sort by seat number
        formatted_rows.append(f"Row {row}: {', '.join(seats_in_row)}")

    return "\n\n".join(formatted_rows)
