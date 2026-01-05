import sqlite3 as sql
from .utilities import print_dictionary_list, xbt_export_json, export_text_to_file, get_current_fy_range
import os


# adds an XBT object to the database
# creates database and tables if they don't exist
# xbt: XBT object
# dbfile: path to database file
def xbt_add_to_database(xbt, dbfile):
    print(f"> Adding {xbt.fileName} to {dbfile}...")
    # create database if doesn't exist
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    # Enable use of foreign keys to link tables
    dbc.execute("PRAGMA foreign_keys = ON")

    # CREATE MAIN TABLE
    # create main table and link to secondary tables with secondary keys
    CREATE_MAIN_TABLE = "CREATE TABLE IF NOT EXISTS main( " \
                        "fileName TEXT PRIMARY KEY, latitude FLOAT, longitude FLOAT, datetime TEXT, " \
                        "shipSpeed FLOAT, shipDirection INT, totalWaterDepth INT, launchHeight INT, probeSerial INT, " \
                        "soopLine TEXT, transectNumber INT, sequenceNumber INT, seasVersion INT, msgType INT," \
                        "callSign TEXT, agencyCode INT, launcherCode INT, probeCode INT, recorderCode INT, riderName TEXT, " \
                        "FOREIGN KEY(callSign) REFERENCES vessel(callSign), " \
                        "FOREIGN KEY(agencyCode) REFERENCES agency(code)," \
                        "FOREIGN KEY(launcherCode) REFERENCES launcher(code)" \
                        "FOREIGN KEY(probeCode) REFERENCES probe(code), " \
                        "FOREIGN KEY(recorderCode) REFERENCES recorder(code), " \
                        "FOREIGN KEY(riderName) REFERENCES rider(name) )"
    dbc.execute(CREATE_MAIN_TABLE)
    # CREATE SECONDARY TABLES
    # create vessel table
    CREATE_VESSEL_TABLE = "CREATE TABLE IF NOT EXISTS vessel (callSign TEXT PRIMARY KEY, IMO INT, shipName TEXT)"
    dbc.execute(CREATE_VESSEL_TABLE)
    # create agency table
    CREATE_AGENCY_TABLE = "CREATE TABLE IF NOT EXISTS agency (code INT PRIMARY KEY, name TEXT)"
    dbc.execute(CREATE_AGENCY_TABLE)
    # create launcher table
    CREATE_LAUNCHER_TABLE = "CREATE TABLE IF NOT EXISTS launcher (code INT PRIMARY KEY, name TEXT)"
    dbc.execute(CREATE_LAUNCHER_TABLE)
    # create probe table # self.code = code, self.coefA = coefA, self.coefB = coefB, self.maxDepth = maxDepth, self.name = name, self.serial = serial, depthProfile (based on probe type)
    CREATE_PROBE_TABLE = "CREATE TABLE IF NOT EXISTS probe (code INT PRIMARY KEY, name TEXT, coefA FLOAT, coefB FLOAT, maxDepth INT)"
    dbc.execute(CREATE_PROBE_TABLE)
    # create recorder table
    CREATE_RECORDER_TABLE = "CREATE TABLE IF NOT EXISTS recorder (code INT PRIMARY KEY, name TEXT, frequency INT)"
    dbc.execute(CREATE_RECORDER_TABLE)
    # create rider table
    CREATE_RIDER_TABLE = "CREATE TABLE IF NOT EXISTS rider (name TEXT PRIMARY KEY, email TEXT, phone TEXT, institution TEXT)"
    dbc.execute(CREATE_RIDER_TABLE)
    # create quality table
    CREATE_QUALITY_TABLE = "CREATE TABLE IF NOT EXISTS quality (code INT PRIMARY KEY, name TEXT)"
    dbc.execute(CREATE_QUALITY_TABLE)
    # create resolution table
    CREATE_RESOLUTION_TABLE = "CREATE TABLE IF NOT EXISTS resolution (code INT PRIMARY KEY, name TEXT)"
    dbc.execute(CREATE_RESOLUTION_TABLE)
    # create sample data table: qc, resolution and temperature (no depths, as can be calculated from probe coefA and coefB  and number of data points)
    CREATE_SAMPLES_TABLE = "CREATE TABLE IF NOT EXISTS samples (fileName TEXT PRIMARY KEY, dataPoints INT, resolutionCode INT, qualityCode INT, data TEXT,  " \
    "FOREIGN KEY(fileName) REFERENCES main(fileName), FOREIGN KEY(resolutionCode) REFERENCES resolution(code), FOREIGN KEY(qualityCode) REFERENCES quality(code) )"
    dbc.execute(CREATE_SAMPLES_TABLE)

    # INSERT VALUES >> order matters: if using a foreign reference in another table, these values need to be populated beforehand in the secondary table
    INSERT_TO_VESSEL_TABLE = "INSERT OR IGNORE INTO vessel VALUES(?,?,?)"    
    dbc.execute(INSERT_TO_VESSEL_TABLE, (xbt.vessel.callSign, xbt.vessel.imo, xbt.vessel.shipName))

    INSERT_TO_AGENCY_TABLE = "INSERT OR IGNORE INTO agency VALUES(?,?)"    
    dbc.execute(INSERT_TO_AGENCY_TABLE, (xbt.agency.code, xbt.agency.name))    
    
    INSERT_TO_LAUNCHER_TABLE = "INSERT OR IGNORE INTO launcher VALUES(?,?)"    
    dbc.execute(INSERT_TO_LAUNCHER_TABLE, (xbt.gear.launcher.code, xbt.gear.launcher.name))   
    
    INSERT_TO_PROBE_TABLE = "INSERT OR IGNORE INTO probe VALUES(?,?,?,?,?)"    
    dbc.execute(INSERT_TO_PROBE_TABLE, (xbt.gear.probe.code, xbt.gear.probe.name, xbt.gear.probe.coefA, xbt.gear.probe.coefB, xbt.gear.probe.maxDepth))  

    INSERT_TO_RECORDER_TABLE = "INSERT OR IGNORE INTO recorder VALUES(?,?,?)"    
    dbc.execute(INSERT_TO_RECORDER_TABLE, (xbt.gear.recorder.code, xbt.gear.recorder.name, xbt.gear.recorder.frequency))   

    INSERT_TO_RIDER_TABLE = "INSERT OR IGNORE INTO rider VALUES(?,?,?,?)"    
    dbc.execute(INSERT_TO_RIDER_TABLE, (xbt.rider.name, xbt.rider.email, xbt.rider.phone, xbt.rider.institution)) 

    INSERT_TO_QUALITY_TABLE = "INSERT OR IGNORE INTO quality VALUES(?,?)"
    dbc.execute(INSERT_TO_QUALITY_TABLE, (xbt.quality.dataQuality.code, xbt.quality.dataQuality.name))

    INSERT_TO_RESOLUTION_TABLE = "INSERT OR IGNORE INTO resolution VALUES(?,?)"
    dbc.execute(INSERT_TO_RESOLUTION_TABLE, (xbt.quality.dataResolution.code, xbt.quality.dataResolution.name))

    # main has foreign keys that need to be populated in the origin tables before inserting the references into main
    INSERT_TO_MAIN_TABLE = "INSERT OR IGNORE INTO main VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" # 20 entries    
    dbc.execute(INSERT_TO_MAIN_TABLE, (xbt.fileName, xbt.vessel.latitude, xbt.vessel.longitude, xbt.profileDatetime.dtString,
                                       xbt.vessel.shipSpeed, xbt.vessel.shipDirection, xbt.vessel.totalWaterDepth, xbt.vessel.launchHeight,
                                       xbt.gear.probe.serial, xbt.line.soopLine, xbt.line.transectNumber, xbt.line.sequenceNumber,
                                       xbt.gear.seasVersion, xbt.msgType,
                                       xbt.vessel.callSign, xbt.agency.code, xbt.gear.launcher.code, xbt.gear.probe.code, 
                                       xbt.gear.recorder.code, xbt.rider.name) ) 

    # # option 1: new table with one item per row >>  10 items, 1204 kB db
    # CREATE_SAMPLES_TABLE_1 = "CREATE TABLE IF NOT EXISTS samples (depth FLOAT, temperature FLOAT, fileName TEXT, FOREIGN KEY(fileName) REFERENCES main(fileName))"
    # INSERT_TO_SAMPLES_TABLE_1 = "INSERT OR IGNORE INTO samples VALUES(?,?,?)"
    # dbc.execute(CREATE_SAMPLES_TABLE_1)
    # # insert values to table one row at a time
    # for i in range(len(xbt.profile.temperatures)):
    #     dbc.execute(INSERT_TO_SAMPLES_TABLE, (xbt.profile.depths[i], xbt.profile.temperatures[i], xbt.fileName))

    # option 2: new table with json row with data >> 10 items, 268 kB | 7575 profiles (2024/2025) = 169.8 MB
    # CAUTIN: NEEDS import json AT TOP OF FILE
    # samples = { "depth": xbt.profile.depths, "temperature": xbt.profile.temperatures }
    # samples_str = json.dumps(samples) # convert back to list later using json.loads(json_samples) 
    # option 3: table with json and only temperatures >> 7575 profiles (2024/2025) = 81.9 MB
    # t_samples = { "temperature": xbt.profile.temperatures }
    # samples_str = json.dumps(t_samples) # convert back to list later using json.loads(json_samples) 
    # option 4: list of temperatures only string >> 7575 profiles (2024/2025) = 66.9 MB
    separator = ","
    samples_str = separator.join(map(str, xbt.profile.temperatures)) # store only temperatures as list string
    # samples has a foreign key (filename) that needs to be populated before inserting new values in samples
    INSERT_TO_SAMPLES_TABLE = "INSERT OR IGNORE INTO samples VALUES(?,?,?,?,?)"    
    dbc.execute(INSERT_TO_SAMPLES_TABLE, (xbt.fileName, xbt.profile.dataPoints, xbt.quality.dataResolution.code, xbt.quality.dataQuality.code, samples_str))

    # save changes to database and close
    conn.commit()
    conn.close()



# read all tables and columns from the data base, specifying a limit and date range for use to create JSON files (used in website with xbt_html.py)
# returns list of dictionaries with all database info for each profile:
# fileName,latitude,longitude,datetime,shipSpeed,shipDirection,totalWaterDepth,launchHeight,probeSerial,
# soopLine,transectNumber,sequenceNumber,seasVersion,agencyName,shipName,callSign,IMO,launcherName,
# riderInstitution,riderName,riderEmail,riderPhone,riderInstitution,probeName,coefA,coefB,maxDepth,
# recorderName,recorderFrequency,dataPoints,temperatures
def read_database_all_by_date_range(dbfile, limit=15000, dateStart="1900-01-01", dateEnd="2100-01-01"):
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    COMMAND = """
        SELECT main.fileName, main.latitude, main.longitude, main.datetime, main.shipSpeed, main.shipDirection, main.totalWaterDepth, main.launchHeight, 
            main.probeSerial, main.soopLine, main.transectNumber, main.sequenceNumber, main.seasVersion, agency.name AS agencyName, 
            vessel.shipName, vessel.callSign, vessel.IMO, launcher.name AS launcherName, rider.institution AS riderInstitution,
            rider.name AS riderName, rider.email AS riderEmail, rider.phone AS riderPhone, rider.institution AS riderInstitution,
            probe.name AS probeName, probe.coefA, probe.coefB, probe.maxDepth, recorder.name AS recorderName, recorder.frequency AS recorderFrequency,
            samples.dataPoints, samples.data AS temperatures
        FROM main
        JOIN agency ON main.agencyCode = agency.code
        JOIN vessel ON main.callSign = vessel.callSign
        JOIN rider ON main.riderName = rider.name
        JOIN probe ON main.probeCode = probe.code
        JOIN recorder ON main.recorderCode = recorder.code
        JOIN launcher ON main.launcherCode = launcher.code
        JOIN samples ON main.fileName = samples.fileName
        WHERE main.datetime >= ? AND main.datetime <= ?
        ORDER BY main.datetime DESC
        LIMIT ? """

    res = dbc.execute(COMMAND, (dateStart, dateEnd, limit))    
    # convert query to dictionary
    dictionary_list = query_to_dict(res)
    print("> All database for JSON read: from {dateStart} to{dateEnd}\r\n")    
    conn.close()

    return dictionary_list



# reads database profile information by date range and returns list of dictionaries. 
# Used to create profile plots and list profiles in profiles page (xbt_html.py)
# fileName, soopLine, datetime, probe coefA, probe coefB, recorder frequency, dataPoints, data (temp list string)
def read_database_profiles_by_date_range(dbfile, limit=15000, dateStart="1900-01-01", dateEnd="2100-01-01", show=False):
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    COMMAND = """
        SELECT main.fileName, main.soopLine, main.latitude, main.longitude, main.datetime, probe.coefA, probe.coefB, recorder.frequency, samples.dataPoints, samples.data AS temperatures
        FROM main
        JOIN probe ON main.probeCode = probe.code
        JOIN recorder ON main.recorderCode = recorder.code
        JOIN samples ON main.fileName = samples.fileName
        WHERE main.datetime >= ? AND main.datetime <= ?
        ORDER BY main.datetime DESC
        LIMIT ? """
    try:
        res = dbc.execute(COMMAND, (dateStart, dateEnd, limit))
        # returns list of profiles with values: fileName, soopLine, datetime, probe coefA, probe coefB, recorder frequency, dataPoints, data (temp list string)
        dictionary_list = query_to_dict(res) 

        # print profile info if show=true
        if show:
            for i,xbtdict in enumerate(dictionary_list):
                if i < limit:
                    print(f"> {i}: {xbtdict['fileName']} | {xbtdict['soopLine']} | {xbtdict['latitude']},{xbtdict['longitude']} | {xbtdict['datetime']} | coefA: {xbtdict['coefA']} | coefB: {xbtdict['coefB']} | freq: {xbtdict['frequency']} | dataPoints: {xbtdict['dataPoints']}")
                    print(f" Temperatures (top-20): {xbtdict['temperatures'].split(',')[:20]}\r\n")
                else:
                    break
    except Exception as e:
        print("> ERROR: database query could not be done! >>", e)

    conn.close()

    return dictionary_list


# Report A: detailed summary by soopline, callsign, month and vessel
# Used to create fiscal year reports in website home page (xbt_html.py)
def database_fy_summary_A(dbfile, yearOffset = 0 ,show = True, outputDir = "output", fname = "fyreport.txt", export = False):
    # get FY info
    fy = get_current_fy_range(yearOffset)
    print(f"> XBT DATABASE FY {fy.fiscalYear} SUMMARY A: dates {fy.startDate} : {fy.endDate}")
    # open DB connection
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    COMMAND = """
    SELECT main.soopLine,strftime('%Y-%m', main.datetime) AS yearMonth,main.callSign,vessel.shipName,main.riderName, rider.institution,COUNT(main.fileName) AS profiles, strftime('%Y-%m-%d', MIN(main.datetime)) AS dateStart, strftime('%Y-%m-%d', MAX(main.datetime)) as dateEnd
    FROM main
    JOIN vessel ON main.callSign = vessel.callSign
	JOIN rider ON main.riderName = rider.name
    WHERE main.datetime BETWEEN ? AND ?
    GROUP BY main.soopLine,yearMonth,main.callSign,main.transectNumber 
    ORDER BY main.soopLine,yearMonth ASC """

    try:
        res = dbc.execute(COMMAND, (fy.startDate, fy.endDate))
        dictionary_list = query_to_dict(res)    
        columns = list(dictionary_list[0].keys())
        TEXT = ""
        for i,col in enumerate(columns):
            if i == (len(columns) - 1):
                # print(col, end = '\r\n')
                TEXT = TEXT + str(col) + "\n"
            else:
                # print(col, end = ',')
                TEXT = TEXT + str(col) + ","
        
        for dictionary in dictionary_list:
            for j,col in enumerate(columns):
                if j == (len(columns) - 1):
                    # print(dictionary[col], end='\r\n')
                    TEXT = TEXT + str(dictionary[col]) + "\n"
                else:
                    # print(dictionary[col], end=',')
                    TEXT = TEXT + str(dictionary[col]) + ","
        # display report on screen
        if show == True:
            print(TEXT)
            print("\r\n")
        print("> Report A: all read") 
    except Exception as e:
        print("> ERROR: database query could not be done! >>", e)
        TEXT = f"WARNING: No results found for the date range specified: {fy.startDate} : {fy.endDate}"

    if export == True:
        export_text_to_file(TEXT, outputDir, fname)

    conn.close()

    return TEXT


# Report B: summary by callsign and vessel
# Used to create fiscal year reports in website home page (xbt_html.py)
def database_fy_summary_B(dbfile, yearOffset = 0 ,show = True, outputDir = "output", fname = "fyreport.txt", export = False):
    # get FY info
    fy = get_current_fy_range(yearOffset)
    print(f"> XBT DATABASE FY {fy.fiscalYear} SUMMARY B: dates {fy.startDate} : {fy.endDate}")
    # open DB connection
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    COMMAND = """
    SELECT main.callSign,vessel.shipName,main.soopLine, COUNT(main.fileName) AS profiles
    FROM main
    JOIN vessel ON main.callSign = vessel.callSign
    WHERE main.datetime BETWEEN ? AND ?
    GROUP BY main.callSign
    ORDER BY main.callSign ASC """

    try:
        res = dbc.execute(COMMAND, (fy.startDate, fy.endDate))
        dictionary_list = query_to_dict(res)    
        columns = list(dictionary_list[0].keys())
        TEXT = ""
        for i,col in enumerate(columns):
            if i == (len(columns) - 1):
                # print(col, end = '\r\n')
                TEXT = TEXT + str(col) + "\n"
            else:
                # print(col, end = ',')
                TEXT = TEXT + str(col) + ","
        
        for dictionary in dictionary_list:
            for j,col in enumerate(columns):
                if j == (len(columns) - 1):
                    # print(dictionary[col], end='\r\n')
                    TEXT = TEXT + str(dictionary[col]) + "\n"
                else:
                    # print(dictionary[col], end=',')
                    TEXT = TEXT + str(dictionary[col]) + ","
        # display report on screen
        if show == True:
            print(TEXT)
            print("\r\n")
        print("> Report B: all read")  
    except Exception as e:
        print("> ERROR: database query could not be done! >>", e)
        TEXT = f"WARNING: No results found for the date range specified: {fy.startDate} : {fy.endDate}"

    if export == True:
        export_text_to_file(TEXT, outputDir, fname)

    conn.close()

    return TEXT


# Report C: summary by soopline
# Used to create fiscal year reports in website home page (xbt_html.py)
def database_fy_summary_C(dbfile, yearOffset = 0 ,show = True, outputDir = "output", fname = "fyreport.txt", export = False):
    # get FY info
    fy = get_current_fy_range(yearOffset)
    print(f"> XBT DATABASE FY {fy.fiscalYear} SUMMARY C: dates {fy.startDate} : {fy.endDate}")
    # open DB connection
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    COMMAND = """
    SELECT main.soopLine, strftime('%Y-%m', main.datetime) AS yearMonth, COUNT(main.fileName) AS profiles
    FROM main
    WHERE main.datetime BETWEEN ? AND ?
    GROUP BY main.soopLine, yearMonth
    ORDER BY main.soopLine ASC """

    try:
        res = dbc.execute(COMMAND, (fy.startDate, fy.endDate))
        dictionary_list = query_to_dict(res)    
        columns = list(dictionary_list[0].keys())
        TEXT = ""
        for i,col in enumerate(columns):
            if i == (len(columns) - 1):
                # print(col, end = '\r\n')
                TEXT = TEXT + str(col) + "\n"
            else:
                # print(col, end = ',')
                TEXT = TEXT + str(col) + ","
        
        for dictionary in dictionary_list:
            for j,col in enumerate(columns):
                if j == (len(columns) - 1):
                    # print(dictionary[col], end='\r\n')
                    TEXT = TEXT + str(dictionary[col]) + "\n"
                else:
                    # print(dictionary[col], end=',')
                    TEXT = TEXT + str(dictionary[col]) + ","
        # display report on screen
        if show == True:
            print(TEXT)
            print("\r\n")
        print("> Report C: all read") 
    except Exception as e:
        print("> ERROR: database query could not be done! >>", e)
        TEXT = f"WARNING: No results found for the date range specified: {fy.startDate} : {fy.endDate}"

    if export == True:
        export_text_to_file(TEXT, outputDir, fname)

    conn.close()

    return TEXT


# converts an sqlite select response to a dictionary
# res: sqlite3 response object after executing a select command
# returns list of dictionaries containing column names and values
def query_to_dict(res):
    dictionary_list = []
    # get column names
    colNames = []
    for col in res.description:
        colNames.append(col[0])   
    # get values from each row
    for row in res:        
        xbtdict = {}
        for j,value in enumerate(row):
            xbtdict[colNames[j]] = value
        dictionary_list.append(xbtdict)
    
    return dictionary_list


# reads database and retrieves data to create map, optionally limit number of points to plot
# returns list of dictionaries with: soopLine, transectNumber, callSign, shipName, latitude, longitude, datetime, fileName, institutionName, agencyName
# used in xbt_html.py to create map plots
def read_database_map_info(dbfile, limit=10000, dateStart="1900-01-01", dateEnd="2100-01-01"):
    conn = sql.connect(dbfile)
    dbc = conn.cursor()
 
    COMMAND = """
        SELECT main.soopLine,main.transectNumber,main.callSign,vessel.shipName,main.latitude,main.longitude,main.datetime,main.fileName,rider.institution AS institutionName,agency.name AS agencyName
        FROM main
		JOIN agency ON main.agencyCode = agency.code
		JOIN rider ON main.riderName = rider.name
		JOIN vessel ON main.callSign = vessel.callSign
		WHERE main.datetime BETWEEN ? AND ?
        ORDER BY main.soopLine,main.datetime,main.callSign ASC
        LIMIT ? """
    res = dbc.execute(COMMAND, (dateStart, dateEnd, limit, ))
   
    # convert query to dictionary
    dictionary_list = query_to_dict(res)

    print(f"> Found {len(dictionary_list)} profiles to plot (<={limit})")       
    conn.close()

    return dictionary_list


# returns list of binary files already stored/processed in database
# dbfile: path to database file
def list_files_in_database(dbfile):
    dbFiles = []
    # check if database exists
    if os.path.isfile(dbfile):
        print(f"> Database {dbfile} found!")
        # connect to db and query files already there
        conn = sql.connect(dbfile)
        dbc = conn.cursor()
        COMMAND = "SELECT main.fileName from main"
        res = dbc.execute(COMMAND)   
        # create list of files already in db           
        for f in res:
            dbFiles.append(f[0])
        conn.close()
        print(f"> {len(dbFiles)} files already stored in database")
    else:
        print(f"> WARNING: database {dbfile} not found!")

    return dbFiles


# Make database report of profiles by soopline for last 2 fiscal years for plotting stats
# used in xbt_html.py to create stats plots
# returns list of dictionaries with: soopLine, callSign, date, profiles
# yearOffset: offset to current fiscal year (0=current FY, -1=previous FY, etc)
def stats_by_soopline_2fy(dbfile, yearOffset = 0, show = False):
    # get FY info for last 2 fiscal years
    fy_current = get_current_fy_range(yearOffset)
    fy_prev = get_current_fy_range(yearOffset - 1)
    print(f"> XBT DATABASE STATS SUMMARY BY SOOPLINE: dates {fy_prev.startDate} : {fy_current.endDate}")
    # open DB connection
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    COMMAND = """
    SELECT main.soopLine, main.callSign, strftime('%Y-%m-%d', main.datetime) AS date, COUNT(main.fileName) AS profiles
    FROM main
    WHERE main.datetime BETWEEN ? AND ?
    GROUP BY main.soopLine, main.callSign, date
    ORDER BY main.soopLine ASC """

    try:
        res = dbc.execute(COMMAND, (fy_prev.startDate, fy_current.endDate))
        dictionary_list = query_to_dict(res)  
        if show == True:
            print(dictionary_list)
            print("\r\n")  
        
    except Exception as e:
        print("> ERROR: database query could not be done! >>", e)

    conn.close()

    return dictionary_list


# Make database report of profiles by map temperature for last 2 fiscal years for plotting stats
# used in xbt_html.py to create stats plots
# returns list of dictionaries with: latitude, longitude, data (temperature list string)
# yearOffset: offset to current fiscal year (0=current FY, -1=previous FY, etc)
def stats_by_map_temperature(dbfile, yearOffset = 0, show = False):
    # get FY info for last 2 fiscal years
    fy_current = get_current_fy_range(yearOffset)
    fy_prev = get_current_fy_range(yearOffset - 1)
    print(f"> XBT DATABASE STATS SUMMARY BY MAP TEMPERATURE: dates {fy_prev.startDate} : {fy_current.endDate}")
    # open DB connection
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    COMMAND = """
    SELECT main.latitude, main.longitude, samples.data
    FROM main
    JOIN samples ON main.fileName = samples.fileName
    WHERE main.datetime BETWEEN ? AND ? """

    try:
        res = dbc.execute(COMMAND, (fy_prev.startDate, fy_current.endDate))
        dictionary_list = query_to_dict(res)  
        if show == True:
            print(dictionary_list)
            print("\r\n")  
        
    except Exception as e:
        print("> ERROR: database query could not be done! >>", e)

    conn.close()

    return dictionary_list

# Make database report of profiles by agency for last 2 fiscal years for plotting stats
# used in xbt_html.py to create stats plots
# returns list of dictionaries with: soopLine, agencyName, date, profiles
# yearOffset: offset to current fiscal year (0=current FY, -1=previous FY, etc)
def stats_by_agency(dbfile, yearOffset = 0, show = False):
    # get FY info for last 2 fiscal years
    fy_current = get_current_fy_range(yearOffset)
    fy_prev = get_current_fy_range(yearOffset - 1)
    print(f"> XBT DATABASE STATS SUMMARY BY MAP TEMPERATURE: dates {fy_prev.startDate} : {fy_current.endDate}")
    # open DB connection
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    COMMAND = """
    SELECT main.soopLine, agency.name AS agencyName, strftime('%Y-%m-%d', main.datetime) AS date, COUNT(main.fileName) AS profiles
    FROM main
    JOIN agency ON main.agencyCode = agency.code
    WHERE main.datetime BETWEEN ? AND ?
    GROUP BY date
    ORDER BY date ASC """

    try:
        res = dbc.execute(COMMAND, (fy_prev.startDate, fy_current.endDate))
        dictionary_list = query_to_dict(res)  
        if show == True:
            print(dictionary_list)
            print("\r\n")  
        
    except Exception as e:
        print("> ERROR: database query could not be done! >>", e)

    conn.close()

    return dictionary_list   






############################## EXTRAS NOT USED IN PROJECT ##############################

# lists all tables and columns in the database without printing the data
def list_database_tables(dbfile):
    print("\r\n> Listing tables and columns...\r\n")
    conn = sql.connect(dbfile)
    dbc = conn.cursor() 
    # get tables in database
    res = dbc.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")

    tables = [row[0] for row in res.fetchall()]    
    # list columns in each table
    for table in tables:        
        table_res = dbc.execute(f"SELECT * FROM {table}")
        columns = []
        for col in table_res.description:
            columns.append(col[0])
        print("> Table:",table, ", Columns:",columns)
    
    conn.close()


# reads all tables and columns from the data base, specifying number of entries to print    
def read_database_all(dbfile, limit=15000):
    conn = sql.connect(dbfile)
    dbc = conn.cursor()
    res = dbc.execute(f"SELECT * FROM main " \
                        "JOIN vessel ON main.callSign = vessel.callSign " \
                        "JOIN agency ON main.agencyCode = agency.code " \
                        "JOIN launcher ON main.launcherCode = launcher.code " \
                        "JOIN probe ON main.probeCode = probe.code " \
                        "JOIN recorder ON main.recorderCode = recorder.code " \
                        "JOIN rider on main.riderName = rider.name " \
                        "JOIN samples on main.fileName = samples.fileName " \
                        "LIMIT ?", (limit,))
    
    print(f"\r\n> Printing {limit} entries:\r\n")    
    # convert query to dictionary
    dictionary_list = query_to_dict(res)
    
    print_dictionary_list(dictionary_list)

    print("> All read\r\n")    
    conn.close()


# read database filtering by date range only
# date_start: string "YYYY-MM-DD"
# date_end: string "YYYY-MM-DD"
def read_database_date_range(dbfile, date_start, date_end):
    conn = sql.connect(dbfile)
    dbc = conn.cursor()
    res = dbc.execute("SELECT main.fileName,main.datetime,main.callSign,main.latitude,main.longitude,main.soopLine FROM main WHERE main.datetime >= ? AND main.datetime <= ?", (date_start, date_end))   

    print(f"> Printing by date: between {date_start} and {date_end}")
    # convert query to dictionary
    dictionary_list = query_to_dict(res)    
    # print dictionaries:
    print_dictionary_list(dictionary_list)

    print("> All read: from {date_start} to {date_end}\r\n")
    conn.close()



# creates JSON files from database dictionary list
# dict_list: list of dictionaries read from database
# creates json files in current directory
def database_to_json(dict_list):
    for i,xbtdict in enumerate(dict_list):
        try:
            print(f"> {i}: exporting {xbtdict["fileName"]} to json...")
            # add db_ to indicate it was read from the database and not directy exported from binary file
            xbtdict["fileName"] = "db_" + xbtdict["fileName"]
            xbt_export_json(xbtdict)
        except:
            print("> ERROR: json file could not be saved!")
    print("> Json exports finished\r\n")


# The most complete filter. Read database filtering by callsign, shipname, soop line, rider, dates and optionally export a json file for each entry
# Use wildcard '%' for incomplete strings i.e. 'A%' filters all variable values starting in 'A'
def read_database_filtered(dbfile, callsign = "%", shipname = "%", soopline = "%", ridername = "%", date_start="1900-01-01", date_end="2100-01-01", response_limit = 10000, export_json = False):
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    COMMAND = """SELECT
	main.callSign,vessel.IMO,vessel.shipName,main.shipSpeed,main.shipDirection,main.launchHeight,main.latitude,main.longitude,main.totalWaterDepth,
	main.launcherCode,launcher.name as launcherName,main.probeCode,probe.name as probeName,probe.coefA as probeCoefA,probe.coefB as probeCoefB,probe.maxDepth as probeMaxDepth,
	main.recorderCode,recorder.name as recorderName, recorder.frequency as recorderFreq,main.seasVersion,main.soopLine,main.transectNumber,main.sequenceNumber,
    main.agencyCode,agency.name as agencyName,main.riderName,rider.email as riderEmail,rider.phone as riderPhone,rider.institution as riderInstitution,
	main.msgType,main.fileName,main.datetime,samples.dataPoints,samples.data
    FROM main 
    JOIN vessel ON main.callSign = vessel.callSign
    JOIN rider ON main.riderName = rider.name
    JOIN agency ON main.agencyCode = agency.code
    JOIN launcher ON main.launcherCode = launcher.code
    JOIN probe ON main.probeCode = probe.code
    JOIN recorder ON main.recorderCode = recorder.code
    JOIN samples ON main.fileName = samples.fileName
    WHERE main.soopLine LIKE ? AND vessel.shipName LIKE ? AND main.callSign LIKE ? AND main.riderName LIKE ?
    AND main.datetime BETWEEN ? AND ? 
    LIMIT ?"""

    try:
        res = dbc.execute(COMMAND, (soopline, shipname, callsign, ridername, date_start, date_end, response_limit))
        
        print(f"> Printing selection: date {date_start} - {date_end} | soopline {soopline} | shipname {shipname} | callsign {callsign} | rider {ridername} | up to {response_limit} entries...\r\n")
        # convert query to dictionary
        dictionary_list = query_to_dict(res)    
        # print dictionaries:
        print_dictionary_list(dictionary_list)
        # Export query to json files
        if export_json == True:
            database_to_json(dictionary_list)
    except Exception as e:
        print("> ERROR: database query could not be done! >>", e)
        
    conn.close()



# reads database and generates a grouped report by soopline, callsign and year-month
# returns report as CSV string
# Report format: soopLine, year_month, callSign, shipName, riderName, transectNumber, profiles, date_start, date_end
# Can export report to text file if export=True
def database_summary(dbfile, start_date = "1900-01-01", end_date = "2100-01-01", show = True, outputDir = "output", fname = "report.txt", export = False):
    print("> XBT DATABASE SUMMARY: dates {start_date} : {end_date}\r\n")
    conn = sql.connect(dbfile)
    dbc = conn.cursor()

    COMMAND = """
        SELECT main.soopLine,strftime('%Y-%m', main.datetime) AS year_month,main.callSign,vessel.shipName,main.riderName,main.transectNumber,COUNT(main.fileName) AS profiles,MIN(main.datetime) AS date_start,MAX(main.datetime) as date_end
        FROM main
        JOIN vessel ON main.callSign = vessel.callSign
        WHERE main.datetime BETWEEN ? AND ?
        GROUP BY main.soopLine,year_month,main.callSign,main.transectNumber 
        ORDER BY main.soopLine,year_month ASC """
    try:
        res = dbc.execute(COMMAND, (start_date, end_date))
        dictionary_list = query_to_dict(res)    
        columns = list(dictionary_list[0].keys())
        TEXT = ""
        for i,col in enumerate(columns):
            if i == (len(columns) - 1):
                # print(col, end = '\r\n')
                TEXT = TEXT + str(col) + "\n"
            else:
                # print(col, end = ',')
                TEXT = TEXT + str(col) + ","
        
        for dictionary in dictionary_list:
            for j,col in enumerate(columns):
                if j == (len(columns) - 1):
                    # print(dictionary[col], end='\r\n')
                    TEXT = TEXT + str(dictionary[col]) + "\n"
                else:
                    # print(dictionary[col], end=',')
                    TEXT = TEXT + str(dictionary[col]) + ","
        # display report on screen
        if show == True:
            print(TEXT)
            print("\r\n")
        print("> All read\r\n") 
    except Exception as e:
        print("> ERROR: database query could not be done! >>", e)
        TEXT = f"WARNING: No results found for the date range specified: {start_date} : {end_date}"

    if export == True:
        export_text_to_file(TEXT, outputDir, fname)

    conn.close()

    return TEXT


# returns list of new binary files to process (not in database yet)
# dbfile: path to database file
# inputDir: path to directory with binary files
def get_files_to_process(dbfile, inputDir):
    new_files = []
    if os.path.isdir(inputDir) == True:
        # list files in directory
        fileList = os.listdir(inputDir)
        if os.path.isfile(dbfile):
            print(f"> Database {dbfile} found!")
            # connect to db and query files already there
            conn = sql.connect(dbfile)
            dbc = conn.cursor()
            COMMAND = "SELECT main.fileName from main"
            res = dbc.execute(COMMAND)
            # list files already in db    
            files_processed = []
            for f in res:
                files_processed.append(f[0])
            print(f"> {len(files_processed)} files already stored in database")
            # add files not in db to new list
            for file in fileList:
                if file not in files_processed:
                    new_files.append(file)
            print(f"> {len(new_files)} new files not stored in database")
        else:
            print(f"> {dbfile} database NOT found!")
            print(f"> All files in {inputDir} will be processed")
            return fileList
    else:
        print("> WARNING: directory does not exist!")
    
    return new_files


# reads database and prints profile information, limited by number of profiles and date range
# used for debugging purposes and not in project
def read_database_profiles(dbfile, limit=10000, dateStart="1900-01-01", dateEnd="2100-01-01"):
    conn = sql.connect(dbfile)
    dbc = conn.cursor()
    COMMAND = """
        SELECT main.fileName, samples.dataPoints, samples.data 
        FROM main JOIN samples ON main.fileName = samples.fileName 
        WHERE main.datetime BETWEEN ? AND ?
        LIMIT ? """
    res = dbc.execute(COMMAND, (dateStart, dateEnd, limit, ))

    print(f"\r\n> Printing {limit} profiles:\r\n")    
    for row in res:
        fileName = row[0]
        dataPoints = row[1]
        data_str = row[2]
        # convert string back to list of temperatures
        separator = ","
        temperatures = list( map(float, data_str.split(separator)) )
        print(f"> File: {fileName} | Data points: {dataPoints} | Top-10 temperatures: {temperatures[:10]}")

    print("> All read\r\n")    
    conn.close()