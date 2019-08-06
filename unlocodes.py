#!/usr/bin/python3
import argparse
import glob
import os

import IPython
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

    # make concatenated unlocode
    df['unlocode'] = df['lo_country'] + df['lo_city']

    # remove weird country header rows
    df = df.dropna(subset=['unlocode'])

    return df


def save_output(df: pd.DataFrame, path: str) -> None:
    if not path.endswith('.csv'):
        path += '.csv'
    df.to_csv(f'output/{path}', header=True)


def main(output: bool) -> None:
    ports = load_ports()
    unlocodes = load_unlocodes()

    merged = pd.merge(
        unlocodes,
        ports,
        how='outer',
        left_on='unlocode',
        right_on='ptrac_unlocode'
    )

    # unlocodes found in ptrac that do not exist
    ptrac_exclusive = (
        merged.loc[pd.isnull(merged['unlocode'])]['ptrac_unlocode']
    )

    # unlocodes missing from ptrac
    missing = merged.loc[pd.isnull(merged['ptrac_unlocode'])]

    # missing that are nautical PORTS!
    missing_ports = missing.loc[missing['function'].str.contains('1')]

    # proposed attition to ptrac
    proposed_addition = merged.loc[
        merged['status'].isin(['AA', 'AC', 'AF', 'AI', 'AI', 'RL', 'QQ']) &
        pd.isna(merged['ptrac_unlocode'])
    ]

    # save csvs
    if output:
        os.makedirs('output', exist_ok=True)
        save_output(merged, 'full_data')
        save_output(ptrac_exclusive, 'ptrac_only_ports')
        save_output(missing, 'missing_unlocodes')
        save_output(missing_ports, 'missing_unlocodes_that_are_ports')
        save_output(proposed_addition, 'ports_to_add_to_ptrac')

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
