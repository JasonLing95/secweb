from time import time
from flask import Flask, render_template, request, Response
import json
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
API_BASE_URL_CLIENT = os.getenv("API_BASE_URL_CLIENT", 'http://localhost:8000')
API_BASE_URL = os.getenv("API_BASE_URL", 'http://localhost:8000')


@app.context_processor
def utility_processor():
    """
    Utility functions available in Jinja2 templates
    """
    return {
        'max': max,
        'min': min,
        'abs': abs,
        'round': round,
        'len': len,
        'range': range,  # if you need math functions
    }


@app.template_filter('format_number')
def format_number_filter(value):
    """Format numbers with thousands separators"""
    if value is None:
        return "0"
    try:
        return "{:,.0f}".format(float(value))
    except (ValueError, TypeError):
        return str(value)


@app.template_filter('human_date')
def human_readable_date(timestamp_string):
    """
    Converts a timestamp string to a human-readable format.
    Example: 2025-09-07T22:21:18.011000 -> September 07, 2025 at 10:21 PM
    """
    if not timestamp_string:
        return "N/A"

    # Use a try-except block to gracefully handle any malformed date strings
    try:
        # datetime.fromisoformat() is used to parse the timestamp
        dt_object = datetime.fromisoformat(timestamp_string)
        # strftime() is used to format the datetime object into a new string
        return dt_object.strftime('%B %d, %Y at %I:%M %p')
    except ValueError:
        return "Invalid Date"


@app.template_filter('safe_round')
def safe_round(value, precision=2):
    """
    Safely rounds a numeric value to a specified precision.
    Returns 0 if the value is None or not a number.
    """
    if value is None or not isinstance(value, (int, float)):
        return 0
    return round(value, precision)


def make_api_request(endpoint: str, params=None):
    """
    Make a request to the FastAPI backend
    """
    try:
        # Get the API base URL from environment or use default
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes

        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except ValueError as e:
        print(f"Failed to parse JSON response: {e}")
        return None


@app.route('/')
def index():
    """Home page showing latest filings with pagination"""
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Calculate offset
    offset = (page - 1) * per_page

    # Make API request with pagination
    params = {'limit': per_page, 'offset': offset}

    response = make_api_request(
        "/filings",
        params=params,
    )

    if response and isinstance(response, dict):
        filings = response.get("filings", [])
        pagination = response.get("pagination", {})
    else:
        filings = []
        pagination = {}

    return render_template(
        'index.html',
        filings=filings,
        pagination=pagination,
        current_page=page,
        per_page=per_page,
    )


@app.route('/manager/<int:cik>')
def company_detail(cik):
    """Page showing details for a specific manager and their filings"""
    manager = make_api_request(f"/managers/{cik}")
    response = make_api_request(f"/managers/{cik}/filings")

    assert response

    filings = response.get("filings", [])

    return render_template(
        'company.html',
        manager=manager if manager else {},
        filings=filings,
        api_url=API_BASE_URL_CLIENT,
    )


@app.route('/filing/<accession_number>')
def filing_by_accession(accession_number):
    """Page showing details for a specific filing by accession number"""
    # First try to get filing by accession number
    filing = make_api_request(f"/filings/{accession_number}")

    # Then get holdings for the filing ID
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)  # Default to 50 items per page

    # Calculate offset for pagination
    offset = (page - 1) * limit

    # Get holdings with pagination
    holdings_response = make_api_request(
        f"/holdings/{accession_number}?limit={limit}&offset={offset}"
    )

    if holdings_response and 'holdings' in holdings_response:
        holdings = holdings_response['holdings']
        pagination = holdings_response.get('pagination', {})
    else:
        holdings = []
        pagination = {}

    return render_template(
        'filing.html',
        filing=filing,
        holdings=holdings,
        pagination=pagination,
        current_page=page,
    )


@app.route('/compare')
def compare():
    """Page for comparing two filings"""
    accession_prev = request.args.get('prev', '')
    accession_latest = request.args.get('latest', '')

    comparison_data = None
    filing_swapped = None

    if accession_prev and accession_latest:
        comparison_data = make_api_request(
            f"/analysis/{accession_prev}/{accession_latest}"
        )
        if comparison_data and comparison_data['metadata'].get('amendment_used'):
            filing_swapped = comparison_data['metadata']['amendment_used']

    return render_template(
        'compare.html',
        comparison=comparison_data,
        prev_accession=accession_prev,
        latest_accession=accession_latest,
        filing_swapped=filing_swapped,
        api_url=API_BASE_URL_CLIENT,
    )


@app.route("/recent_comparisons")
def show_recent_comparisons():
    comparisons = make_api_request("/comparisons")

    return render_template('recent_comparisons.html', comparisons=comparisons)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
