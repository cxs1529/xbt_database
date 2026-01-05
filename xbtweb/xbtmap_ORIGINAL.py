import folium
from folium.plugins import TagFilterButton
import random
import os
import posixpath
from urllib.parse import quote

# This file creates an interactive map with markers for XBT profiles but only works in newer folium versions that support TagFilterButton
# which is not the case for the phodnet current python version 3.6.8

# creates the xbt map with markers from list of dictionaries/profiles
# each dictionary contains relevant info for each profile to be displayed in the map
# dict_list: list of dictionaries with profile info
# outputParentDir: parent output directory where map subdir is located
def make_xbt_map(dict_list, outputParentDir, map_subdir, plots_subdir, json_subdir, fname):
    init_pos = [20.416501, -69.914840]
    full_map = folium.Map(location=init_pos, zoom_start=6)

    # initialize tag filter lists
    tags_year = ["None"]
    tags_soopLine = ["None"]
    tags_callSign = ["None"]
    tags_shipName = ["None"]
    tags_institutionName = ["None"]
    tags_agencyName = ["None"]

    # initialize previous values for changing color when any of these change in loop
    soopLine_prev = ""
    callSign_prev = ""
    transectNumber_prev = ""
    # loop through list of dictionaries/profiles
    for dict in dict_list:           
        # extract reelvant values
        latitude = dict["latitude"]
        longitude = dict["longitude"]
        soopLine = dict["soopLine"]
        transectNumber = dict["transectNumber"]
        callSign = dict["callSign"]
        shipName = dict["shipName"]
        institutionName = dict["institutionName"]
        agencyName = dict["agencyName"]
        datetime = dict["datetime"]
        fileName = dict["fileName"]

        # add plot and json links to popup
        plotFilename = fileName.replace(".bin", ".png")
        jsonFilename = fileName.replace(".bin", ".json")
        # Normalize provided subdir paths to POSIX (replace backslashes)
        plots_subdir_posix = plots_subdir.replace("\\", "/").strip("/")
        json_subdir_posix = json_subdir.replace("\\", "/").strip("/")
        # Build web-friendly relative URLs (use forward slashes) and URL-encode filenames
        plotLink = posixpath.join("../../", plots_subdir_posix, plotFilename)
        jsonLink = posixpath.join("../../", json_subdir_posix, jsonFilename)
        # URL-encode the path but keep forward slashes
        plotLink = quote(plotLink, safe="/")
        jsonLink = quote(jsonLink, safe="/")

        # check if callsign or soopline changed
        if (callSign != callSign_prev) or (soopLine != soopLine_prev) or (transectNumber != transectNumber_prev):
            fc_r,fc_g,fc_b = generate_random_rgb_color()

        # format to plot in map
        popup_text = f"callSign: {callSign}<br>position: {(latitude):.3f},{(longitude):.3f}<br>soopLine: {soopLine}<br>datetime: {datetime}<br>transectNumber: {transectNumber}<br>file: {fileName}<br><a href=\"{jsonLink}\" alt='JSON'>JSON</a>  |  <a href=\"{plotLink}\" alt='Plot'>Plot</a>"
        tip_text = f"callSign: {callSign}<br>soopLine: {soopLine} ({transectNumber})<br>datetime: {datetime}"
        # Tag marker for filtering
        profileYear = datetime[:4]
        tags=[soopLine, callSign, shipName, institutionName, agencyName, profileYear]        
        # include tags in tag list for filter buttons        
        if soopLine not in tags_soopLine:
            tags_soopLine.append(soopLine)
        if profileYear not in tags_year:
            tags_year.append(profileYear)
        if callSign not in tags_callSign:
            tags_callSign.append(callSign)
        if shipName not in tags_shipName:
            tags_shipName.append(shipName)
        if institutionName not in tags_institutionName:
            tags_institutionName.append(institutionName)
        if agencyName not in tags_agencyName:
            tags_agencyName.append(agencyName)

        # marker properties
        fillcolor = f"rgb({fc_r},{fc_g},{fc_b})"
        extcolor = "white"
        radius = 5
        # get marker object and add to map
        obj = create_map_marker(latitude , longitude, radius, extcolor, fillcolor, popup_text, tip_text, tags)
        obj.add_to(full_map)
        # reset previous values for coloring
        callSign_prev = callSign
        soopLine_prev = soopLine
        transectNumber_prev = transectNumber

    # ADD FILTER MARKER IN MAP
    # add tag filter buttons to map
    # https://fontawesome.com/search?q=boat&ic=free-collection
    # https://github.com/maydemirx/leaflet-tag-filter-button
    year_filter = TagFilterButton(icon="fa-calendar-days", data=tags_year, button_name="Filter by Year")
    year_filter.add_to(full_map)
    soopline_filter = TagFilterButton(icon="fa-route", data=tags_soopLine, button_name="Filter by SOOP Line")
    soopline_filter.add_to(full_map)
    callsign_filter = TagFilterButton(icon="fa-sailboat", data=tags_callSign, button_name="Filter by Call Sign")
    callsign_filter.add_to(full_map)
    shipname_filter = TagFilterButton(icon="fa-anchor", data=tags_shipName, button_name="Filter by Ship Name")
    shipname_filter.add_to(full_map)
    institution_filter = TagFilterButton(icon="fa-building", data=tags_institutionName, button_name="Filter by Institution Name")
    institution_filter.add_to(full_map)
    agency_filter = TagFilterButton(icon="fa-light fa-building-columns", data=tags_agencyName, button_name="Filter by Agency Name")
    agency_filter.add_to(full_map)

    # SAVE MAP TO HTML FILE
    # create output dir if it doesn't exist
    xbtmap_dir_path = os.path.join(outputParentDir, map_subdir)
    os.makedirs(xbtmap_dir_path, exist_ok=True)
    # save map as html    
    xbtmap_file_path = os.path.join(xbtmap_dir_path, fname)
    full_map.save(xbtmap_file_path)
    print(f"> XBT Map saved in {xbtmap_file_path}")
    

# creates a circle marker and returns the marker object to add into the map
def create_map_marker(lat , lon, radius, extcolor, fillcolor, popup_text, tip_text, tags):

    myobj = folium.CircleMarker(
        location=[lat, lon],        # Latitude and Longitude
        radius=radius,              # Radius in pixels
        color=extcolor,             # Outline color
        fill=True,                  # Fill the circle
        fill_color=fillcolor,       # Fill color
        fill_opacity=0.7,           # Fill opacity
        popup=popup_text,           # Popup text on click
        tooltip=tip_text,           # Tooltip text on hover
        tags=tags                   # Tags for filtering  
    )
    return myobj


# generates a random rgb color for the map markers
def generate_random_rgb_color():
    """Generates a random RGB color as a tuple (r, g, b)."""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)
