from flask import Flask, render_template, request, flash, session
import requests
import xml.etree.ElementTree as ET
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
BASE_URL = 'https://flydata.avinor.no/XmlFeed.asp'
TIME_FROM = -24
TIME_TO = 24

def format_time(iso_time):
    if iso_time:
        dt = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d %B %Y, %H:%M")
    return "N/A"

def parse_flight_data(root):
    flights = []
    for flight in root.findall(".//flight"):
        flight_data = {
            'uniqueId': flight.attrib.get('uniqueID'),
            'flightId': flight.findtext('flight_id'),
            'domestic_or_international': flight.findtext('dom_int'),
            'scheduled_time': format_time(flight.findtext('schedule_time')),
            'arrival_departure': flight.findtext('arr_dep'),
            'airport': flight.findtext('airport'),
            'airline': flight.findtext('airline'),
            'status_code': flight.find('./status').attrib.get('code') if flight.find('./status') is not None else None,
            'status_time': format_time(flight.find('./status').attrib.get('time')) if flight.find('./status') is not None else None,
            'gate': flight.findtext('gate'),
            'belt_number': flight.findtext('belt_number'),
        }
        flights.append(flight_data)
    return flights


#fetch flight data from Avinor API and apply filters
def get_flight_data(airport_code, time_from=TIME_FROM, time_to=TIME_TO, direction=None, codeshare='Y', airline=None, flight_number=None):
    params = {
        'airport': airport_code,
        'TimeFrom': time_from,
        'TimeTo': time_to,
        'direction': direction,
        'codeshare': codeshare
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        flights = parse_flight_data(root)

        # filter by airline
        if airline:
            flights = [flight for flight in flights if flight['airline'] and airline.lower() in flight['airline'].lower()]

        # filter by flight number
        if flight_number:
            flights = [flight for flight in flights if flight['flightId'] and flight_number.lower() in flight['flightId'].lower()]

        return flights

    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        flash("Network error occurred while fetching flight data. Please try again later.", "danger")
        return []
    except ET.ParseError:
        print("Failed to parse the response XML.")
        flash("Error parsing flight data. Please check the airport code and try again.", "danger")
        return []

@app.route('/', methods=['GET', 'POST'])
def home():
    flights = []
    airport_code = session.get('airport_code', '')
    direction = session.get('direction', '')
    airline = session.get('airline', '')
    flight_number = session.get('flight_number', '')
    sort_by_status = session.get('sort_by_status', '')

    if request.method == 'POST':
        #process user input from form
        airport_code = request.form.get('airport_code').upper().strip()
        #validate IATA airport code
        if not airport_code.isalpha() or len(airport_code) != 3:
            flash("Invalid IATA code. Please enter a 3-letter airport code.", "danger")
            return render_template('index.html', flights=flights, airport_code=airport_code, direction=direction, airline=airline, flight_number=flight_number)

        direction_input = request.form.get('direction')
        direction = direction_input if direction_input in ['A', 'D'] else None
        
        airline = request.form.get('airline').strip()
        flight_number = request.form.get('flight_number').strip()

        # handle status sorting
        sort_by_status = request.form.get('sort_by_status')
        #fetch and filter flight data
        flights = get_flight_data(airport_code=airport_code, direction=direction, airline=airline, flight_number=flight_number)

        #sort flights by status if selected
        if sort_by_status:
            flights = sorted(flights, key=lambda x: x['status_code'])
        # store form values in session
        session['airport_code'] = airport_code
        session['direction'] = direction
        session['airline'] = airline
        session['flight_number'] = flight_number
        session['sort_by_status'] = sort_by_status

    return render_template('index.html', flights=flights, airport_code=airport_code, direction=direction, airline=airline, flight_number=flight_number, sort_by_status=sort_by_status)

if __name__ == '__main__':
    app.run(debug=True)
