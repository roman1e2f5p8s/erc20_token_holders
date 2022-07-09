import os
import shutil
import argparse


def args():
    optional_args = argparse.ArgumentParser()


def main():
    formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50)
    parser = argparse.ArgumentParser(
            description='Copy CSV files of ERC-20 token transfers from Google Cloud Storage',
            add_help=False,
            formatter_class=formatter,
            )
    
    # required arguments
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument(
            '--name',
            type=str,
            required=True,
            help='Name of ERC20 token (also the name of directory for that token)',
            )
    required_args.add_argument(
            '--to_dir',
            type=str,
            required=True,
            help='Path to parent directory where the data shall be copied',
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

    cmd = 'gsutil -m cp -n -r \"gs://blockchain_historical_data/erc20_tokens/{}/*\" \"{}\"'.format(
            args.name, os.path.join(args.to_dir, args.name))
    os.system(cmd)

    if os.path.isdir(os.path.join(args.to_dir, args.name, 'new')):
        last_csv = list(sorted([f for f in os.listdir(os.path.join(args.to_dir, args.name)) \
                if 'csv' in f and f.split('.')[0].isnumeric()]))[-1].split('.')[0]
        num_zeros = len(last_csv)
        last_csv_num = int(last_csv)

        for i, csv in enumerate(sorted(os.listdir(os.path.join(args.to_dir, args.name, 'new')))):
            print(csv, str(int(last_csv) + i + 1).zfill(num_zeros) + '.csv')
            old = os.path.join(args.to_dir, args.name, 'new', csv)
            new = os.path.join(args.to_dir, args.name, 'new', 
                    str(int(last_csv) + i + 1).zfill(num_zeros) + '.csv')
            os.rename(old, new)

        cmd = 'gsutil -m cp -n -r \"{}\" \"gs://blockchain_historical_data/erc20_tokens/{}\"'.format(
                os.path.join(args.to_dir, args.name, 'new', '*'), args.name)
        os.system(cmd)

        shutil.copytree(
                os.path.join(args.to_dir, args.name, 'new'),
                os.path.join(args.to_dir, args.name),
                copy_function=shutil.move,
                dirs_exist_ok=True,
                )
        shutil.rmtree(os.path.join(args.to_dir, args.name, 'new'))
        
        cmd = 'gsutil -m rm -r \"gs://blockchain_historical_data/erc20_tokens/{}/new\"'.format(
                args.name)
        os.system(cmd)

if __name__ == '__main__':
    main()
