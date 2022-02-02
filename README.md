# ERC20 token holders: data extraction and processing

The code in this repository is used to extract the data from ERC20 token transfers (until some end date) 
on the Ethereum blockchain. The data is publicly available on 
[Google BigQuery](https://bigquery.cloud.google.com/dataset/bigquery-public-data:crypto_ethereum).
The extracted data is then processed in order to obtain weekly data of the top ERC20 token holders.

## Data extraction

To extract the data for a given ERC20 token, please visit 
[Etherscan Token Tracker](https://etherscan.io/tokens), find your token of interest, copy its address 
and decimals and paste it into a query file called ````extract.sql````, which can be ran on the 
[Google BigQuery workspace](https://console.cloud.google.com/bigquery). Additionally, one might want 
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
For instructions, please refer to ````extract2csv.sql````.

## Data processing

Queried data must be thereafter processed in order to calculate weekly top token holders.

### Split CSVs to weekly data saved in pickle files

Use ````split_csv.py```` to split CSV files downloaded from GCS by weekly data saved into pickle files.
The choice of the pickle format over CSV is made to save storage space and speed up loading data.

Example usage:

```bash
python3.9 split_csv.py --dir="data" --name="SushiToken" --verbose
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
...
