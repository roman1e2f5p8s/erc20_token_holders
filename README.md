# ERC20 token holders: data extraction and processing

The code in this repository is used to extract the data from ERC20 token transfers (until some end date) 
on the Ethereum blockchain. The data is publicly available on 
[Google BigQuery](https://bigquery.cloud.google.com/dataset/bigquery-public-data:crypto_ethereum).
The extracted data is then processed in order to obtain weekly data of the top ERC20 token holders.

## Implementation

The coding language of this project is ````Python 3.9````. Queries are written in the ````SQL```` 
programming language.

## Getting Started
Please follow these instructions to install all the requirements and use the scripts correctly.

### Requirements and Installation
**Make sure you have installed:**
1. [Python 3.9](https://www.python.org/downloads/release/python-390/)

**Download the code:**
```bash
git clone https://github.com/roman1e2f5p8s/erc20_token_holders
```

**Create a virtual environment ```venv```:**
```bash
python3.9 -m venv venv
```

**Activate the virtual environment:**
- On Unix or MacOS:
```bash
source venv/bin/activate
```
- On Windows:
```bash
venv\Scripts\activate.bat
```

**Install the dependencies:**
```bash
pip3.9 install -r requirements.txt
```

## Data extraction

To extract the data for a given ERC20 token, please visit 
[Etherscan Token Tracker](https://etherscan.io/tokens), find your token of interest, copy its address 
and decimals and paste it into a query file called 
[extract.sql](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/extract.sql), 
which can be ran on the 
[Google BigQuery workspace](https://console.cloud.google.com/bigquery). Additionally, one may want 
to change the end date until which the token transfers need to be scanned (exclusively).
For example, for 
[SushiToken](https://etherscan.io/token/0x6b3595068778dd592e39a122f4f5a5cf09c90fe2), the query returns 
the following results (note that only the first five rows are presented here):

| date       | address                                    | value              |
| ---------- | ------------------------------------------ | ------------------ |
| 2020-08-28 | 0xf942dba4159cb61f8ad88ca4a83f5204e8f4a6bd | 14.285714285714286 |
| 2020-08-28 | 0x7047ceaff999ef495c08ee4de4c423a0b8b79143 | 248.72829907238406 |
| 2020-08-28 | 0xc2edad668740f1aa35e4d8f227fb8e17dca888cd | 357.14285714285717 |
| 2020-08-28 | 0xf942dba4159cb61f8ad88ca4a83f5204e8f4a6bd | 92.85714285714286  |
| 2020-08-28 | 0xce84867c3c02b05dc570d0135103d3fb9cc19433 | 100.77547966308072 |

Query results can also be directly exported to CSV files saved on Google Cloud Storage (GCS). 
For instructions, please refer to 
[extract2csv.sql](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/extract2csv.sql)

The queried data in the form of CSV files for other ERC20 tokens is publicly available in 
[this bucket on GCS](https://console.cloud.google.com/storage/browser/blockchain_historical_data).

## Data processing

Queried data must thereafter be processed in order to calculate weekly top token holders.
Two Python scripts are used for data processing: 
[split_csv.py](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/split_csv.py) and 
[calc_top_holders.py](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/calc_top_holders.py).

### Step 1: split CSV files to weekly data saved in pickle files

Use [split_csv.py](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/split_csv.py) 
to split CSV files downloaded from GCS by weekly data saved into pickle files.
The choice of the pickle format over CSV is made to save storage space and speed up data loading.

Example usage: assuming CSV files for SushiToken (can be downloaded from 
[Google Drive](https://drive.google.com/drive/folders/1oWilo-ss1yRWieO4BZ-RvzhyP3Yk94Vt?usp=sharing) 
or directly extracted using the ````extract2csv.sql```` script) are stored in ````./data/SushiToken/````:

```bash
python3.9 split_csv.py --dir="data" --name="SushiToken" --verbose
```

The script [split_csv.py](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/split_csv.py) 
also outputs the start date to be used later in the 
[calc_top_holders.py](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/calc_top_holders.py) script. The start date is date such that a week ahead will be the 
first date for which top token holders 
will be calculated. For example, for SushiToken, 
[split_csv.py](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/split_csv.py) 
will output:

```
Use "2020-08-30" as start_date for calc_top_holders.py
```

See help files for more details:

```bash
python3.9 split_csv.py --help
```

```
usage: split_csv.py --dir DIR --name NAME [-h] [--rm] [--end_date END_DATE] [--verbose]

Converts and splits CSV files (downloaded from GCS) to weekly data saved in pickle files

required arguments:
  --dir DIR            Path to parent directory with ERC20 tokens data
  --name NAME          Name of ERC20 token (also the name of the folder with CSV files)

optional arguments:
  -h, --help           show this help message and exit
  --rm                 Remove CSV files after converting, defaults to False
  --end_date END_DATE  End date to consider, defaults to 2022-01-16
  --verbose            Print detailed output to console, defaults to False
```

### Step 2: calculate weekly top token holders

Use 
[calc_top_holders.py](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/calc_top_holders.py) to calculates top token holders from pickle files split by weeks.

Example usage: assuming pickle files for SushiToken are stored in ````./data/SushiToken/````, and the 
start date (returned by [split_csv.py](https://github.com/roman1e2f5p8s/erc20_token_holders/blob/main/split_csv.py)) is ````2020-08-30````:

```bash
python3.9 calc_top_holders.py --dir="data" --name="SushiToken" --start_date="2020-08-30" --verbose
```

This will generate a CSV file (saved in ````./data/SushiToken/````) with weekly top 10000 token holders.
For example, top five token holders for the first three dates are given in the table below:


| 2020-09-06       | 2020-09-13       | 2020-09-20       |
|------------------|------------------|------------------|
| 18072441.3513119 | 27532694.6284704 | 23938749.5570045 |
| 13043658.1154027 | 20915794.7423454 | 21790196.6130313 |
| 8373307.01764695 | 17856981.1038341 | 19176827.2701975 |
| 4054865.94452714 | 15678351.5597793 | 14086290.9598478 |
| 2879805.90997324 | 5008829.76889882 | 11038584.1500118 |


See help files for more details:

```bash
python3.9 calc_top_holders.py --help
```

```
usage: calc_top_holders.py --dir DIR --name NAME --start_date START_DATE [-h] [--top TOP]
                           [--rm] [--end_date END_DATE] [--verbose]

Calculates top token holders from pickle files splitted by weeks

required arguments:
  --dir DIR                Path to parent directory with ERC20 tokens data
  --name NAME              Name of ERC20 token (also the name of the folder with pickle files)
  --start_date START_DATE  Start date to consider (this date is printed by split_csv.py)

optional arguments:
  -h, --help               show this help message and exit
  --top TOP                How many top holders to consider, defaults to 10000
  --rm                     Remove pickle files after calculating, defaults to False
  --end_date END_DATE      End date to consider, defaults to 2022-01-16
  --verbose                Print detailed output to console, defaults to False
```
