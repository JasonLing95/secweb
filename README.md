# SEC Filings Web Frontend 📈

This is a Flask-based web application that serves as a user-friendly frontend for an SEC filings analysis API. It allows users to browse, search, and compare 13F-HR filings.

---

## ✨ Features

- **Recent Filings**: View a paginated list of the latest 13F-HR filings with sorting options.
- **Manager Details**: See the complete filing history for a specific investment manager.
- **Filing Analysis**: View the detailed holdings for any given filing in a searchable table.
- **Filing Comparison**: Compare any two filings side-by-side to see portfolio changes, including:
  - New and closed positions.
  - Increased and decreased holdings.
- **Latest Stories**: A dynamic feed showing recent filings with the most significant portfolio changes.

---

## 🚀 Getting Started

Follow these steps to get the frontend application running locally.

### Prerequisites

- Python 3.8+
- An instance of the [backend API](https://github.com/JasonLing95/secapi) must be running.

### Installation and Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/JasonLing95/secweb.git
    cd secweb
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the API Endpoint:**
    The application needs to know the URL of your running backend API. Set this using an environment variable. If not set, it defaults to `http://localhost:8000`.

    ```bash
    export API_BASE_URL="http://your-api-host:8000"
    ```

4.  **Run the Application:**

    ```bash
    python app.py
    ```

    The web server will start. You can now access the application in your browser at `http://localhost:5000`.
