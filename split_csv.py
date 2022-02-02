# This script can be used to split CSV files downloaded from GCS by weekly data saved into pickle files.
# The resulting pickle files can then be processed by script calc_top_holders.py
#
# Author:  Roman Overko
# Contact: roman.overko@iota.org
# Date:    February 02, 2022

import os
import argparse
import datetime
import pandas as pd
from time import time


def main():
    formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50)
    parser = argparse.ArgumentParser(
            description='Converts and splits CSV files (downloaded from GCS) to weekly data saved in '
                'pickle files',
            add_help=False,
            formatter_class=formatter,
            )
    
    # required arguments
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument(
            '--dir',
            type=str,
            required=True,
            help='Path to parent directory with ERC20 tokens data',
            )
    required_args.add_argument(
            '--name',
            type=str,
            required=True,
            help='Name of ERC20 token (also the name of the folder with CSV files)',
            )
    
    # optimal arguments
    optional_args = parser.add_argument_group('optional arguments')
    optional_args.add_argument(
            '-h',
            '--help',
            action='help',
            help='show this help message and exit',
            )
    optional_args.add_argument(
            '--rm',
            action='store_true',
            default=False,
            help='Remove CSV files after converting, defaults to False'
            )
    optional_args.add_argument(
            '--end_date',
            type=str,
            default='2022-01-16',
            help='End date to consider, defaults to 2022-01-16'
            )
    optional_args.add_argument(
            '--verbose',
            action='store_true',
            default=False,
            help='Print detailed output to console, defaults to False'
            )
    args = parser.parse_args()
    
    DIR = os.path.join(args.dir, args.name)
    if not os.path.isdir(DIR):
        raise FileNotFoundError('Directory \"{}\" does not exist!'.format(DIR))
    
    CSV_FILES = [f for f in os.listdir(DIR) if f[-3:] == 'csv']
    if not CSV_FILES:
        raise FileNotFoundError('Directory \"{}\" contains no CSV files!'.format(DIR))
    CSV_FILES = list(sorted(CSV_FILES))
    N_FILES = len(CSV_FILES)
    
    df = pd.read_csv(os.path.join(DIR, CSV_FILES[0]), nrows=1, parse_dates=['block_date'])
    first_date = df['block_date'].iloc[0]
    del df
    
    END_WEEKDAY = datetime.datetime.strptime(args.end_date, '%Y-%m-%d').weekday()
    DELTA = datetime.timedelta(weeks=1)
    
    days_ahead = END_WEEKDAY - first_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    START_DATE = first_date + datetime.timedelta(days_ahead)
    assert START_DATE.weekday() == END_WEEKDAY
    print('Use \"{}\" as start_date for calc_top_holders.py'.\
            format(datetime.datetime.strftime(START_DATE, '%Y-%m-%d')))
    
    date = START_DATE + DELTA
    csv_rows_counter = 0
    pkl_rows_counter = 0
    week_counter = 0
    to_save_df = pd.DataFrame()
    
    print('Converting data in \"{}\"...'.format(DIR))
    start = time()
    for i, file_ in enumerate(CSV_FILES):
        if args.verbose:
            print(' file {} out of {}'.format(i, N_FILES - 1), end='\r')
    
        fname = os.path.join(DIR, file_)
        df = pd.read_csv(fname, dtype={'value': float}, parse_dates=['block_date'])
        csv_rows_counter += df.shape[0]
        
        to_save_df = pd.concat([to_save_df, df[df['block_date'] <= date][['address', 'value']]])
        remain_df = df[df['block_date'] > date]
    
        while not remain_df.empty:
            to_save_df.to_pickle(os.path.join(DIR, '{:04d}.pkl'.format(week_counter)))
            pkl_rows_counter += to_save_df.shape[0]
            week_counter += 1
            date += DELTA
    
            df = remain_df
            to_save_df = df[df['block_date'] <= date][['address', 'value']]
            remain_df = df[df['block_date'] > date]
    
        if args.rm:
            os.remove(fname)
    
    to_save_df.to_pickle(os.path.join(DIR, '{:04d}.pkl'.format(week_counter)))
    pkl_rows_counter += to_save_df.shape[0]
    assert pkl_rows_counter == csv_rows_counter
    
    print('Converting done!')
    print('Elapsed time: {:.4f} s'.format(time() - start))


if __name__ == '__main__':
    main()
