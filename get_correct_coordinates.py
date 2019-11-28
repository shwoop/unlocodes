from os import environ
from time import sleep
from typing import Optional
from pprint import pprint

import IPython
import numpy as np
import pandas as pd
from requests import get

from unlocodes import (
    load_unlocodes,
    save_output,
    translate_coords_to_lat,
    translate_coords_to_lon,
)

GCPAPIKEY = environ.get('GCPAPIKEY', '')
if not GCPAPIKEY:
    print('PLEASE SET GCPAPIKEY ON THE ENVIRONMENT')
    exit(1)

MAPS_API_URI = 'https://maps.googleapis.com/maps/api'


class Coordinate:
    def __init__(self, latitude=None, longitude=None):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        if self.latitude:
            return f'{self.latitude} {self.longitude}'
        return ''


def _filter_candidate_places(
    place_name: str,
    candidates: dict
) -> Optional[dict]:
    """
    Attempt to filter multiple candidate places
    """

    # is there a perfect match?
    perfect_match = list(
        filter(lambda x: x.get('name') == place_name, candidates)
    )
    if perfect_match:
        return perfect_match[0]

    # Compare names
    import difflib
    from collections import defaultdict
    ratios = defaultdict(list)
    for candidate in candidates:
        # Check for place name with port?
        diff = difflib.SequenceMatcher(a=place_name, b=candidate.get('name')).ratio()
        ratios[diff].append(candidate)

    closest_candidates = ratios[max(ratios.keys())]
    if len(closest_candidates) == 1:
        return closest_candidates[0]

    if len({i['name'] for i in closest_candidates}) == 1:
        return closest_candidates[0]

    # # Strip out any candidates that have candidates who's name is a subset
    # for candidate in list(closest_candidates):
    #     if any(i['name'] in candidate['name'] for i in closest_candidates if i['name'] != candidate['name']):
    #         closest_candidates.pop(candidate)

    return None


def google_says_this_is_at(
    place_name: str,
    response_format='json'
) -> Coordinate:
    places_url = f'{MAPS_API_URI}/place/findplacefromtext/{response_format}'
    params = {
        'key': GCPAPIKEY,
        'input': f'{place_name}{" port" if "port" not in place_name.lower() else ""}',
        'inputtype': 'textquery',
        'fields': 'geometry/location,name'
    }
    response = get(url=places_url, params=params)
    if response.status_code != 200:
        return Coordinate()
    candidates = response.json()['candidates']
    if not candidates:
        print('Oops, we do not have a candidate!')
        return Coordinate()
    if len(candidates) > 1:
        print(f'Oops, we have more than one candidate for {place_name}')
        pprint(candidates)
        candidate = _filter_candidate_places(place_name, candidates)
        if not candidate:
            return Coordinate()
        print(f'decided on {candidate}')
    else:
        candidate = candidates[0]

    location = candidate['geometry']['location']
    return Coordinate(location['lat'], location['lng'])


def do_it(from_unlocodes=False):
    if from_unlocodes:
        codes = load_unlocodes()
        codes = codes.loc[codes['function'].str.contains('1')].copy()
        codes['claimed_lat'] = np.vectorize(translate_coords_to_lat)(
            codes['coordinates']
        )
        codes['claimed_lon'] = np.vectorize(translate_coords_to_lon)(
            codes['coordinates']
        )
        codes_to_process = codes
    else:
        codes = pd.read_csv('output/improved_coordinates.original.csv')
        codes_to_process = codes[codes['new_coords'].isnull()]

    for row_num, row in codes_to_process[['unlocode', 'namewodiacritics']].iterrows():
        coords = google_says_this_is_at(row.namewodiacritics)
        codes.loc[row_num, 'new_coords'] = coords

    save_output(codes, 'improved_coordinates')

    # Launch IPython interactive shell
    user_ns = locals()
    user_ns.update({'codes': codes, 'save_output': save_output})
    IPython.start_ipython(argv=[], user_ns=user_ns)


if __name__ == '__main__':
    do_it()
