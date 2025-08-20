# Strava Data Fetcher

This project fetches athlete and activity data from the **Strava API** and stores it in a **PostgreSQL database** for analysis and tracking.  

The script handles authentication, token refresh, athlete profile fetching and incremental updates of activity data. The application is containerized for easy deployment.

---

## Features
- Authenticate with the Strava API and refresh access tokens automatically.  
- Fetch athlete profile details and store them in a PostgreSQL database.  
- Incrementally fetch new activities since the last update.  
- Save activities in SQL database.  
- Two modes of operation:
  - `init`: Perform the initial setup and get new tokens.  
  - `update`: Refresh tokens if expired, fetch new data, and update the database.  

---

## Requirements

- Docker and Docker Compose
- Python **3.8+** (managed via Poetry)
- A registered **Strava API application** (to obtain `client_id` and `client_secret`)
- PostgreSQL database

---
