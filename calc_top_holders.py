#!/usr/bin/env python3.9

# This script can bee used to calcualted top ERC20 token holders from weekly pickle files.
#
# Author:  Roman Overko
# Contact: roman.overko@iota.org
# Date:    February 02, 2022

import os
import gc
import pickle
import argparse
import datetime
import pandas as pd
from time import time
from collections import defaultdict


def main():
    formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50)
    parser = argparse.ArgumentParser(
            description='Calculates top token holders from pickle files split by weeks',
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
            help='Name of ERC20 token (also the name of the folder with pickle files)',
            )
    required_args.add_argument(
            '--start_date',
            type=str,
            required=True,
            help='Start date to consider (this date is printed by split_csv.py)'
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
            '--top',
            type=int,
            default=10000,
            help='How many top holders to consider, defaults to 10000',
            )
    optional_args.add_argument(
            '--rm',
            action='store_true',
            default=False,
            help='Remove pickle files after calculating, defaults to False'
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
    
    PKL_DIR = os.path.join(DIR, 'pkl')
    if not os.path.isdir(PKL_DIR):
        raise FileNotFoundError('Directory \"{}\" does not exist! Please split CSV files'.\
                format(PKL_DIR))
    
    PKL_FILES = os.listdir(PKL_DIR)
    if not PKL_FILES:
        raise FileNotFoundError('Directory \"{}\" contains no pickle files! Please split CSV files'.\
                format(PKL_DIR))
    PKL_FILES = list(sorted(PKL_FILES))
    N_FILES = len(PKL_FILES)
    
    START_DATE = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
    DELTA = datetime.timedelta(weeks=1)

    date = START_DATE + DELTA
    tokens = defaultdict(float)
    main_df = pd.DataFrame()

    print('Calculating top token holders for \"{}\"...'.format(args.name))
    start = time()
    for i, file_ in enumerate(PKL_FILES):
        if args.verbose:
            print(' file {} out of {}'.format(i, N_FILES - 1), end='\r')

        fname = os.path.join(PKL_DIR, file_)
        f = open(fname, 'rb')
        gc.disable()
        df = pickle.load(f)
        gc.enable()
        f.close()

        z1 = zip(*df.to_dict('list').values())
        for address, value in z1:
            tokens[address] += value


        if args.keep_address:
            tokens = defaultdict(float, {k: v for k, v in sorted(tokens.items(), reverse=True, 
                key=lambda item: item[1]) if v})
            sorted_d_len = len(tokens)
        else:
            sorted_d = [t for t in tokens.values() if t]
            sorted_d.sort(reverse=True)
            sorted_d_len = len(sorted_d)

        cut = args.top if sorted_d_len >= args.top else sorted_d_len
        
        if not args.keep_address:
            df = pd.DataFrame({date.strftime('%Y-%m-%d'): sorted_d[:cut]})
        else:
            df = pd.DataFrame({date.strftime('%Y-%m-%d'): list(tokens.keys())[:cut]})
            df = pd.concat([df, pd.DataFrame({'': list(tokens.values())[:cut]})], axis=1)
        main_df = pd.concat([main_df, df], axis=1)
        # print(main_df)
        # exit()
        date += DELTA

    print(' ' * 50, end='\r')
    print('Calculating done! Saving data...')
    assert main_df.shape[1] == N_FILES if not args.keep_address else N_FILES / 2
    fname = os.path.join(DIR, 'top{}_token_holders'.format(args.top) + \
            '_addresses' * args.keep_address + '.csv')
    main_df.to_csv(fname)
    if args.verbose:
        print(main_df.iloc[:20, :])
    print('Elapsed time: {:.4f} s'.format(time() - start))
    print('Data saved in {}'.format(fname))


if __name__ == '__main__':
    main()
