# Avinor Flight Status

## Overview

The Avinor Flight Status application allows users to track flight information by entering an airport's IATA code. The app retrieves real-time flight data from the Avinor API, displaying arrivals and departures, and providing filtering options based on airline and flight number.

## Features

- Fetch flight data from Avinor's XML API.
- Filter by IATA airport code, direction (arrivals/departures), airline, and flight number.
- Sort flights based on their status (On Time, Delayed, Canceled).
- Flash messages for user feedback on form submissions and errors.

## Technologies Used

- Python
- Flask
- HTML/CSS
- Requests (for making API calls)
- XML Parsing

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:thisisomar4/Avinor-flight-data.git
   cd AvinorFlightData


2. Set up a virtual environment:

python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install the required packages:

pip install -r requirements.txt



4. Run the application:

python3 FlightStatus.py

Open your web browser and go to http://127.0.0.1:5000 to access the application.


## License
This project is licensed under the MIT License