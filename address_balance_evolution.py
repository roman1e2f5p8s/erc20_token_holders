import pandas as pd
from pprint import pprint
from collections import defaultdict
import matplotlib.pyplot as plt


path = 'data/SushiToken/SushiToken_top10000_token_holders_addresses.csv'
df = pd.read_csv(path, header=0)
N = 10

print(df.iloc[:N, -2:])
print()

addresses = pd.Series(df.iloc[:N, -2:-1].iloc[:, -1]).to_list()
colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange', 'lime', 'olive']
markers = ['o', '+', 'x', 's', 'd', 'v', '8', 'p', '*', '1']
ac = dict(zip(addresses, colors))
am = dict(zip(addresses, markers))
# pprint(addresses)
print()

data = {}


for c in range(int(df.shape[-1] / 2)):
    left = -2 - 2*c
    right = -1 - 2*c
    date = df.iloc[:N, left:right].columns[0]
    d = {}
    for a in addresses:
        try:
            i = df.iloc[:N, left:right].loc[df.iloc[:N, left:right].iloc[:, -1] == a].index[0]
            v = df.iloc[:N, right:right+1 if right < -1 else df.shape[-1]].iloc[:, -1].iloc[i]
            d[a] = v
            plt.plot([int(df.shape[-1] / 2) - c], [v], color=ac[a], label=a if not c else None,
                    marker=am[a])
        except IndexError:
            pass
    data[date] = d

for a in addresses:
    x = []
    y = []
    for i, k in enumerate(sorted(data.keys())):
        try:
            y.append(data[k][a])
            x.append(i+1)
        except KeyError:
            pass
    plt.plot(x, y, linestyle='-', color=ac[a])

plt.title('Time evolution of balances of top {} SushiToken holders (at the last date)'.format(N))
plt.xlabel('Weeks since the deployment')
plt.ylabel('Ammount of tokens')
plt.legend()
plt.show()
pprint(data)
