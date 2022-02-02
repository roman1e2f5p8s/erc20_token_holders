-- This query can be used to extract the data (until END_DATE exclusively) from ERC20 token transfers,
-- and save the results to CSV files on Google Cloud Storage (GCS).
-- As an example, here we extract data for SushiToken
-- https://etherscan.io/token/0x6b3595068778dd592e39a122f4f5a5cf09c90fe2
--
-- Author:  Roman Overko
-- Contact: roman.overko@iota.org
-- Date:    February 02, 2022

#standardSQL

DECLARE TARGET_TOKEN_ADDRESS STRING;
DECLARE DECIMALS INT64;
DECLARE END_DATE DATE;

-- Set address and decimals (both can be found on Etherscan), and the end date of token transfers for
-- the token of interest
SET TARGET_TOKEN_ADDRESS = "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2";
SET DECIMALS = 18;
SET END_DATE = DATE("2022-01-17"); --exclusively

EXPORT DATA OPTIONS(
    uri='gs://my_bucket/my_folder/*.csv', -- make sure to change the path to your bucket and folder
    format='CSV',
    overwrite=TRUE,
    header=TRUE,
    field_delimiter=',') AS
SELECT FORMAT_DATE("%Y-%m-%d", tt.block_timestamp) AS date, tt.to_address AS address, SAFE_CAST(tt.value AS FLOAT64)/POWER(10, DECIMALS) AS value
FROM `bigquery-public-data.crypto_ethereum.token_transfers` AS tt
WHERE tt.to_address IS NOT NULL AND SAFE_CAST(tt.value AS FLOAT64) > 0 AND tt.token_address = TARGET_TOKEN_ADDRESS AND DATE(tt.block_timestamp) < END_DATE
UNION ALL
SELECT FORMAT_DATE("%Y-%m-%d", tt.block_timestamp) AS date, tt.from_address AS address, -SAFE_CAST(tt.value AS FLOAT64)/POWER(10, DECIMALS) AS value
FROM `bigquery-public-data.crypto_ethereum.token_transfers` AS tt
WHERE tt.from_address IS NOT NULL AND safe_cast(tt.value as float64) > 0 AND tt.token_address = TARGET_TOKEN_ADDRESS AND DATE(tt.block_timestamp) < END_DATE
ORDER BY date ASC
