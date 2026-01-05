from datetime import datetime
from .utilities import *

class LineClass:
    def __init__(self, soopLine=-99, transectNumber=-99, sequenceNumber=-99):
        self.soopLine = soopLine
        self.transectNumber = transectNumber
        self.sequenceNumber = sequenceNumber

class ProfileClass:
    def __init__(self, dataPoints=-99, depths=[], temperatures=[]):    
        self.dataPoints = dataPoints
        self.depths = depths
        self.temperatures = temperatures

class ProfileDatetimeClass:
    def __init__(self, dtObject=-99, dtString="na"):    
        self.dtObject = dtObject
        self.dtString = dtString



def get_sample_datetime(StringOfBits, csvList, newMessageType):
    # DATE & TIME
    dtprofile = ProfileDatetimeClass()
    try:
        # YEAR
        [a,b] = get_range(csvList, "YEAR", newMessageType)
        year = int(bits_to_dec(StringOfBits,a,b,1,0))
        # MONTH
        [a,b] = get_range(csvList, "MONTH", newMessageType)
        month = int(bits_to_dec(StringOfBits,a,b,1,0))
        # DAY
        [a,b] = get_range(csvList, "DAY", newMessageType)
        day = int(bits_to_dec(StringOfBits,a,b,1,0))
        # HOUR
        [a,b] = get_range(csvList, "HOUR", newMessageType)
        hour = int(bits_to_dec(StringOfBits,a,b,1,0))
        # MINUTE
        [a,b] = get_range(csvList, "MINUTE", newMessageType)
        minute = int(bits_to_dec(StringOfBits,a,b,1,0))       
    except:
        year, month, day, hour, minute = [1900,1,1,0,0]                                                      

    dtprofile.dtObject = datetime(year, month, day, hour, minute, 0) # keep to use in calculations
    # another option is to use epoch time for storage efficiency and calculations
    dtprofile.dtString = dtprofile.dtObject.strftime("%Y-%m-%d %H:%M:%S")
    # print("> dt: ", year, month, day, hour, minute, " >>> ", dtprofile.dtString)

    return dtprofile


def get_line(StringOfBits, csvList, newMessageType):
    line = LineClass()
    try:
        # SOOP_LINE
        [a,b] = get_range(csvList, "SOOP_LINE", newMessageType)
        line.soopLine = bits_to_ascii(StringOfBits,a,b)
    except:
        line.soopLine = "NA"
    try:
        # TRANSECT_NUMBER
        [a,b] = get_range(csvList, "TRANSECT_NUMBER", newMessageType)
        line.transectNumber = bits_to_dec(StringOfBits,a,b,1,0)
    except:
        line.transectNumber = -1
    try:
        # SEQUENCE_NUMBER
        [a,b] = get_range(csvList, "SEQUENCE_NUMBER", newMessageType)
        line.sequenceNumber = bits_to_dec(StringOfBits,a,b,1,0)
    except:
        line.sequenceNumber = -1

    return line

# get profile data based on probe type and recorder sampling frequency for depth calculation
def get_profile_data(StringOfBits, csvList, newMessageType, gearType):
    profile = ProfileClass()
    # get data points
    try:
        # TIMES_REPLICATED
        [a,b] = get_range(csvList, "TIMES_REPLICATED", newMessageType)
        profile.dataPoints = int(bits_to_dec(StringOfBits,a,b,1,0))
    except:
        profile.dataPoints = 0
    # get temperatures and depths
    try:        
        # temperatures and depths as recorded - no smoothering
        [a,b] = get_range(csvList, "SEA_SURFACE_TEMPERATURE", newMessageType)
        profile.temperatures = get_profile_temperatures(StringOfBits, profile.dataPoints, a)
        profile.depths = get_profile_depths(profile.dataPoints, gearType)
    except:
        profile.temperatures = []
        profile.depths = []

    return profile