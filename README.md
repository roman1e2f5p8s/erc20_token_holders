# ERC20 token holders: data extraction and processing

The code in this repository is used to extract the data from ERC20 token transfers on the Ethereum 
blockchain. The data is publicly available on 
[Google BigQuery](https://bigquery.cloud.google.com/dataset/bigquery-public-data:crypto_ethereum).
The extracted data is then processed in order to obtain top ERC20 token holders for a given date.

## Data extraction

To extract the data for a given ERC20 token, please visit 
[Etherscan Token Tracker](https://etherscan.io/tokens), find your token of interest, copy its address 
and decimals and paste it into a query file called ````extract.sql````, which can be ran on 
Google BigQuery platform. For example, for 
[SushiToken](https://etherscan.io/token/0x6b3595068778dd592e39a122f4f5a5cf09c90fe2), the query returns 
the following results (note that only the first five rows are presented here):

| date       | address                                    | value              |
| ---------- | ------------------------------------------ | ------------------ |
| 2020-08-28 | 0xc2edad668740f1aa35e4d8f227fb8e17dca888cd | 500.0              |
| 2020-08-28 | 0x8468c6efa8ca7ffccb2c31d112e5e9331a469867 | 316.6713034408554  |
| 2020-08-28 | 0x3ab5c2ac327c3044776a2c229cb9c16ba9dcdbee | 124.00870068571557 |
| 2020-08-28 | 0xf942dba4159cb61f8ad88ca4a83f5204e8f4a6bd | 42.857142857142854 |
| 2020-08-28 | 0xc2edad668740f1aa35e4d8f227fb8e17dca888cd | 1285.7142857142858 |
