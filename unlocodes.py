#!/usr/bin/env python
import argparse
import glob
import os

import IPython
import numpy as np
import pandas as pd


def load_ports() -> pd.DataFrame:
    with open('data/ptrac_ports.csv') as f:
        df = pd.read_csv(f)
    df.columns = ['ptrac_unlocode']
    return df


def load_unlocodes() -> pd.DataFrame:
    file_names = sorted(glob.glob('data/*UNLOCODE*.csv'))
    data_releases = {n.split(' ')[0] for n in file_names}
    if len(data_releases) > 1:
        print(
            'There are multiple releases in the data folder '
            f'({", ".join(data_releases)}), please purge and re-download.'
        )
        exit(1)

    csv_imports = []
    for file_name in file_names:
        with open(file_name, encoding='latin1') as f:
            csv_imports.append(pd.read_csv(f, quotechar='"', header=None))

    df = pd.concat(csv_imports, axis=0, ignore_index=True)
    df.columns = [
        'change',
        'lo_country',
        'lo_city',
        'name',
        'namewodiacritics',
        'subdiv',
        'function',
        'status',
        'date',
        'iata',
        'coordinates',
        'remarks'
    ]

    # Remove the International waters XZ codes
    df = df.loc[df['lo_country'] != 'XZ']

    # make concatenated unlocode
    df['unlocode'] = df['lo_country'] + df['lo_city']

    # remove weird country header rows
    df = df.dropna(subset=['unlocode'])

    # Some rows are duplicated, having the translations in different orders
    #  eg, here(ici) and ici(here)
    #  dropping duplicates will pick the first one in the list.
    df = df.drop_duplicates(subset=['unlocode'])

    return df


def save_output(df: pd.DataFrame, path: str) -> None:
    if not path.endswith('.csv'):
        path += '.csv'
    df.to_csv(f'output/{path}', header=True, index=False)


def translate_coords_to_lat(coord: str):
    return translate_coords(coord, lat=True)


def translate_coords_to_lon(coord: str):
    return translate_coords(coord, lat=False)


def load_ports_2() -> pd.DataFrame:
    with open('data/test_port.csv') as f:
        df = pd.read_csv(f)
    return df


def load_country() -> pd.DataFrame:
    with open('data/test_country.csv') as f:
        df = pd.read_csv(f)
    return df


def load_iso_country() -> pd.DataFrame:
    with open('data/test_isocountry.csv') as f:
        df = pd.read_csv(f)
    return df


def translate_coords(coord: str, lat=True) -> str:
    """
    Transform unlocode coordinates to lat and lon.

    input format DDDMMP, where DDD is degrees, MM is minutes, and P is the
    pole.
    output formatis will be [-]DEG.MIN
    utput formatis will b
    """
    try:
        coord = coord.split()[0 if lat else 1]
    except:
        return ''
    d, m, pole = coord[:-3], coord[-3:-1], coord[-1]
    return f'{"-" if pole in ["S", "W"] else ""}{int(d)}.{int(m)}'


def main(output: bool) -> None:
    ports = load_ports()
    unlocodes = load_unlocodes()
    country = load_country()
    ports2 = load_ports_2()
    isocountry = load_iso_country()


    known_unlocodes = ports2[['code']].copy()
    known_unlocodes.columns = ['ptrac_unlocode']
    # attach known ports
    codes_with_ptrac_ports = pd.merge(
        unlocodes,
        known_unlocodes,
        how='left',
        left_on='unlocode',
        right_on='ptrac_unlocode'
    )

    # attach isocountry for country codes
    isocountry_codes = isocountry[['alpha_2', 'alpha_3', 'id']].copy()
    isocountry_codes.columns = ['alpha_2', 'alpha_3', 'iso_country_id']
    codes_ptrac_and_isocountry = pd.merge(
        codes_with_ptrac_ports,
        isocountry_codes,
        how='left',
        left_on='lo_country',
        right_on='alpha_2'
    )

    # attach country for country id
    country_codes = country[['code', 'iso_3166_1_alpha_2', 'name']].copy()
    country_codes.columns = [
        'country_code', 'iso_3166_1_alpha_2', 'country_code_name'
    ]
    codes_ptrac_and_country = pd.merge(
        codes_ptrac_and_isocountry,
        country_codes,
        how='left',
        left_on='alpha_3',
        right_on='country_code'
    )

    data = codes_ptrac_and_country

    # strip out known unlocodes
    data = data.loc[pd.isnull(data['ptrac_unlocode'])].copy()

    # dump non standard country code ports
    non_standard_country_code_rows = (
        data.loc[pd.isnull(data['country_code'])]
    )
    data = data.loc[pd.notnull(data['country_code'])]

    # generate coordinates
    data['latitude'] = (
        np.vectorize(translate_coords_to_lat)(data['coordinates'])
    )
    data['longitude'] = (
        np.vectorize(translate_coords_to_lon)(data['coordinates'])
    )

    # generate scale
    data['scale'] = 0.1
    data['polygon'] = None
    data['position'] = None
    data['ihs_port_id'] = None
    data['world_port_number'] = None
    data['port_source'] = '2019-1'
    data['iso_country_id'] = data[['iso_country_id']].fillna('0').astype(int)

    final = data[[
        'unlocode', 'namewodiacritics', 'country_code', 'latitude', 'longitude',
        'scale', 'polygon', 'position', 'iso_country_id', 'port_source',
        'ihs_port_id', 'world_port_number'
    ]].copy()
    final.columns = [
        'code', 'name', 'country_code_id', 'latitude', 'longitude',
        'scale', 'polygon', 'position', 'iso_country_id', 'port_source',
        'ihs_port_id', 'world_port_number'
    ]

    # save csvs
    if output:
        os.makedirs('output', exist_ok=True)
        save_output(data, 'raw_data')
        save_output(final, 'ports_to_insert')

    # Launch IPython interactive shell
    user_ns = locals()
    user_ns.update({'pd': pd, 'save_output': save_output})
    IPython.start_ipython(argv=[], user_ns=user_ns)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UNLOCODE data analysis.')
    parser.add_argument(
        '-o',
        dest='output',
        action='store_true',
        default=False,
        help='save Output csv files to ./output/ (default: False)'
    )
    args = parser.parse_args()
    main(args.output)
