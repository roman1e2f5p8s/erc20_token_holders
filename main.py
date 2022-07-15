#!/usr/bin/env python3.9

# This script can be used to calculate weekly top N ERC20 token balances from CSV files 
# downloaded from GCS.
#
# Author:  Roman Overko
# Contact: roman.overko@iota.org
# Date:    July 15, 2022

import os
import argparse
import datetime
import pandas as pd
from time import time
from collections import deque, defaultdict
from io import StringIO


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
            '--verbose',
            action='store_true',
            default=False,
            help='Print detailed output to console, defaults to False'
            )
    optional_args.add_argument(
            '--top',
            type=int,
            default=10000,
            help='How many top holders to consider, defaults to 10000',
            )
    optional_args.add_argument(
            '--keep_address',
            action='store_true',
            default=False,
            help='Keep address along with its values, defaults to False'
            )
    args = parser.parse_args()
    
    DIR = os.path.join(args.dir, args.name)
    if not os.path.isdir(DIR):
        raise FileNotFoundError('Directory \"{}\" does not exist! Please download data from GCS'.\
                format(DIR))

    CSV_DIR = os.path.join(DIR, 'csv')
    if not os.path.isdir(CSV_DIR):
        raise FileNotFoundError('Directory \"{}\" does not exist! Please download data from GCS'.\
                format(CSV_DIR))
    
    CSV_FILES = os.listdir(CSV_DIR)
    if not CSV_FILES:
        raise FileNotFoundError('Directory \"{}\" contains no CSV files! Please download data from GCS'\
                .format(CSV_DIR))

    CSV_FILES = list(sorted(CSV_FILES))
    
    # get the first and last dates
    df = pd.read_csv(os.path.join(CSV_DIR, CSV_FILES[0]), nrows=1)
    with open(os.path.join(CSV_DIR, CSV_FILES[-1]), 'r') as f:
        q = deque(f, 1)
    df = pd.concat([df, pd.read_csv(StringIO(''.join(q)), names=df.columns)])
    df['block_date'] = pd.to_datetime(df['block_date'])
    FIRST_DATE, LAST_DATE = df['block_date']
    del df
    assert LAST_DATE > FIRST_DATE
    LAST_DATE += datetime.timedelta(days=-1)

    # calculate the end date as the last sunday before LAST_DATE
    if not LAST_DATE.weekday() == 6:
        END_DATE = LAST_DATE - datetime.timedelta(days=(LAST_DATE.weekday() + 1))
    else:
        END_DATE = LAST_DATE
    assert END_DATE.weekday() == 6 # the end date of balances will be the last Sunday w.r.t. LAST_DATE
    print('You have data collected until \'{}\' including.'.format(LAST_DATE.strftime('%Y-%m-%d')))
    print('The last date, for which top balances will be calculated, is\n\tthe last Sunday before '
            '\'{}\': namely, \'{}\'.'.format(LAST_DATE.strftime('%Y-%m-%d'), 
                END_DATE.strftime('%Y-%m-%d')))
    
    # calculate the start date as the first sunday after FIRST_DATE
    if not FIRST_DATE.weekday() == 6:
        START_DATE = FIRST_DATE + datetime.timedelta(days=(6 - FIRST_DATE.weekday()))
    else:
        START_DATE = FIRST_DATE
    START_DATE += datetime.timedelta(weeks=1)
    assert START_DATE.weekday() == END_DATE.weekday()
    print('\nYou have data collected since \'{}\' including.'.format(FIRST_DATE.strftime('%Y-%m-%d')))
    print('The first date, for which top balances will be calculated, is\n\tthe first Sunday after '
            'a week after \'{}\': namely, \'{}\'.'.format(FIRST_DATE.strftime('%Y-%m-%d'), 
                START_DATE.strftime('%Y-%m-%d')))
    
    # calculate number of weeks
    NUM_WEEKS = (END_DATE - START_DATE).days
    assert NUM_WEEKS % 7 == 0
    NUM_WEEKS = NUM_WEEKS // 7 + 1
    print('\nThere are {} weeks between \'{}\' and \'{}\'.'.format(NUM_WEEKS,
        START_DATE.strftime('%Y-%m-%d'), END_DATE.strftime('%Y-%m-%d')))
    DELTA = datetime.timedelta(weeks=1)

    date = START_DATE
    week_counter = 1
    till_date_df = pd.DataFrame()
    main_df = pd.DataFrame()
    address_balance_dict = defaultdict(float)
    
    print('\nCalculating balances for \"{}\"...'.format(args.name))
    start = time()
    for i, file_ in enumerate(CSV_FILES):
        df = pd.read_csv(os.path.join(CSV_DIR, file_), dtype={'value': float}, parse_dates=['block_date'])
        
        till_date_df = pd.concat([till_date_df, df[df['block_date'] <= date][['address', 'value']]])
        remain_df = df[df['block_date'] > date]
    
        while not remain_df.empty:
            # print('Save at {}'.format(date.strftime('%Y-%m-%d')))
            if args.verbose:
                print(' week {} out of {}'.format(week_counter, NUM_WEEKS), end='\r')

            z1 = zip(*till_date_df.to_dict('list').values())
            for address, value in z1:
                address_balance_dict[address] += value

            if not args.keep_address:
                sorted_d = [b for b in address_balance_dict.values() if b > 0]
                sorted_d.sort(reverse=True)
                sorted_d_len = len(sorted_d)
                cut = args.top if sorted_d_len >= args.top else sorted_d_len
                df = pd.DataFrame({date.strftime('%Y-%m-%d'): sorted_d[:cut]})
            else:
                address_balance_dict = defaultdict(float, {k: v for k, v in sorted(
                    address_balance_dict.items(), reverse=True, key=lambda item: item[1]) if v})
                sorted_d_len = len(address_balance_dict)
                cut = args.top if sorted_d_len >= args.top else sorted_d_len
                df = pd.DataFrame({date.strftime('%Y-%m-%d'): list(address_balance_dict.keys())[:cut]})
                df = pd.concat([df, pd.DataFrame({'': list(address_balance_dict.values())[:cut]})], axis=1)

            main_df = pd.concat([main_df, df], axis=1)

            week_counter += 1
            date += DELTA
    
            df = remain_df
            till_date_df = df[df['block_date'] <= date][['address', 'value']]
            remain_df = df[df['block_date'] > date]

    assert week_counter - 1 == NUM_WEEKS
    assert main_df.shape[1] == NUM_WEEKS if not args.keep_address else NUM_WEEKS // 2
    
    print(' ' * 50, end='\r')
    print('Calculating done! Saving data...')
    fname = os.path.join(DIR, 'top{}_token_holders_{}'.format(args.top, END_DATE.strftime('%Y-%m-%d')) +\
            '_addresses' * args.keep_address + '.csv')
    main_df.to_csv(fname)
    if args.verbose:
        print(main_df.iloc[:20, :])
    print('Elapsed time: {:.4f} s'.format(time() - start))
    print('Data saved in {}'.format(fname))


if __name__ == '__main__':
    main()
