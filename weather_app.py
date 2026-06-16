import requests
import mysql.connector
import re
from datetime import datetime

API_KEY = "b0143f4f8ded4438a84101616261206"

# Global runtime counter for failed validations (Feature 3)
failed_validations_counter = 0

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          
        password="Jabeen@57",  
        database="weather_db"
    )
print("Connected successfully...")


# ==========================================
#         REGEX VALIDATION FUNCTIONS
# ==========================================

def validate_city(city_name):
    # Bonus Challenge 1: Allows alphabets, spaces, dots (St. Louis), and hyphens
    pattern = r"^[A-Za-z\s\.\-]+$"
    return bool(re.fullmatch(pattern, str(city_name)))

def validate_country(country_name):
    # Rules: Alphabets and spaces allowed
    pattern = r"^[A-Za-z\s]+$"
    return bool(re.fullmatch(pattern, str(country_name)))

def validate_temperature(temp):
    # Rules: Numeric values only, allows signs like negative integers or floats
    pattern = r"^-?\d+(\.\d+)?$"
    return bool(re.fullmatch(pattern, str(temp)))

def validate_humidity(humidity):
    # Rules: Numeric values only (integers or floats)
    pattern = r"^\d+(\.\d+)?$"
    return bool(re.fullmatch(pattern, str(humidity)))

def validate_wind_speed(wind_speed):
    # Rules: Numeric values only (integers or floats)
    pattern = r"^\d+(\.\d+)?$"
    return bool(re.fullmatch(pattern, str(wind_speed)))

def validate_condition(condition):
    # Rules: Alphabets and spaces allowed
    pattern = r"^[A-Za-z\s]+$"
    return bool(re.fullmatch(pattern, str(condition)))


# ==========================================
#         MASTER VALIDATION MANAGER
# ==========================================

def validate_weather_data(city_name, country, temp, humidity, wind_speed, condition):
    global failed_validations_counter
    
    # Process checks individually
    v_city = validate_city(city_name)
    v_country = validate_country(country)
    v_temp = validate_temperature(temp)
    v_hum = validate_humidity(humidity)
    v_wind = validate_wind_speed(wind_speed)
    v_cond = validate_condition(condition)
    
    # Feature 1: Print Validation Status Report 
    print("\n>>> VALIDATION REPORT <<<")
    print(f"City Validation        : {'Passed' if v_city else 'Failed'}")
    print(f"Country Validation     : {'Passed' if v_country else 'Failed'}")
    print(f"Temperature Validation : {'Passed' if v_temp else 'Failed'}")
    print(f"Humidity Validation    : {'Passed' if v_hum else 'Failed'}")
    print(f"Wind Speed Validation  : {'Passed' if v_wind else 'Failed'}")
    print(f"Condition Validation   : {'Passed' if v_cond else 'Failed'}")
    print("--------------------------------")

    all_passed = all([v_city, v_country, v_temp, v_hum, v_wind, v_cond])
    
    # Track metrics if components drop issues
    if not all_passed:
        failed_validations_counter += 1
        
    return all_passed


# ==========================================
#       LOGGING & SYSTEM FILE WRITERS
# ==========================================

def write_validation_log(city_name, status):
    # Feature 2: Append entries into validation_log.txt
    current_time_str = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    with open("validation_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{current_time_str}\n{city_name}\n{status}\n\n")

def export_invalid_record(city_name, country, temp, humidity, wind_speed, condition):
    # Bonus Challenge 3: Dump failed objects into invalid_weather_records.txt
    current_time_str = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    with open("invalid_weather_records.txt", "a", encoding="utf-8") as f:
        f.write(f"Timestamp: {current_time_str} | City: {city_name} | Country: {country} | "
                f"Temp: {temp} | Humidity: {humidity} | Wind: {wind_speed} | Cond: {condition}\n")


# ==========================================
#             CORE BACKEND ENGINE
# ==========================================

def fetch_weather_api(city):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": API_KEY,
        "q": city,
        "aqi": "no"
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"API Connection Error: {e}")
    return None


def insert_weather_data(city_name, country, temp, humidity, wind_speed, condition, 
                        feels_like, pressure, visibility, uv_index, raw_text, validation_status):
    # Bonus Challenge 2: Includes validation_status mapping architecture
    connection = get_db_connection()
    cursor = connection.cursor()
    
    sql_query = """
        INSERT INTO weather_reports (
            city, country, temperature, humidity, wind_speed, `condition`, 
            search_date, search_time, feels_like, pressure, visibility, uv_index, raw_response, validation_status
        ) VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), CURTIME(), %s, %s, %s, %s, %s, %s)
    """
    data_tuple = (
        city_name, country, temp, humidity, wind_speed, condition,
        feels_like, pressure, visibility, uv_index, raw_text, validation_status
    )
    
    cursor.execute(sql_query, data_tuple)
    connection.commit()
    
    cursor.close()
    connection.close()


def execute_weather_search():
    global failed_validations_counter
    
    raw_city = input("Enter City: ").strip()
    if not raw_city:
        print("Error: City name cannot be empty.")
        return
        
    # Standardize input by cleaning out parental country notation placeholders (e.g., "Paris (France)" -> "Paris")
    clean_city = re.sub(r"\s*\(.*?\)", "", raw_city).strip()
    
    # 1. CHECK FOR USER INPUT PARAMETER VALIDATION FAILURE BEFORE API CALL
    if not validate_city(clean_city):
        print("\n>>> VALIDATION REPORT <<<")
        print("City Validation        : Failed (Invalid characters detected in search parameter)")
        print("--------------------------------")
        print("Validation Failed")
        print("Record Not Saved")
        
        failed_validations_counter += 1
        write_validation_log(clean_city, "FAILED")
        export_invalid_record(clean_city, "N/A", "N/A", "N/A", "N/A", "N/A")
        
        # CHANGED: Insert a FAILED placeholder entry into MySQL database
        insert_weather_data(
            city_name=clean_city, country="N/A", temp=0.0, humidity=0, wind_speed=0.0, condition="Invalid Input Pattern", 
            feels_like=0.0, pressure=0.0, visibility=0.0, uv_index=0.0, 
            raw_text="Blocked by local regex preprocessing rules.", validation_status="FAILED"
        )
        print("Invalid search attempt logged into database history.")
        return
        
    print(f"\nFetching data for '{clean_city}'...")
    data = fetch_weather_api(clean_city)
    
    if data:
        city_name = data["location"]["name"]
        country = data["location"]["country"]
        temp = data["current"]["temp_c"]
        humidity = data["current"]["humidity"]
        wind_speed = data["current"]["wind_kph"]
        condition = data["current"]["condition"]["text"]
        feels_like = data["current"]["feelslike_c"]
        pressure = data["current"]["pressure_mb"]
        visibility = data["current"]["vis_km"]
        uv_index = data["current"]["uv"]
        raw_text = str(data)
        
        print("\n--------------------------------")
        print("Weather Report")
        print("--------------------------------")
        print(f"City        : {city_name}")
        print(f"Country     : {country}")
        print(f"Temperature : {temp}°C")
        print(f"Humidity    : {humidity}%")
        print(f"Wind Speed  : {wind_speed} km/h")
        print(f"Condition   : {condition}")
        print("--------------------------------")
        
        # Double check remaining incoming payload validation items (Numbers, speed formats, etc.)
        is_valid = validate_weather_data(city_name, country, temp, humidity, wind_speed, condition)
        
        if is_valid:
            insert_weather_data(city_name, country, temp, humidity, wind_speed, condition, 
                                feels_like, pressure, visibility, uv_index, raw_text, "PASSED")
            write_validation_log(city_name, "PASSED")
            print("Weather report successfully saved to database history.")
        else:
            # 2. CHECK FOR WEATHER API PAYLOAD DATA VALIDATION FAILURE
            print("\nValidation Failed")
            print("Record Not Saved")
            write_validation_log(city_name, "FAILED")
            export_invalid_record(city_name, country, temp, humidity, wind_speed, condition)
            
            # CHANGED: Insert the corrupted/invalid response entry into MySQL as FAILED
            insert_weather_data(city_name, country, temp, humidity, wind_speed, condition, 
                                feels_like, pressure, visibility, uv_index, raw_text, "FAILED")
            print("Corrupted API payload logged into database history.")
    else:
        print("Could not retrieve weather details. Please verify city name spelling.")


def view_weather_history():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    sql_query = "SELECT id, city, temperature, `condition`, search_date, search_time, validation_status FROM weather_reports"
    cursor.execute(sql_query)
    dataset = cursor.fetchall()
    
    if not dataset:
        print("\nNo search history logs found inside the database.")
    else:
        print(f"\n{'ID':<5} | {'City':<15} | {'Temp':<6} | {'Condition':<15} | {'Date':<12} | {'Time':<8} | {'Status':<8}")
        print("-" * 85)
        for row in dataset:
            print(f"{row[0]:<5} | {row[1]:<15} | {row[2]:.1f}°C | {row[3]:<15} | {str(row[4]):<12} | {str(row[5]):<8} | {row[6]}")
            
    cursor.close()
    connection.close()


def view_last_search():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    sql_query = "SELECT id, city, temperature, `condition`, search_date, search_time, validation_status FROM weather_reports ORDER BY id DESC LIMIT 1"
    cursor.execute(sql_query)
    record = cursor.fetchone()
    
    if not record:
        print("\nNo historical search entries logged yet.")
    else:
        print("\n>>> LAST WEATHER SEARCH ENTRY RECORDED <<<")
        print(f"ID: {record[0]} | City: {record[1]} | Temp: {record[2]}°C | Cond: {record[3]} | Checked: {record[4]} at {record[5]} | Status: {record[6]}")
        
    cursor.close()
    connection.close()


def view_extreme_temperature(metric_type):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    sort_order = "DESC" if metric_type == "Hottest" else "ASC"
    sql_query = f"SELECT city, temperature, `condition` FROM weather_reports WHERE validation_status = 'PASSED' ORDER BY temperature {sort_order} LIMIT 1"
    
    cursor.execute(sql_query)
    record = cursor.fetchone()
    
    if not record:
        print("\nHistory tracking database contains no valid records.")
    else:
        print(f"\n>>> {metric_type.upper()} CITY HISTORICALLY TRACKED <<<")
        print(f"Location: {record[0]} | Temperature: {record[1]}°C | Condition: {record[2]}")
        
    cursor.close()
    connection.close()


def display_aggregate_statistics():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    sql_query = "SELECT COUNT(*), MAX(temperature), MIN(temperature), AVG(temperature) FROM weather_reports WHERE validation_status = 'PASSED'"
    cursor.execute(sql_query)
    stats = cursor.fetchone()

    if stats[0] == 0:
        print("\nNo valid tracking entries currently saved to analyze.")
    else:
        print("\n=========================================")
        print("        WEATHER ENGINE STATISTICS        ")
        print("=========================================")
        print(f" Total Stored Searches  : {stats[0]}")
        print(f" Highest Temperature    : {stats[1]:.2f}°C")
        print(f" Lowest Temperature     : {stats[2]:.2f}°C")
        print(f" Average Temperature    : {stats[3]:.2f}°C")
        print("=========================================")
        
    cursor.close()
    connection.close()


def export_weather_history():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    sql_query = "SELECT city, temperature, `condition`, validation_status from weather_reports"
    cursor.execute(sql_query)
    dataset = cursor.fetchall()
    
    if not dataset:
        print("\nDatabase is empty. No data available to export.")
    else:
        with open("weather_history.txt", "w", encoding="utf-8") as target_file:
            for row in dataset:
                target_file.write(f"{row[0]} | {row[1]}°C | {row[2]} | Status: {row[3]}\n\n")
        print("\nSystem logs successfully exported to 'weather_history.txt'.")
        
    cursor.close()
    connection.close()


def delete_weather_history():
    confirm = input("\nAre you sure you want to delete ALL history logs? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Deletion canceled.")
        return
        
    connection = get_db_connection()
    cursor = connection.cursor()
    
    sql_query = "DELETE FROM weather_reports"
    cursor.execute(sql_query)
    connection.commit()
    print(f"\nDatabase cleared successfully. Removed {cursor.rowcount} entries.")
    
    cursor.close()
    connection.close()


def main():
    while True:
        print("\n" + "="*40)
        print("        WEATHER MONITORING SYSTEM        ")
        print("="*40)
        print("1. Check Weather (Fetch, Display & Log)")
        print("2. View All Logged Weather History")
        print("3. View Last Weather Search Entry")
        print("4. Display Hottest City Tracked")
        print("5. Display Coldest City Tracked")
        print("6. Run Metrics Analytical Statistics")
        print("7. Export System Logs to File (.txt)")
        print("8. Clear/Wipe Entire Database History")
        print("9. View Runtime Validation Failures Counter")
        print("10. Exit Application")
        print("="*40)
        
        choice = input("Enter Choice (1-10): ").strip()
        
        if choice == "1":
            execute_weather_search()
        elif choice == "2":
            view_weather_history()
        elif choice == "3":
            view_last_search()
        elif choice == "4":
            view_extreme_temperature("Hottest")
        elif choice == "5":
            view_extreme_temperature("Coldest")
        elif choice == "6":
            display_aggregate_statistics()
        elif choice == "7":
            export_weather_history()
        elif choice == "8":
            delete_weather_history()
        elif choice == "9":
            print(f"\nTotal Failed Validations during current execution session: {failed_validations_counter}")
        elif choice == "10":
            print("\nShutting down backend connection modules. System Offline.")
            break
        else:
            print("\nInvalid input choice. Please select an option from 1 to 10.")


if __name__ == "__main__":
    main()