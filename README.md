# Flavors-Storage

This program creates a report that summarizes the storage utilization per flavor, category, and month.

This is a sample generated:

|YEAR/MONTH|CATEGORY|0|32|33|34|301991|487041|
|---|---|---|---:|---:|---:|---:|---:|
|2024/01|Alpha||346112|68812|95641||
|2024/02|23549781_23549881|9582037||||108184|120998|

Notes:
* The numbers in the header are flavorParamsIDs
* If entries are published to more than one category, they will appear like this `23549781_23549881`
* If entries are published to only one category, the name of the category is listed, e.g. `Alpha`

## Running the program

Steps:
1. pip install KalturaApiClient (see https://developer.kaltura.com/api-docs/Client_Libraries)
2. Change `'admin secret'` to your admin secret from KMC
3. Change `'ron.raz@kaltura.com'` to your user ID
4. Change `1809631` to your partner ID
5. run `python flavors_storage.py`
6. The csv file `storage_per_flavor.csv` will be written
