import time
import os
import obd
import random

connection = obd.OBD()
logs = []
last_voice_alert = 0

if connection.is_connected():
    mode = "REAL"
    print("Scanning For Engine Codes")
    codes = connection.get_dtc()
else:
    mode = "SIMULATOR"
    print('No adapter found. Starting in SIMULATOR MODE')
    codes = [("P0420", "Catalyst System Efficiency Below Threshold")] # FAKE CODE
    time.sleep(2)

if codes:
    print(f"--- DIAGNOSTIC REPORT ---")
    for code_name, description in codes:
        with open("engine_codes_log.txt", "a") as f:
            f.write(f"{time.ctime()}: [{code_name}] - {description} \n")
    print("-" * 32)

cvt_temp_sim = 20
temp_c_sim = 25

def detect_vehicle(connection):
    if not connection.is_connected():
        return "SIMULATOR"
    
    try:
        vin_response = connection.query(obd.commands.VIN)
        vin = str(vin_response.value)
        print(f"DETECTED VIN: {vin}")

        if "JN8" in vin:
            return "NISSAN"
        elif "3VW" in vin or "WVW" in vin:
            return "JETTA"
        else:
            return "UNKNOWN"
    except:
        return "UNKNOWN"
    
vehicle_type = detect_vehicle(connection)
print(f"Configuring system for: {vehicle_type}")

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    current_time = time.time()        


    if mode == "REAL":

        r_rpm = connection.query(obd.commands.RPM)
        r_temp_c = connection.query(obd.commands.COOLANT_TEMP)

        rpm = r_rpm.value.magnitude if not r_rpm.is_null() else 0
        temp_c = r_temp_c.value.magnitude if not r_temp_c.is_null() else 0
        
        if vehicle_type == "NISSAN":
            r_cvt = connection.query(obd.commands['0121'])
            car_name = "2014 Nissan Rouge Select"

            cvt_temp = r_cvt.value.magnitude if not r_cvt.is_null() else 0

        elif vehicle_type == "JETTA":
            car_name = "1996 Voltwagen Jetta GLX"

            cvt_temp = 0
        
        else:
            car_name = "Unknown Vehicle"
            cvt_temp = 0

    else:
        car_name = "Simulator Vehicle"
        rpm = random.randint(800, 3000)
        temp_c = 90
        cvt_temp_sim += 1
        cvt_temp = cvt_temp_sim

    print(f"--- {car_name} Vitals ---")
    print(f"Engine Speed: {rpm} RPM")

    if temp_c > 110:
        print(f"Coolant Temp: {temp_c}°C \nWARNING: COOLANT OVERHEATING")
        os.system('say"Warning: Coolant Temperature High"')
        logs.append("Coolant Overheat Detected")
        with open("nissan_health_log.txt", "a") as f:
            f.write(f"{time.ctime()}: Coolant Hot - {temp_c}C\n")
    else:
        print(f"Coolant Temp: {temp_c}°C")

    if cvt_temp > 100:
        print(f"CVT Temp: {cvt_temp}°C \nWARNING: CVT FUILD OVERHEATING")
        logs.append("CVT Fuild Overheat Detected")
        with open("nissan_health_log.txt", "a") as f:
            f.write(f"{time.ctime()}: CVT Hot - {cvt_temp}C\n")
    else:
        print(f"CVT Temp: {cvt_temp}°C")

    print("-" * 32)

    if cvt_temp > 100:
        if current_time - last_voice_alert > 5:
            os.system('say "Warning: Transmission Overheating"&')
            last_voice_alert = current_time

    if cvt_temp > 106:
        if current_time - last_voice_alert > 5:
            os.system('say "Emergency: Engine Overheating"&')
            last_voice_alert = current_time

    print(f"Total Events Logged: {len(logs)}")
    time.sleep(1)