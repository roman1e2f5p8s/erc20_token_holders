import os
import argparse


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

# optimal arguments
optional_args = parser.add_argument_group('optional arguments')
optional_args.add_argument(
        '-h',
        '--help',
        action='help',
        help='show this help message and exit',
        )

args = parser.parse_args()

DIR = os.path.join(args.dir)
METRICS = ['entropy', 'gini', 'nakamoto', 'efficiency', 'robin']
# METRICS = METRICS[-2:]


names = [n for n in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, n)) and not 'zcash' in n]
tokens_dir = [d for d in names if 'tokens' in d][0]
names.remove(tokens_dir)
names.sort()

cmd  = 'python3.9 metric.py --min_N=10 --max_N=10000 --step_N=10 --dir=\'{}\' --latex --ylog '.format(DIR)

for name in names:
    print('\nComputing for {}:'.format(name))
    for metric in METRICS:
        print('\t{}'.format(metric.title()))
        os.system(cmd + '--name=\'{}\' --metric=\'{}\''.format(name, metric))
exit()


# for tokens
DIR = os.path.join(DIR, tokens_dir)

names = [n for n in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, n)) and not 'scam' in n]
names.sort()

cmd  = 'python3.9 metric.py --min_N=10 --max_N=10000 --step_N=10 --dir=\'{}\' --latex --ylog '.format(DIR)

for name in names:
    print('\nComputing for {}:'.format(name))
    for metric in METRICS:
        print('\t{}'.format(metric.title()))
        os.system(cmd + '--name=\'{}\' --metric=\'{}\''.format(name, metric))
