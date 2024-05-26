import json
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict
import os
from aircraft_seat_list import aircraft_seat_capacity  # Import the aircraft seat capacity list

# Load JSON data from files
folder_path = "airport_data"
file_names = ["DNMM.json", "DNAA.json", "KLAX.json", "KSFO.json", "YSSY.json", "YMML.json"]
airport_codes = ["DNMM", "DNAA", "KLAX", "KSFO", "YSSY", "YMML"]

flights = []

for file_name in file_names:
    file_path = os.path.join(folder_path, file_name)
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            for flight in data:
                if isinstance(flight, dict):
                    flight['origin'] = file_name.split('.')[0]  # Add origin airport code to each flight
                    flights.append(flight)
                else:
                    print(f"Skipping malformed entry in {file_name}: {flight}")
    except json.JSONDecodeError as e:
        print(f"Error reading {file_path}: {e}")

# Define start and end dates
start_date = datetime(2023, 5, 25)
end_date = datetime(2024, 5, 22)
current_date = start_date

# Prepare a structure to hold seat matrices for each week
seat_matrices = {}
flight_counts = {}
missing_models = set()


# Iterate through each week
while current_date < end_date:
    week_end_date = current_date + timedelta(days=7)
    weekly_seat_matrix = defaultdict(lambda: defaultdict(int))
    weekly_flight_count = defaultdict(lambda: defaultdict(int))

    # Filter flights for the current week
    for flight in flights:
        try:
            movement_time = datetime.strptime(flight["movement"]["scheduledTime"]["utc"], "%Y-%m-%d %H:%MZ")
            if current_date <= movement_time < week_end_date:
                origin = flight["origin"]
                destination = flight["movement"]["airport"].get("icao")  # Use .get to avoid KeyError
                if destination and destination in airport_codes and origin in airport_codes:
                    aircraft = flight.get("aircraft", {})
                    if isinstance(aircraft, dict):
                        model = aircraft.get("model")
                        if model:
                            seats = aircraft_seat_capacity.get(model, 0)
                            if seats == 0:
                                missing_models.add(model)
                            # Accumulate seats for both directions in the same field
                            weekly_seat_matrix[origin][destination] += seats
                            weekly_seat_matrix[destination][origin] += seats
                            # Increment flight count for both directions
                            weekly_flight_count[origin][destination] += 1
                            weekly_flight_count[destination][origin] += 1
                        else:
                            print(f"Missing model for flight from {origin} to {destination}")
                    else:
                        print(f"Aircraft data is not a dictionary for flight from {origin} to {destination}: {aircraft}")
        except KeyError as e:
            print(f"Missing key in flight data: {e}")
        except ValueError as e:
            print(f"Error parsing date for flight: {e}")

    # Save the weekly matrices
    seat_matrices[current_date.strftime("%Y-%m-%d")] = weekly_seat_matrix
    flight_counts[current_date.strftime("%Y-%m-%d")] = weekly_flight_count

    # Move to the next week
    current_date = week_end_date

# Calculate average seats per flight and save to CSV in the same folder as JSON files
for week in seat_matrices:
    seat_matrix = seat_matrices[week]
    flight_count = flight_counts[week]
    average_seat_matrix = defaultdict(lambda: defaultdict(int))

    for origin in seat_matrix:
        for destination in seat_matrix[origin]:
            if flight_count[origin][destination] > 0:
                average_seat_matrix[origin][destination] = seat_matrix[origin][destination] // flight_count[origin][destination]

    df = pd.DataFrame(average_seat_matrix).fillna(0).astype(int)
    df = df.reindex(index=airport_codes, columns=airport_codes, fill_value=0)
    df.to_csv(os.path.join(folder_path, f"seat_matrix_{week}.csv"))

# Log missing aircraft models
if missing_models:
    with open(os.path.join(folder_path, "missing_aircraft_models.log"), 'w') as log_file:
        for model in missing_models:
            log_file.write(f"Missing aircraft model: {model}\n")

print("Processing complete. Seat matrices have been saved to CSV files in the same folder as the JSON files.")
print("Missing aircraft models have been logged.")