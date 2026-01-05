from .utilities import *

class DataQualityClass:
    def __init__(self, code, name):
        self.code = code
        self.name = name

class DataResolutionClass:
    def __init__(self, code, name):
        self.code = code
        self.name = name

# DATA QC
class QualityClass:
    def __init__(self, qualityCode=-99, qualityName="na", resolutionCode=-99, resolutionName="na"):
        self.dataQuality = DataQualityClass(qualityCode, qualityName)
        self.dataResolution = DataResolutionClass(resolutionCode, resolutionName)


def get_data_quality(code):
    dataType = DataQualityClass(-99, "Description")
    dataType.code = code

    if code == 0:
        dataType.name = "Data Not Suspect"
    elif code == 1:
        dataType.name = "Data Slightly Suspect"
    elif code == 2:
        dataType.name = "Data Highly Suspect"
    elif code == 3:
        dataType.name = "Data Unfit For Use"
    else:
        dataType.name = "Unknown Data Quality Code"       

    return dataType


def get_data_resolution(code):
    dataRes = DataResolutionClass(-99, "Description")
    dataRes.code = code

    if code == 1:
        dataRes.name = "Full Resolution"
    elif code == 2:
        dataRes.name = "2 Meter Resolution"
    elif code == 3:
        dataRes.name = "Inflection Points"
    else:
        dataRes.name = "Unknown Data Resolution Code"       
    
    return dataRes


def get_data_qc(StringOfBits, csvList, newMessageType):
    dataQC = QualityClass()
    # get xbt data resolution
    [a,b] = get_range(csvList, "THIS_DATA_IS", newMessageType)
    dataIsCode = int(bits_to_dec(StringOfBits,a,b,1,0))
    dataQC.dataResolution = get_data_resolution(dataIsCode)
    # get xbt data quality
    [a,b] = get_range(csvList, "DATAQUALITY", newMessageType)
    dataQualityCode = int(bits_to_dec(StringOfBits,a,b,1,0))
    dataQC.dataQuality = get_data_quality(dataQualityCode)

    return dataQC

