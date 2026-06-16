# weather-data-validator
# Weather Monitoring and Data Validation System

A Python-based application that fetches real-time weather data from the WeatherAPI, processes it, and performs local validation rules before storing the records into a MySQL database.

## Repository Structure
The project contains the following core files:
* `weather_app.py` - The main Python application script.
* `weather_db.sql` - The official MySQL database export containing schemas and data.
* `validation_log.txt` - Text logs tracking data evaluation metrics.
* `weather_history.txt` - Text logs of successful weather records.

---

## Database Configuration

### 1. Database Name
* **Name:** `weather_db`

### 2. Table Structure
The system utilizes a single table named `weather_reports` with an appended validation tracking column:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | INT (Primary Key) | Auto-incremented unique record identifier. |
| `city` | VARCHAR(100) | Name of the queried city. |
| `country` | VARCHAR(100) | Country of the queried city. |
| `temperature` | DECIMAL(5,2) | Temperature in Celsius. |
| `humidity` | INT | Humidity percentage. |
| `wind_speed` | DECIMAL(5,2) | Wind speed in km/h. |
| `condition` | VARCHAR(100) | Text description of weather conditions (e.g., Sunny, Mist). |
| `search_date` | DATE | Date the query was executed. |
| `search_time` | TIME | Time the query was executed. |
| `feels_like` | DECIMAL(5,2) | Perceived temperature in Celsius. |
| `pressure` | DECIMAL(7,2) | Atmospheric pressure in millibars (mb). |
| `visibility` | DECIMAL(5,2) | Visibility distance in kilometers. |
| `uv_index` | DECIMAL(4,2) | UV Index exposure level. |
| `raw_response` | TEXT | The full, unmodified JSON payload received from the API. |
| `validation_status` | VARCHAR(10) | Tracks data integrity status (`PASSED` or `FAILED`). |

---

## Data Validation Workflow

The application implements strict regex and pattern verification on incoming query parameters before sending data requests to the API, ensuring garbage data is rejected early.

* **PASSED Status:** Valid geographic inputs (e.g., Mumbai, Paris, Tokyo) fetch real-time weather parameters successfully and append a `PASSED` state.
* **FAILED Status:** Numeric or corrupted input queries (e.g., `12345`, `mumbai123`) trigger local preprocessing exceptions, blocking the API request and logging a `FAILED` status with a descriptive tracking message.

---
Import the database schema into your local MySQL instance:

Bash
mysql -u root -p weather_db < weather_db.sql
Run the application:

Bash
python weather_app.py
