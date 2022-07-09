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

prev_sum = 0
prev_N = 0


def entropy(x):
    return -np.dot(x, np.log(x))


def gini(x, prev_sum=0, prev_N=0):
    # n = len(x)

    # method
    new = 2 * np.abs(np.tril(np.subtract.outer(x[prev_N:], x[prev_N:]))).sum()
    # cross = 2 * sum([np.abs(val - x[:prev_N]).sum() for val in x[prev_N:]])
    # print(mat)
    cross = 2 * np.abs(np.subtract.outer(x[prev_N:], x[:prev_N])).sum()
    # print('prev_sum', prev_sum, 'new', new, 'cross', cross)
    return prev_sum + new + cross

    # method
    # return 2 * np.abs(np.tril(np.subtract.outer(x, x))).sum()

    # method
    # s = 0
    # for i in range(len(x)):
        # s += np.abs(x[i] - x).sum()
    # return s

    # method
    # return sum([np.abs(val - x).sum() for val in x]) # very slow, O(n^2)

    # this one does not work
    # return np.array([i * x[i] - (n - 1 - i) * x[i] for i in range(n - 1, -1, -1)]).sum() / n


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
        '--name',
        type=str,
        required=True,
        help='Name of coin/token',
        )
required_args.add_argument(
        '--min_N',
        type=int,
        required=True,
        help='Minimum number of top addresses to consider',
        )
required_args.add_argument(
        '--max_N',
        type=int,
        required=True,
        help='Maximum number of top addresses to consider',
        )
required_args.add_argument(
        '--step_N',
        type=int,
        required=True,
        help='Step for the top addresses',
        )
required_args.add_argument(
        '--metric',
        type=str,
        choices=['entropy', 'gini', 'nakamoto', 'efficiency', 'robin'],
        required=True,
        help='Metric to plot. Available metrics: entropy, '
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


DIR = os.path.join(args.dir, args.name)
# fname = [x for x in os.listdir(DIR) if 'csv' in x and not 'addresses' in x and not
        # x.split('.')[0].isdigit()][0]
fname = args.name + '.csv'
df = pd.read_csv(os.path.join(DIR, fname), header=0, index_col=0)
df.drop(df.index[0], inplace=True)


Y = np.arange(args.min_N, args.max_N + args.step_N, args.step_N)
mat = []

FIRST_COL = None
for i, col in enumerate(df):
    if not df[col][:args.max_N].isnull().sum():
        FIRST_COL = col
        break
# print(df)
# print(df.loc[:, FIRST_COL:])
# print(FIRST_COL)
# # exit()
non_nan_df = df.loc[:, FIRST_COL:].copy()
# print(non_nan_df)

# some token addresses have zero or nagative balance, this may cause warning when computing entropy
# so we will replace 'bad' values with machine epsilon
for col in non_nan_df:
    non_nan_df.loc[np.isclose(non_nan_df[col], 0), col] = np.finfo(float).eps
# print(non_nan_df)

N_WEEKS = non_nan_df.shape[-1]
X = pd.to_datetime(non_nan_df.columns)
if args.verbose:
    print('Total number of weeks: {}'.format(df.shape[-1]))
    print('Number of weeks with more than {} addresses: {}'.format(args.max_N, N_WEEKS))
    print('Number of weeks to be dropped: {}'.format(df.shape[-1] - N_WEEKS))



start = time()
for i, col in enumerate(non_nan_df):
    if args.verbose:
        # print('Computing for N={} out of {}'.format(N, args.max_N))
        print('Computing for week {} out of {}'.format(i, N_WEEKS))
    y = []
    # top_N = np.array([])
    for N in Y:
        top_N = non_nan_df[col][:N].to_numpy()
        # top_N = np.append(top_N, np.arange(N-args.step_N+1, N+1, 1))
        # print(N, top_N)
        
        if args.metric == 'entropy':
            top_N = top_N / top_N.sum()
            assert np.isclose(top_N.sum(), 1)
            y.append(entropy(top_N))
        elif args.metric == 'gini':
            # top_N = np.array([1, 8, 9, 15, 16])
            # print(prev_sum / (2*(N-args.step_N)), end=' ')
            # top_N = top_N / top_N.sum()
            # assert np.isclose(top_N.sum(), 1)
            prev_sum = gini(top_N, prev_sum=prev_sum, prev_N=prev_N)
            prev_N = N
            y.append(prev_sum / (2 * N * top_N.sum()))
            # y.append(prev_sum)
            # print(y[-1])
            # print(prev_sum)
            # exit()
        elif args.metric == 'nakamoto':
            top_N = top_N / top_N.sum()
            assert np.isclose(top_N.sum(), 1)
            y.append(nakamoto(top_N))
        elif args.metric == 'efficiency':
            top_N = top_N / top_N.sum()
            assert np.isclose(top_N.sum(), 1)
            y.append(efficiency(top_N))
        elif args.metric == 'robin':
            top_N = top_N / top_N.sum()
            assert np.isclose(top_N.sum(), 1)
            y.append(robin(top_N))
        else:
            pass
        # exit()
    
    # if i == 5:
        # exit()
    mat.append(y)
    prev_sum = 0
    prev_N = 0
    # mat = np.array(mat).T
    # print(mat, np.array(mat).T.shape)
    # exit()
if args.verbose:
    print('Elapsed time: {} s'.format(time() - start))

mat = np.array(mat).T
x_lim = mdates.date2num([X[0], X[-1]])

if args.latex:
    plt.rcParams['font.size'] = 20
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rc('text', usetex=True)

fig, ax = plt.subplots(figsize=(8.636, 5.2)) # this width is twice larger for double-column IEEE articles

COLOR_MAP = mcol.LinearSegmentedColormap.from_list(
        name='custom_cmap',
        # colors=['#f5f0e1', '#ff6e40', '#ffc13b', '#1e3d69'],
        colors=['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00', '#FF7F00', '#FF0000'],
        )
COLOR_NORMALIZER = mcol.Normalize(
        vmin=mat.min().min(),  # red
        vmax=mat.max().max(),  # blue
        )
COLOR_PICKER = cm.ScalarMappable(
        norm=COLOR_NORMALIZER,
        cmap=COLOR_MAP,
        )
COLOR_PICKER.set_array([])

im = ax.imshow(
        X=np.flip(mat, axis=0),
        cmap=COLOR_MAP,
        # cmap=cm.get_cmap('hsv'),
        extent=(x_lim[0]+1, x_lim[-1], Y[0], Y[-1]),
        aspect='auto',
        # norm=mcol.LogNorm(),
        )

label = '{}'.format(args.metric.title())
if args.metric in ['gini', 'nakamoto']:
    label += ' coefficient'
elif args.metric == 'robin':
    label += ' Hood index'

fig.colorbar(
        im,
        ax=ax,
        label=label,
        )
# plt.hsv()

title = label + ' for {}'.format(args.name)
ax.set_title(title)

ax.xaxis_date()
ax.set_ylabel('Sample size ' + ('$N$' if args.latex else 'N'))


if args.ylog:
    plt.yscale('log')

# myFmt = mdates.DateFormatter('%Y')
# ax.xaxis.set_major_formatter(myFmt)

date_diff = mdates.num2date(ax.get_xticks()[:2])
# print(date_diff[1] - date_diff[0])
if date_diff[-1] - date_diff[0] < datetime.timedelta(days=28):
    ax.set_xlabel('Year{}Month{}Day'.format('$-$' if args.latex else '-', '$-$' if args.latex else '-'))
    plt.xticks(
            rotation=90,
            horizontalalignment='center',
            verticalalignment='top',
            )
elif date_diff[-1] - date_diff[0] < datetime.timedelta(days=365):
    ax.set_xlabel('Year{}Month'.format('$-$' if args.latex else '-'))
    plt.xticks(
            rotation=90,
            horizontalalignment='center',
            verticalalignment='top',
            )
else:
    ax.set_xlabel('Year')

plt.savefig(
        os.path.join(DIR, '{}_{}.pdf'.format(args.name, args.metric)),
        format='PDF',
        bbox_inches='tight',
        )
# plt.show()

new_df = pd.DataFrame({'N': Y})
for i, col in enumerate(non_nan_df):
    new_df = pd.concat([new_df, pd.DataFrame({col: mat[:, i]})], axis=1)

new_df.to_csv(os.path.join(DIR, '{}_{}.csv'.format(args.name, args.metric)))
