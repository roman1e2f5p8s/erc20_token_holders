import os
import argparse
import datetime
import pandas as pd
from pprint import pprint
from itertools import cycle
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50)
parser = argparse.ArgumentParser(
        description='Time evolution of top (at the last date) N addresses',
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
        '--N',
        type=int,
        required=True,
        help='Number of addresses to consider',
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
args = parser.parse_args()


DIR = os.path.join(args.dir, args.name)
ASSETS_TYPE = 'tokens' if 'tokens' in DIR else 'coins'
fname = [x for x in os.listdir(DIR) if 'addresses' in x][0]
df = pd.read_csv(os.path.join(DIR, fname), header=0)

#print(df.iloc[:N, -2:])
#print()

addresses = pd.Series(df.iloc[:args.N, -2:-1].iloc[:, -1]).to_list()
colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange', 'lime', 'olive']
markers = ['o', '+', 'x', 's', 'd', 'v', '8', 'p', '*', '1']
while len(colors) < len(addresses):
    colors += colors
    markers += markers
colors = colors[:len(addresses)]
markers = markers[:len(addresses)]

ac = dict(zip(addresses, colors))
am = dict(zip(addresses, markers))
# pprint(addresses)
#print()

data = {}
fig, ax = plt.subplots(figsize=(18, 10))


for c in range(int(df.shape[-1] / 2)):
    left = -2 - 2*c
    right = -1 - 2*c
    date = df.iloc[:args.N, left:right].columns[0]
    d = {}
    for a in addresses:
        try:
            i = df.iloc[:args.N, left:right].loc[df.iloc[:args.N,
                left:right].iloc[:, -1] == a].index[0]
            v = df.iloc[:args.N, right:right+1 if right < -1 else df.shape[-1]].iloc[:, -1].iloc[i]
            d[a] = v
            plt.plot([int(df.shape[-1] / 2) - c], [v], color=ac[a], label=a if not c else None,
                    marker=am[a], markersize=8)
        except IndexError:
            pass
    data[date] = d
print(date)
date = datetime.datetime.strptime(date, '%Y-%m-%d')

for a in addresses:
    x = []
    y = []
    for i, k in enumerate(sorted(data.keys())):
        try:
            y.append(data[k][a])
            x.append(i+1)
            # x.append(date + datetime.timedelta(weeks=i+1))
            # x.append(datetime.datetime.strptime(k, '%Y-%m-%d'))
        except KeyError:
            # print(x, i+1)
            if x:
                plt.plot(x, y, linestyle='-', linewidth=3, color=ac[a])
                x = []
                y = []
            else:
                pass
    # x = [date + datetime.timedelta(weeks=w) for w in x]
    # print(x)
    plt.plot(x, y, linestyle='-', linewidth=3, color=ac[a])

plt.title('Time evolution of top (at the last date) {} {} balances'.format(args.N, args.name),
        fontsize=16, fontweight='bold')

print((date + datetime.timedelta(weeks=170)).strftime('%Y-%m-%d'))
xticks = [date + datetime.timedelta(weeks=x) for x in ax.get_xticks()]
# ax.set_xticklables(xticks)
# plt.xticks(ticks=ax.get_xticks(), labels=xticks)
# ax.xaxis_date()
# myFmt = mdates.DateFormatter('%Y')
# ax.xaxis.set_major_formatter(myFmt)
date_diff = mdates.num2date(ax.get_xticks()[:2])
print(date_diff[1] - date_diff[0])
if date_diff[-1] - date_diff[0] < datetime.timedelta(days=28):
    ax.set_xlabel('Year-Month-Day')
    plt.xticks(
            rotation=90,
            horizontalalignment='center',
            verticalalignment='top',
            )
elif date_diff[-1] - date_diff[0] < datetime.timedelta(days=365):
    ax.set_xlabel('Year-Month')
    plt.xticks(
            rotation=90,
            horizontalalignment='center',
            verticalalignment='top',
            )
else:
    ax.set_xlabel('Year')

plt.xlabel('Weeks since deployment', fontsize=16)
plt.ylabel('Ammount of {}'.format(ASSETS_TYPE), fontsize=16)

plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
# plt.ylabel('Ammount of coins')
plt.legend()
# plt.show()
plt.savefig(os.path.join('evolution', '{}.pdf'.format(args.name)))
# pprint(data)
print('Done!')
