-- This query can be used to extract the data from ERC20 token transfers.
-- As an example, here we extract data for SushiToken
-- https://etherscan.io/token/0x6b3595068778dd592e39a122f4f5a5cf09c90fe2
--
-- Author:  Roman Overko
-- Contact: roman.overko@iota.org
-- Date:    December 14, 2021

#standardSQL

declare TARGET_TOKEN_ADDRESS string;
declare DECIMALS int64;

-- In the next two lines, set address and decimals (both can be found on Etherscan) of token of interest
set TARGET_TOKEN_ADDRESS = "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2";
set DECIMALS = 18;

select format_date("%Y-%m-%d", tt.block_timestamp) as date, tt.to_address as address, safe_cast(tt.value as float64)/power(10, DECIMALS) as value
from `bigquery-public-data.crypto_ethereum.token_transfers` as tt
where tt.to_address is not null and safe_cast(tt.value as float64) > 0 and tt.token_address = TARGET_TOKEN_ADDRESS
union all
select format_date("%Y-%m-%d", tt.block_timestamp) as date, tt.from_address as address, -safe_cast(tt.value as float64)/power(10, DECIMALS) as value
from `bigquery-public-data.crypto_ethereum.token_transfers` as tt
where tt.from_address is not null and safe_cast(tt.value as float64) > 0 and tt.token_address = TARGET_TOKEN_ADDRESS
order by date asc
