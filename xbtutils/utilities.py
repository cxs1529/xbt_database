import os # creates output dir
import shutil
import json
from datetime import datetime
from .gear_info import GearClass

# fiscal year class
class FYClass:
    def __init__(self, fiscalYear = "1901",startDate="1900-10-01", endDate="1901-09-30"):
        self.fiscalYear = fiscalYear
        self.startDate = startDate
        self.endDate = endDate

# get start and end bit index for a given parameter and message type from csv list
# mType: 1 = MSG Type 1, 2 = MSG Type 2, 3 = MSG Type 3
def get_range(csvList,parameter,mType):
    if mType == 1:
        a = 1
        b = 2
    elif mType == 2:
        a = 3
        b = 4
    elif mType == 3:
        a = 5
        b = 6

    for line in csvList:
        if parameter in line:
            startBit = line[a]
            endBit = line[b]
            break
    return [int(startBit),int(endBit)]


# convert a binary stream into an ascii string, given start-end bit index
# removes NULL chars
def bits_to_ascii(bitStr,startBit,endBit):
    binaryChunk = bitStr[startBit:(endBit+1)] # extract needed binary chunk
    mydata = int(binaryChunk,2) # binary to integer
    mydata = hex(mydata)[2:] # convert to hexadecimal and remove leading '0x'
    try:
        mydata = bytes.fromhex(mydata) # creates a bytes object from a string of hexadecimal digits like b'DCUJ2\x00\x00\x00\x00'
        mydata = mydata.decode("ASCII") # decode bytes hex to ascii        
    except:
        mydata = "N/A"    
    mydata = mydata.replace('\x00', '') # remove NULL chars
    return mydata


# convert a binary stream into a decimal, given start-end bit index, scale factor and offset
# if last the last variable is used and =True, it'll print the binary number for debugging purpuses
# returns a float number
def bits_to_dec(bitStr,startBit,endBit,scale,offset, debugFlag = False):
    binaryChunk = bitStr[startBit:(endBit+1)] # extract needed binary chunk
    mydata = (int(binaryChunk,2) + offset)/scale
    if debugFlag == True:
        print(f"binaryChunk: {binaryChunk}, mydata: {mydata}, startBit: {startBit}, endBit: {endBit}")

    return mydata


# get temperature profile samples from bits string
# returns a list of temperatures based on number of samples and start bit
def get_profile_temperatures(bitStr, samples, startBit): 
    tempList = []
    for x in range(startBit,startBit+samples*12,12): # each sample is 12 bits
        thisTemp = bits_to_dec(bitStr,x,x+11,100,-400) # current temperature point
        tempList.append(round(thisTemp,2))

    return tempList


# Probe depth is based in time since water touchdown and probe hydrodynamic coefs A and B
# returns a list of depths based on gear object
def get_profile_depths(sampleCount, gearType):
    samplingFreq = gearType.recorder.frequency
    A = gearType.probe.coefA
    B = gearType.probe.coefB
    dList = []
    for n in range(0,sampleCount):
        time = (n+1)/samplingFreq
        depth = (A * time) + (0.001 * B * time * time)
        dList.append(round(depth,2))

    return dList


# export the binary as an ascii (text) file
# Converts an xbt class object into a text file, stored in outputDir
# Not used in project but can be used to directly export a binary to .txt file
# Use example: xbt = decode_binary(binfile) and then xbt_export_ascii(xbt, outputDir = "output")
def xbt_export_ascii(xbt, outputDir = "output"):
    # get ascii file name
    fname = xbt.fileName.split("/")[-1] # get only file name
    fname = fname.split(".")[0] # remove the .bin
    asciiFile = fname + '_ascii.txt'
    # create full path to output file
    asciiPath = os.path.join(outputDir, asciiFile)
    try:
        # create output directory if it doesn't exist
        os.makedirs(outputDir, exist_ok=True) 
        # open file to write
        print("> Creating ASCII:", asciiPath)
        with open(asciiPath, 'w') as fout:      
            print('--------------------------------------------------------------------------------------------------', file=fout)
            print('fileName     |', xbt.fileName, file=fout)
            print('CallSign     |', xbt.vessel.callSign, file=fout)
            print('IMO          |', xbt.vessel.imo, file=fout)
            print('ShipName     |', xbt.vessel.shipName, file=fout)
            print('Speed        |', xbt.vessel.shipSpeed, 'kt', file=fout)
            print('Direction    |', xbt.vessel.shipDirection, '°', file=fout)
            print('Date         |', xbt.profileDatetime.dtString, file=fout)
            print('Latitude     |', xbt.vessel.latitude,'°', file=fout)
            print('Longitude    |', xbt.vessel.longitude,'°', file=fout)
            print('Water Depth  |', xbt.vessel.totalWaterDepth, 'm', file=fout)
            print('Line         |', xbt.line.soopLine, file=fout)
            print('Transect No. |', xbt.line.transectNumber, file=fout)
            print('Sequence No. |', xbt.line.sequenceNumber, file=fout)
            print('Agency       |', xbt.agency.name,'(',xbt.agency.code,')', file=fout)
            print('MSGType      |', xbt.msgType, file=fout)
            print('SEAS version |', xbt.gear.seasVersion)
            print('Launcher     |', xbt.gear.launcher.name, '(', xbt.gear.launcher.code,')', file=fout)
            print('LaunchHeight |', xbt.vessel.launchHeight,'m', file=fout)
            print('Recorder     |', xbt.gear.recorder.name, '(', xbt.gear.recorder.code , ')', 'Frequency:', xbt.gear.recorder.frequency,'Hz', file=fout)
            print('Probe        |', xbt.gear.probe.name, '(', xbt.gear.probe.code,')', 'SN:', int(xbt.gear.probe.serial), 'Max Depth:', xbt.gear.probe.maxDepth, 'CoefA:', xbt.gear.probe.coefA, 'CoefB:', xbt.gear.probe.coefB, file=fout)
            print('Samples      |', xbt.profile.dataPoints, file=fout)
            print('Rider        |','Name:' ,xbt.rider.name, "|Email:",xbt.rider.email, "|Institution:", xbt.rider.institution, "|Phone:", xbt.rider.phone, file=fout)
            print('--------------------------------------------------------------------------------------------------', file=fout)
            # write depth vs temperatures
            print("D[m]","T[°C]", file=fout)
            for i in range(0, len(xbt.profile.temperatures)):
                print(xbt.profile.depths[i], xbt.profile.temperatures[i], file=fout)
            print("EOF", file=fout)
            # close file
            fout.close()
            print(f"> ASCII saved to {asciiPath} OK")
    except Exception as e:
        print(f"> WARNING: {asciiPath} could not be saved >>", e)
    finally:
        print("> End of ascii conversion")


# Converts an xbt class object into a json file, stored in outputDir
# Not used in project (only in database.py EXTRAS) but can be used to directly export a binary to .json file
# Use example: xbt = decode_binary(binfile) and then xbt_export_json(xbt, outputDir = "output")
def xbt_export_json(xbtdict, outputDir = "output"):
    # get file name
    fname = xbtdict["fileName"]
    fname = fname.split(".")[0] # remove the .bin
    jsonFile = fname + '.json'
    # create full path to output file
    jsonPath = os.path.join(outputDir, jsonFile)
    try:
        # create output directory if it doesn't exist
        os.makedirs(outputDir, exist_ok=True)  
        print("> Creating JSON: ", jsonPath)        
        with open(jsonPath,'w') as file:
            json.dump(xbtdict, file, indent=4)
        print(f"> Dictionary saved to {jsonFile} OK")
    except Exception as e:
        print(f"> WARNING: {jsonPath} could not be saved >>", e)
    finally:
        print("> End of json conversion")


# Prints a dictionary to console, limiting number of data samples printed
def print_dictionary(dict, sample_count = 20):
    for key in dict.keys():
        # do not print all the samples
        if key == "depths" or key == "temperatures":
            print(f"{key} : {dict[key][:sample_count]} ...")
        else:
            print(f"{key} : {dict[key]}")


# Prints a list of dictionaries to console, limiting number of data samples printed for each dictionary
def print_dictionary_list(dict_list, sample_count = 20):
    for i,dict in enumerate(dict_list):
        print("\r\n> Entry", i, ":")
        print("------------")
        print_dictionary(dict, sample_count)


# Export any text string to a file in outputDir with given fname
def export_text_to_file(text, outputDir, fname):
    print(f"> Exporting report to {outputDir}")
    filePath = os.path.join(outputDir, fname)
    try:
        # create output directory if it doesn't exist
        os.makedirs(outputDir, exist_ok=True) 
        with open(filePath, 'w') as fout:
            print(text, file=fout)
    except Exception as e:
        print(f"> WARNING: {fname} could not be saved >>", e)


# Get list of binary files in parentDir within a given date range
# input: parentDir - directory where to look for binary files
#        dateRange - list with 2 elements with start and end date ['YYYY-MM-DD','YYYY-MM-DD']
# output: list of binary files in the given date range
def list_dir_binaries_by_date(parentDir, dateRange):
    bin_list = []
    start_date = dateRange[0]
    end_date = dateRange[1]
    # get range of years between start and end date
    years = range( int(start_date.split("-")[0]), int(end_date.split("-")[0]) + 1 )
    print(years)
    # loop through year directories for a given date range
    for year in years:
        year_dir = os.path.join(parentDir, str(year))
        print("Looking into:", year_dir)
        if os.path.isdir(year_dir):
            for file in os.listdir(year_dir):
                if file.endswith(".bin"):
                    print("Found file:", file)
                    # check if file date is within the given date range based on file name
                    file_date_str = file.split("_")[-3] # date is in the third last position YYYYMMDD between "_"
                    file_date_formatted = f"{file_date_str[0:4]}-{file_date_str[4:6]}-{file_date_str[6:8]}"
                    print("File date:", file_date_formatted)
                    if (file_date_formatted >= start_date) and (file_date_formatted <= end_date):    
                        print("-> File within date range, adding to list")                   
                        bin_list.append(os.path.join(str(year), file))
    return bin_list


# List all files in a directory with a given extension
def list_dir_files(parentDir, extension = ".bin"):
    files = []
    if os.path.isdir(parentDir):
        for file in os.listdir(parentDir):
            if file.endswith(extension):
                files.append(file)
    else:
        print(f"> WARNING: {parentDir} is not a valid directory!")
        
    return files

# filter repeated profiles based on file name ID
# I.e. done_20250929-0030_WDH6745_20250929032500_N06_XBT >> ID is WDH6745_20250929032500_N06
# input: fileList - list of binary files to filter
# output: filteredList - list of unique binary files (without repeated IDs)
def filter_repeated_profiles(fileList):
    filteredList = []
    seenProfiles = set()
    repeatedCount = 0
    uniqueCount = 0
    for file in fileList:        
        profile_id = get_profile_id(file)
        # if ID is was not already processed then add binaryfile to filtered list
        if profile_id not in seenProfiles:
            print(f"> Adding profile: {file}")
            seenProfiles.add(profile_id)
            filteredList.append(file)
            uniqueCount += 1
        else:
            print(f"> Skipping repeated profile: {file}")
            repeatedCount += 1
    print(f"> Total repeated profiles skipped: {repeatedCount}")
    print(f"> Total unique profiles added: {uniqueCount}")

    return filteredList


# extract profile ID from file name
# input: fileName - binary file name
# output: profile_id - unique profile ID string
def get_profile_id(fileName):
    idString = fileName.split("_")
    profile_id = idString[2] + "_" + idString[3] + "_" + idString[4] + "_" + idString[5]  # callsign date time profile number
    
    return profile_id


# get current fiscal year info
# input: yearOffset - integer to add/subtract years from current fiscal year
def get_current_fy_range(yearOffset = 0):    
    fy = FYClass()

    now = datetime.now()
    # determine current fiscal year    
    if now.month >= 10:
        fy.fiscalYear = now.year + yearOffset + 1
        fy.startDate = f"{now.year + yearOffset}-10-01"
        fy.endDate = f"{now.year + yearOffset +1}-09-30"
    else:
        fy.fiscalYear = now.year + yearOffset
        fy.startDate = f"{now.year + yearOffset - 1}-10-01"
        fy.endDate = f"{now.year + yearOffset}-09-30"

    return fy


# get current timestamp as string "YYYY-MM-DD HH:MM:SS"
def get_current_timestamp():
    now = datetime.now()
    now_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    return now_timestamp


# calculate time difference between two timestamps in format "YYYY-MM-DD HH:MM:SS"
# returns a string with difference in minutes and seconds
def calculate_time_difference(start_timestamp, end_timestamp):
    fmt = "%Y-%m-%d %H:%M:%S"
    t1 = datetime.strptime(start_timestamp, fmt)
    t2 = datetime.strptime(end_timestamp, fmt)
    delta = t2 - t1
    s = delta.total_seconds()
    m = s/60.0
    str = "{:.2f} minutes ({:.2f} seconds)".format(m, s)
    return str


# copy and replace existing directory with file contents
# input: source_dir - directory to copy from
#        destination_dir - directory to copy to (will be replaced if existing)
def copy_directory_replacing_existing(source_dir, destination_dir):
    print(f"> Copying static files from {source_dir} to {destination_dir} ...")
    # check if css directory exists, if so remove it
    if os.path.exists(destination_dir):        
        shutil.rmtree(destination_dir) 
    # copy new css directory    
    shutil.copytree(source_dir, destination_dir)
    print("> Static files copied.\r\n")


# given a sample dictionary with frequency, coefA, coefB, dataPoints and temperatures (list)
# returns two lists: depths and temperatures
# Used to plot depth vs temperature profiles from sample dictionaries
def get_depth_temperature_pairs(sampleDict):
    gear = GearClass()

    dataPoints = sampleDict["dataPoints"]
    gear.probe.coefA = sampleDict["coefA"]
    gear.probe.coefB = sampleDict["coefB"]
    gear.recorder.frequency = sampleDict["frequency"]
    depths = get_profile_depths(dataPoints, gear)

    temperatures = [float(temp) for temp in sampleDict['temperatures'].split(',')]

    return depths, temperatures

