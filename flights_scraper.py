"""Scrape xml files"""


from collections import defaultdict
from datetime import datetime
import xml.etree.cElementTree as ET


def scrape(pax, file_name):
    """The main function"""
    count_journey = 1 if 'OW' in file_name else 2
    response = ET.parse(file_name)
    flights_info = response.findall('.//PricedItineraries/Flights')
    result = list(collect_flight_info(flights_info, count_journey, pax))
    return result


def collect_flight_info(flights_info, count_journey, pax):
    """Flight information cycle"""
    tags = ['OnwardPricedItinerary'] if count_journey == 1 else [
        'OnwardPricedItinerary', 'ReturnPricedItinerary'
    ]
    for flight_info in flights_info:
        flight = get_base_flight_info(flight_info.find('./Pricing'), pax)
        for index, tag in enumerate(tags):
            for itinerary in flight_info.findall('.//{tag}/Flights/Flight'.format(tag=tag)):
                flight['itineraries'][index].append(collect_itinerary_info(itinerary))
            flight['duration_{}'.format(index)] = \
                flight['itineraries'][index][-1]['arr_time'] - \
                flight['itineraries'][index][0]['dep_time']
        yield flight


def get_base_flight_info(flight_info, pax):
    """Return general information regarding the entire flight"""
    currency = flight_info.attrib['currency']
    path = './ServiceCharges[@type="Single{pax}"]'
    price = []
    for pax_name, value in pax.items():
        if value:
            prices = flight_info.findall(path.format(pax=pax_name.title()))
            price.append(
                value * float(
                    [p.text for p in prices if p.attrib['ChargeType'] == 'TotalAmount'][0]
                )
            )
    return {'price': sum(price), 'currency': currency, 'itineraries': defaultdict(list)}


def collect_itinerary_info(itinerary_info):
    """Return information for each flight"""
    return {
        'from_iata': itinerary_info.find('./Source').text,
        'to_iata': itinerary_info.find('./Destination').text,
        'dep_time': datetime.strptime(
            itinerary_info.find('./DepartureTimeStamp').text, '%Y-%m-%dT%H%M'
        ),
        'arr_time': datetime.strptime(
            itinerary_info.find('./ArrivalTimeStamp').text, '%Y-%m-%dT%H%M'
        ),
        'operating_code': itinerary_info.find('./Carrier').attrib['id'],
        'flight_number': itinerary_info.find('./FlightNumber').text
    }
