import datetime
import json
from flask import Flask

from flights_scraper import scrape

app = Flask(__name__)


@app.route('/search/<int:count_journey>/DXBBKK<int:adult><int:child><int:infant>/<option>')
@app.route('/search/<int:count_journey>/DXBBKK<int:adult><int:child>/<option>')
@app.route('/search/<int:count_journey>/DXBBKK<int:adult>/<option>')
@app.route('/search/<int:count_journey>/DXBBKK<int:adult><int:child><int:infant>')
@app.route('/search/<int:count_journey>/DXBBKK<int:adult><int:child>')
@app.route('/search/<int:count_journey>/DXBBKK<int:adult>')
@app.route('/search/<int:count_journey>/DXBBKK')
@app.route('/search/<int:count_journey>/DXBBKK/<option>')
def get_flight_info(count_journey, option=None, adult=1, child=0, infant=0):
    """
    :param count_journey: 1, 2
    :param option: cheap, expensive, short, long, optimal
    :param adult: int
    :param child: int
    :param infant: int
    """
    pax = {'adult': adult, 'child': child, 'infant': infant}
    file_name = 'RS_ViaOW.xml' if count_journey == 1 else 'RS_Via-3.xml'
    flights = scrape(pax, file_name)
    sorted_by_price = sorted(flights, key=lambda a: a['price'])
    sorted_by_duration = sorted(flights, key=lambda a: a['duration_0'])
    optimal = get_optimal(flights)
    result = {
        'cheap': sorted_by_price[0],
        'expensive': sorted_by_price[-1],
        'short': sorted_by_duration[0],
        'long': sorted_by_duration[-1],
        'optimal': optimal
    }

    return json.dumps(result.get(option, flights), default=converter)


def get_optimal(flights):
    """Return the cheapest fligh with duration less than average"""
    result = []
    all_durations = [int(flight['duration_0'].total_seconds()) for flight in flights]
    average_duration = sum(all_durations) / len(all_durations)
    for flight in flights:
        if float(flight['duration_0'].total_seconds()) < average_duration:
            result.append(flight)
    return sorted(result, key=lambda a: a['price'])[0]


def converter(data):
    """Сonvert datetime for json"""
    if isinstance(data, datetime.datetime):
        return data.strftime("%m/%d/%Y, %H:%M:%S")
    elif isinstance(data, datetime.timedelta):
        return str(data)


if __name__ == '__main__':
    app.run(debug=True)
