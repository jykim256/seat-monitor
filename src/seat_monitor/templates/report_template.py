# src/seat_monitor/templates/report_template.py
from datetime import datetime


def generate_html_report(monitor):
    """Generate HTML report with history table"""
    style_content = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 2rem;
            background: #f5f5f7;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1d1d1f;
            margin-bottom: 1.5rem;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e6e6e6;
        }
        th {
            background: white;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 1;
            border-bottom: 2px solid #e6e6e6;
        }
        tr:hover {
            background: #f8f8fa;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            margin: 2px;
        }
        .badge-added {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .badge-removed {
            background: #ffebee;
            color: #c62828;
        }
        .status {
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 500;
        }
        .status-change {
            background: #e3f2fd;
            color: #1565c0;
        }
        .status-initial {
            background: #f3e5f5;
            color: #6a1b9a;
        }
        .status-check {
            background: #f5f5f5;
            color: #666;
        }
        .meta-info {
            color: #666;
            margin-bottom: 2rem;
        }
        .timestamp {
            color: #666;
            font-size: 0.9em;
            white-space: nowrap;
        }
        .latest-check {
            animation: highlight 2s ease-out;
        }
        @keyframes highlight {
            0% { background-color: #fff9c4; }
            100% { background-color: transparent; }
        }
        .total-count {
            background: #f5f5f5;
            padding: 8px 16px;
            border-radius: 8px;
            margin-top: 1rem;
            display: inline-block;
        }
    """
    html_content = f"""
    <html>
    <head>
        <title>Seat Monitor History</title>
        <meta http-equiv="refresh" content="1">
        <style>
            {style_content}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AMC Seat Monitor</h1>
            <div class="meta-info">
                <p>Showtime ID: {monitor.showtime_id}</p>
                <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p class="total-count">Total checks: {len(monitor.change_history)}</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Event</th>
                        <th>Available Seats</th>
                        <th>Changes</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Add rows for each event in reverse chronological order
    for i, event in enumerate(reversed(monitor.change_history)):
        time_str = datetime.fromisoformat(event["timestamp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        row_class = "latest-check" if i == 0 else ""

        if event["event"] == "initial":
            status = '<span class="status status-initial">Initial Check</span>'
            seats = monitor.format_seats_by_row(set(event["available_seats"])).replace(
                "\n", "<br>"
            )
            changes = "Initial state"
        elif event["event"] == "change":
            status = '<span class="status status-change">Change Detected</span>'
            seats = monitor.format_seats_by_row(set(event["available_seats"])).replace(
                "\n", "<br>"
            )

            changes = []
            if event.get("new_seats"):
                formatted = monitor.format_seats_by_row(
                    set(event["new_seats"])
                ).replace("\n", "<br>")
                changes.append(f'<span class="badge badge-added">+ {formatted}</span>')
            if event.get("removed_seats"):
                formatted = monitor.format_seats_by_row(
                    set(event["removed_seats"])
                ).replace("\n", "<br>")
                changes.append(
                    f'<span class="badge badge-removed">- {formatted}</span>'
                )
            changes = " ".join(changes) if changes else "No changes"
        else:  # regular check
            status = '<span class="status status-check">Regular Check</span>'
            seats = monitor.format_seats_by_row(set(event["available_seats"])).replace(
                "\n", "<br>"
            )
            changes = "No changes"

        html_content += f"""
            <tr class="{row_class}">
                <td class="timestamp">{time_str}</td>
                <td>{status}</td>
                <td>{seats}</td>
                <td>{changes}</td>
            </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html_content
