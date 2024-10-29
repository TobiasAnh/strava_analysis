# Strava Data Fetcher

This project fetches athlete and activity data from the Strava API and saves it to a CSV file. The data fetching involves authentication, retrieving athlete info, and getting activities within a specified time frame.

## Prerequisites

- A Strava account with an activated API app
- https://developers.strava.com/docs/reference/
- https://developers.strava.com/docs/getting-started/

## Setup

1. **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Environment Variables:**
    Create a `.env` file in the project root with the following content:
    ```plaintext
    CLIENT_ID=your_strava_client_id
    CLIENT_SECRET=your_strava_client_secret
    ```

## Usage

1. **Run the script:**
    ```bash
    python main.py
    ```

2. **Authorize the application:**
    The script will open a browser window for you to authorize the application. Copy the authorization code provided and paste it back into the terminal.

3. **Output:**
    - `activities.json`: Raw activities data in JSON format.
    - `file.csv`: Activities data in CSV format.

## Project Structure

- `main.py`: The main entry point of the application.
- `funcs.py`: Contains helper functions for authentication, data fetching, and data handling.
- `heatmap.py`: Visualize activities on a map.
- `.env`: Environment variables for Strava API credentials.
- `requirements.txt`: Python dependencies.

## Functions Overview

- **Authentication:**
  - `get_tokens()`: Authenticates with Strava and retrieves access and refresh tokens.

- **Data Fetching:**
  - `get_athlete_info(access_token)`: Fetches athlete information using the provided access token.
  - `get_activities(access_token, athlete, start, end)`: Fetches activities data for the athlete within the specified time frame.

- **Data Handling:**
  - `create_json(data, filepath)`: Saves data to a JSON file.
  - `import_json(filepath)`: Imports data from a JSON file.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
