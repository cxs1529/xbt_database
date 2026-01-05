# XBT MONITOR

## XBT binary decoder
Convert an XBT binary file to a text file, in either standard ASCII fromat ot JSON, with *export_ascii()* and *xbt_export_json()*, or just print a single binary to screen with *decode_binary()* followed by print_binary_header().

## XBT database builder
Read a directory containing xbt binaries and store the data into an sqlite database running *make_db.py*.
The process decodes binary file directories and adds these to a database, using *decode_binary(filePath)* followed by *xbt_add_to_database(xbtdata, dbfile)*

## Query XBT database
Use *SQLite Data browser* to browser the xbt database or run any of the available functions for standard queries in the *database.py* library (see examples in *dbquery.py*):
- *read_database_profile(dbfile, "9V8584")*
- *read_database_date_range(dbfile, "2025-10-20", "2025-10-22")*
- *list_database_tables(dbfile)*
- *read_database_filtered(dbfile, callsign = "%", shipname = "%", soopline = "%", ridername = "%", date_start="2025-01-01", date_end="2025-01-15", export_json=False)*
- *database_summary(dbfile, start_date="2025-01-01", end_date="2025-03-01",outputDir="output", fname="myreport.txt", export=False)*

## XBT Monitor website
Run *make_web.py* to create an interactive map with all profiles stored in the database.
See example in https://cxs1529.github.io/xbt_database/website/


### XBT Monitor website Home
<img width="1901" height="915" alt="image" src="https://github.com/user-attachments/assets/d0cec187-57c1-4a4c-bd13-e1e7a543829e" />


### XBT Monitor website Stats
<img width="1405" height="832" alt="image (1)" src="https://github.com/user-attachments/assets/04654487-1512-4f2d-ad2a-086b31d13742" />
<img width="1212" height="624" alt="image (2)" src="https://github.com/user-attachments/assets/242854c7-a7dc-4262-a3ce-9a39ca33df24" />
<img width="1380" height="670" alt="image (3)" src="https://github.com/user-attachments/assets/0862cb6f-6906-41d2-b2c6-ef9ab4b3d7a1" />
<img width="1114" height="641" alt="image (4)" src="https://github.com/user-attachments/assets/74fcd190-5bbf-44f7-9425-cb53ab352855" />


### XBT Monitor website map
<img width="1911" height="902" alt="image (5)" src="https://github.com/user-attachments/assets/5ac4f171-e1f3-4248-a18f-fbe4f3dd44ba" />

Access JSON (text in json format) and PNG (plots) via links.
<img width="848" height="526" alt="image (6)" src="https://github.com/user-attachments/assets/17463e93-ada5-41c7-a1ee-fd3f016d3e0f" />


### XBT Monitor website Profiles
<img width="1901" height="660" alt="Capture" src="https://github.com/user-attachments/assets/16f59ffe-b928-4f6d-b6c0-86f87329f435" />




