import time
import psycopg2
import json
from sense_hat import SenseHat
from datetime import datetime, timezone


# Load database connection details from JSON file
def load_db_config(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)


def get_cpu_temperature() -> float:
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        cpu_temp = float(f.read()) / 1000.0
    return cpu_temp


def get_sensor_readings() -> dict:
    # Fetch sensor data
    temperature = sense.get_temperature()
    temperature_from_humidity = sense.get_temperature_from_humidity()
    pressure = sense.get_pressure()
    humidity = sense.get_humidity()
    cpu_temp = get_cpu_temperature()

    return {
        'temperature': temperature,
        'temperature_from_humidity': temperature_from_humidity,
        'pressure': pressure,
        'humidity': humidity,
        'cpu_temp': cpu_temp
    }

def insert_readings_to_db(readings, db_config):
    try:
        # Connect to the database
        connection = psycopg2.connect(
            dbname=db_config["DB_NAME"],
            user=db_config["DB_USER"],
            password=db_config["DB_PASSWORD"],
            host=db_config["DB_HOST"],
            port=db_config["DB_PORT"]
        )
        cursor = connection.cursor()

        # Insert the sensor readings into the database
        cursor.execute("""
            INSERT INTO readings.raspberry_readings (
                timestamp, temperature, temperature_from_humidity, pressure, humidity, cpu_temp
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
        """, (
            datetime.now(timezone.utc), readings['temperature'], readings['temperature_from_humidity'], 
            readings['pressure'], readings['humidity'], readings['cpu_temp']
        ))

        # Commit the transaction
        connection.commit()

    except Exception as error:
        print(f"Error inserting data: {error}")
    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    while True:
        sense = SenseHat()
        readings = get_sensor_readings()
        db_config = load_db_config('secrets.json')
        insert_readings_to_db(readings, db_config)
        time.sleep(60)
