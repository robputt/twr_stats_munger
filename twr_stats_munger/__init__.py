import json
import operator
import collections
import requests
from bs4 import BeautifulSoup


def get_sec(time_str):
    """Get mins from time."""
    h, m = time_str.split(':')
    return int(h) * 60 + int(m)


def get_stats_page(url='http://fsmine.dhis.org/stats/showstats.cgi'):
    stats_resp = requests.get(url)
    if stats_resp.status_code != 200:
        raise Exception("Error fetching stats from %s" % url)
    return stats_resp.text


def extract_eigth_table(stats_page):
    stats_soup = BeautifulSoup(stats_page, 'lxml')
    table = stats_soup.findAll('table')[8]
    return table


def extract_table_rows(table):
    rows = table.findAll(name='tr')
    towers = []
    for row in rows:
        cols = row.findAll(name='td')
        tower = cols[1].text
        time_online = cols[3].text
        towers.append({'tower': tower.strip(), 'time_online': time_online.strip()})
    return towers


def combine_tower_hours(towers):
    combined_towers = {}

    for tower in towers:
        airport_icao = tower['tower'].split('_')[0]
        if combined_towers.get(airport_icao):
            current_time = combined_towers[airport_icao]
            additional_time = get_sec(tower['time_online'])
            combined_towers[airport_icao] += additional_time
        else:
            current_time = get_sec(tower['time_online'])
            combined_towers[airport_icao] = current_time

    combined_towers = sorted(combined_towers.items(),
                             key=lambda kv: kv[1],
                             reverse=True)[:20]

    ret_dict = {}
    for tower in combined_towers:
        ret_dict[tower[0]] = tower[1]
    return ret_dict


def main():
    stats_page = get_stats_page()
    eigth_table = extract_eigth_table(stats_page)
    towers = extract_table_rows(eigth_table)
    combined_hours = combine_tower_hours(towers)
    print(json.dumps(combined_hours, indent=4))


if __name__ == '__main__':
    main()
