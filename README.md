# XBT MONITOR

## XBT binary decoder
Convert an XBT binary file to a text file, in either standard ASCII fromat ot JSON, with *export_ascii()* and *xbt_export_json()*, or just print a single binary to screen with *decode_binary()* followed by print_binary_header().

## XBT database builder
Read a directory containing xbt binaries and store the data into an sqlite database running *main.py*
The process is basically decode and add to database, using *decode_binary(filePath)* followied by *xbt_add_to_database(xbtdata, dbfile)*

## Query XBT database
Use *SQLite Data browser* to browser the xbt database or run any of the available functions for standard queries in the *database.py* library (see examples in *dbquery.py*):
- *read_database_profile(dbfile, "9V8584")*
- *read_database_date_range(dbfile, "2025-10-20", "2025-10-22")*
- *list_database_tables(dbfile)*
- *read_database_filtered(dbfile, callsign = "%", shipname = "%", soopline = "%", ridername = "%", date_start="2025-01-01", date_end="2025-01-15", export_json=False)*
- *database_summary(dbfile, start_date="2025-01-01", end_date="2025-03-01",outputDir="output", fname="myreport.txt", export=False)*

## XBT Monitor website
Run app.py to create an interactive map with all profiles stored in the database.
See example in https://cxs1529.github.io/xbt_database/web/

### XBT Monitor website main
![xbtmonitor_main](https://github.com/user-attachments/assets/484ad117-e9bf-47a2-afb2-47a7b3f1d561)


### XBT Monitor website map
![xbtmonitor_map](https://github.com/user-attachments/assets/1fd77af1-4a0d-407e-ab88-df4d5c0bd7fd)
