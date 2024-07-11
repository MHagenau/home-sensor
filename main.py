import time
import psycopg2
from sense_hat import SenseHat
from datetime import datetime

# Initialize SenseHat
sense = SenseHat()

# Database connection details
DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_HOST = "your_db_host"
DB_PORT = "your_db_port"


def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        cpu_temp = float(f.read()) / 1000.0
    return cpu_temp


def get_sensor_readings():
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


def insert_readings_to_db(readings):
    try:
        # Connect to the database
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        # Insert the sensor readings into the database
        cursor.execute("""
            INSERT INTO sensor_readings (
                timestamp, temperature, temperature_from_humidity, pressure, humidity, cpu_temp
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
        """, (
            datetime.now(), readings['temperature'], readings['temperature_from_humidity'], 
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
        readings = get_sensor_readings()
        insert_readings_to_db(readings)
        time.sleep(60)
