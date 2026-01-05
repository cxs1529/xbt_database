from .utilities import *

# Vessel Information Class
class VesselClass:
  def __init__(self, callSign="na", imo=-99, shipName="na", shipSpeed=-99, shipDirection=-99, launchHeight=-99, latitude=-99, longitude=-99, totalWaterDepth=-99):
    self.callSign = callSign
    self.imo = imo
    self.shipName = shipName
    self.shipSpeed = shipSpeed
    self.shipDirection = shipDirection
    self.launchHeight = launchHeight
    self.latitude = latitude
    self.longitude = longitude
    self.totalWaterDepth = totalWaterDepth

# Extract Vessel Information from binary string
def get_vessel(StringOfBits, csvList, newMessageType):

    vessel = VesselClass()
    try:
      # WMO_ID
      [a,b] = get_range(csvList, "WMO_ID", newMessageType)
      vessel.callSign = bits_to_ascii(StringOfBits,a,b)
    except:
      vessel.callSign = "NA"
    try:
      # LLOYDS
      [a,b] = get_range(csvList, "LLOYDS", newMessageType)
      vessel.imo = int(bits_to_dec(StringOfBits,a,b,1,0))
    except:
      vessel.imo = -1
    try:
      # LATITUDE
      [a,b] = get_range(csvList, "LATITUDE", newMessageType)
      vessel.latitude = bits_to_dec(StringOfBits,a,b,1E5,-9E6)
    except:
      vessel.latitude = -1
    try:
      # LONGITUDE
      [a,b] = get_range(csvList, "LONGITUDE", newMessageType)
      vessel.longitude = bits_to_dec(StringOfBits,a,b,1E5,-18E6)
    except:
      vessel.longitude = -1
    try:
      # SHIP_NAME
      [a,b] = get_range(csvList, "SHIP_NAME", newMessageType)
      vessel.shipName = bits_to_ascii(StringOfBits,a,b)
    except:
      vessel.shipName = "NA"
    try:
      # LAUNCH_HEIGHT
      [a,b] = get_range(csvList, "LAUNCH_HEIGHT", newMessageType)
      vessel.launchHeight = bits_to_dec(StringOfBits,a,b,1E2,0)   
    except:
      vessel.launchHeight = -1
    try:
      # SHIP_SPEED
      [a,b] = get_range(csvList, "SHIP_SPEED", newMessageType)
      vessel.shipSpeed = round(bits_to_dec(StringOfBits,a,b,1E2,0) * 1.94384, 2) # m/s to knot
    except:
      vessel.shipSpeed = -1
    try:
      # SHIP_DIRECTION
      [a,b] = get_range(csvList, "SHIP_DIRECTION", newMessageType)
      vessel.shipDirection = bits_to_dec(StringOfBits,a,b,1,0)  
    except:
      vessel.shipDirection = -1 
    try:
      # TOTAL_WATER_DEPTH
      [a,b] = get_range(csvList, "TOTAL_WATER_DEPTH", newMessageType)
      vessel.totalWaterDepth = bits_to_dec(StringOfBits,a,b,1,0)
    except:
      vessel.totalWaterDepth = -1       

    return vessel