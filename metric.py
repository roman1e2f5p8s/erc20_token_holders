#!/usr/bin/env python3.9

import os
import argparse
import datetime
import pandas as pd
import numpy as np
from pprint import pprint
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.colors as mcol
import matplotlib.dates as mdates
import matplotlib.cm as cm
from time import time


def entropy(x):
    return -np.dot(x, np.log(x))


def gini(x):
    # s = 0
    # for i in range(len(x)):
        # s += np.abs(x[i] - x).sum()
    # return s / (2 * len(x))
    return np.abs(np.tril(np.subtract.outer(x, x))).sum() / len(x)


def nakamoto(x):
    half = 0.5 * x.sum()
    s = 0
    for i in range(1, len(x) + 1):
        s += x[i-1]
        if s > half:
            return i


def efficiency(x):
    return entropy(x) / np.log(len(x))


def robin(x):
    return 0.5 * np.abs(x - 1 / len(x)).sum()


formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50)
parser = argparse.ArgumentParser(
        description='Calcualte and plot some metric based on the top N addresses',
        add_help=False,
        formatter_class=formatter,
        )

# required arguments
required_args = parser.add_argument_group('required arguments')
required_args.add_argument(
        '--dir',
        type=str,
        required=True,
        help='Path to parent directory with coins/tokens data',
        )
required_args.add_argument(
        '--metric',
        type=str,
        choices=['entropy', 'gini', 'nakamoto', 'efficiency', 'robin'],
        required=True,
        help='Metric to plot. Available metrics: entropy, '
        )
required_args.add_argument(
        '--N',
        type=int,
        required=True,
        help='Top N token holders to consider',
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
        '--latex',
        action='store_true',
        default=False,
        help='Use LaTeX font on figures, defaults to False'
        )
optional_args.add_argument(
        '--ylog',
        action='store_true',
        default=False,
        help='Use log scale on y-axis, defaults to False'
        )
args = parser.parse_args()

LABELS = {
        'ChainLink Token': 'LINK',
        'Dai Stablecoin': 'DAI',
        'Matic Token': 'MATIC',
        'stETH': 'stETH',
        'Tether USD': 'USDT',
        'Theta Token': 'THETA',
        'Uniswap (UNI)': 'UNI',
        'USD Coin': 'USDC',
        'Wrapped Bitcoin (WBTC)': 'WBTC'
        }

if args.latex:
    plt.rcParams['font.size'] = 20
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rc('text', usetex=True)

fig, ax = plt.subplots(figsize=(8.636, 5.2)) # this width is twice larger for double-column IEEE articles

token_csvs = [f for f in os.listdir(args.dir) if 'csv' in f]
for token_csv in token_csvs:
    # if token_csv in ['Theta Token.csv', 'stETH.csv']:
        # continue

    df = pd.read_csv(os.path.join(args.dir, token_csv), header=0, index_col=0)
    df.drop(df.index[0], inplace=True)

    FIRST_COL = None
    for i, col in enumerate(df):
        if not df[col][:args.top].isnull().sum():
            FIRST_COL = col
            break
    non_nan_df = df.loc[:, FIRST_COL:].copy()

    name = token_csv.split('.')[0]
    print('First {} weeks dropped for \"{}\"'.format(df.shape[-1] - non_nan_df.shape[-1], name))

    X = pd.to_datetime(non_nan_df.columns)
    Y = []

    for i, col in enumerate(non_nan_df):
        # some token addresses have zero or nagative balance, this may cause warning when 
        # computing entropy so we will replace 'bad' values with machine epsilon
        non_nan_df.loc[np.isclose(non_nan_df[col], 0), col] = np.finfo(float).eps

        top_N = non_nan_df[col][:args.N].to_numpy()
        top_N = top_N / top_N.sum()
        assert np.isclose(top_N.sum(), 1)
        
        if args.metric == 'entropy':
            Y.append(entropy(top_N))
        elif args.metric == 'gini':
            Y.append(gini(top_N))
        elif args.metric == 'nakamoto':
            Y.append(nakamoto(top_N))
        elif args.metric == 'efficiency':
            Y.append(efficiency(top_N))
        elif args.metric == 'robin':
            Y.append(robin(top_N))
        else:
            pass
    
    plt.plot(X, Y, linewidth=3, label=LABELS[name])

ax.set_title('Sample size {}N = {}{}'.format('$' if args.latex else '', args.N,
    '$' if args.latex else ''))

ax.xaxis_date()
ax.set_xlabel('Year')

if args.ylog:
    plt.yscale('log')
y_label = '{}'.format(args.metric.title())
if args.metric in ['gini', 'nakamoto']:
    y_label += ' coefficient'
elif args.metric == 'robin':
    y_label += ' Hood index'
ax.set_ylabel(y_label)

plt.legend(labelspacing=0.1, fontsize='small')

plt.savefig(
        os.path.join(args.dir, 'tokens_{}_N={}.pdf'.format(args.metric, args.N)),
        format='PDF',
        bbox_inches='tight',
        )
