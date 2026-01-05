import folium
from folium.plugins import GroupedLayerControl
import random
import os
import posixpath
from urllib.parse import quote

# This file creates an interactive map with markers for XBT profiles organized hierarchically:
# The Control Menu is grouped by Year, with individual SOOP Lines listed under each Year.

def make_xbt_map(dict_list, outputParentDir, map_subdir, plots_subdir, json_subdir, fname):
    init_pos = [20.416501, -69.914840]
    full_map = folium.Map(location=init_pos, zoom_start=6)

    # Dictionary to structure the GroupedLayerControl
    # Correct Structure: {'Year_String': [FeatureGroup1, FeatureGroup2, ...]}
    grouped_overlays = {}

    # Dictionary to keep track of created layers to avoid duplicates
    # Structure: {'2015_AX10': <folium.FeatureGroup Object>}
    created_layers = {}

    # Initialize previous values for color logic
    soopLine_prev = ""
    callSign_prev = ""
    transectNumber_prev = ""
    
    # ---------------------------------------------------------
    # 1. PROCESS PROFILES AND CREATE LAYERS
    # ---------------------------------------------------------
    for dict_item in dict_list:           
        # Extract relevant values
        latitude = dict_item["latitude"]
        longitude = dict_item["longitude"]
        soopLine = dict_item["soopLine"]
        transectNumber = dict_item["transectNumber"]
        callSign = dict_item["callSign"]
        datetime = dict_item["datetime"]
        fileName = dict_item["fileName"]
        
        # Extract Year to serve as the Group Header
        profileYear = datetime[:4]

        # Define a unique key for this Year + SOOP Line combination
        layer_key = f"{profileYear}_{soopLine}"

        # Check if the FeatureGroup (Layer) for this specific Year+SOOP exists
        if layer_key not in created_layers:
            # Create a new FeatureGroup. 
            # 'name' is what appears in the toggle list (just the SOOP Line name)
            fg = folium.FeatureGroup(name=soopLine, overlay=True)
            fg.add_to(full_map)
            
            # Store in our tracking dict
            created_layers[layer_key] = fg
            
            # Add to the grouped_overlays dictionary for the control
            # FIX: Use a LIST to store layers for the group, not a dictionary
            if profileYear not in grouped_overlays:
                grouped_overlays[profileYear] = []
            
            # Append the layer object to the list
            grouped_overlays[profileYear].append(fg)

        # ---------------------------------------------------------
        # 2. PREPARE POPUP CONTENT
        # ---------------------------------------------------------
        plotFilename = fileName.replace(".bin", ".png")
        jsonFilename = fileName.replace(".bin", ".json")
        plots_subdir_posix = plots_subdir.replace("\\", "/").strip("/")
        json_subdir_posix = json_subdir.replace("\\", "/").strip("/")
        plotLink = posixpath.join("../../", plots_subdir_posix, plotFilename)
        jsonLink = posixpath.join("../../", json_subdir_posix, jsonFilename)
        plotLink = quote(plotLink, safe="/")
        jsonLink = quote(jsonLink, safe="/")

        # Update color if key attributes change
        if (callSign != callSign_prev) or (soopLine != soopLine_prev) or (transectNumber != transectNumber_prev):
            fc_r, fc_g, fc_b = generate_random_rgb_color()

        popup_text = f"callSign: {callSign}<br>position: {(latitude):.3f},{(longitude):.3f}<br>soopLine: {soopLine}<br>datetime: {datetime}<br>transectNumber: {transectNumber}<br>file: {fileName}<br><a href=\"{jsonLink}\" alt='JSON'>JSON</a>  |  <a href=\"{plotLink}\" alt='Plot'>Plot</a>"
        tip_text = f"callSign: {callSign}<br>soopLine: {soopLine} ({transectNumber})<br>datetime: {datetime}"

        fillcolor = f"rgb({fc_r},{fc_g},{fc_b})"
        extcolor = "white"
        radius = 5
        
        # ---------------------------------------------------------
        # 3. CREATE MARKER AND ADD TO SPECIFIC LAYER
        # ---------------------------------------------------------
        obj = create_map_marker(latitude, longitude, radius, extcolor, fillcolor, popup_text, tip_text)
        
        # Add the marker to the correct FeatureGroup (Year + SOOP)
        obj.add_to(created_layers[layer_key])
        
        # Reset previous values
        callSign_prev = callSign
        soopLine_prev = soopLine
        transectNumber_prev = transectNumber

    # ---------------------------------------------------------
    # 4. ADD GROUPED LAYER CONTROL
    # ---------------------------------------------------------
    # This renders the menu with Years as headers and SOOP lines as checkboxes.
    # The 'groups' argument must be {'Group Name': [Layer1, Layer2, ...]}
    GroupedLayerControl(
        groups=grouped_overlays,
        collapsed=True,
        exclusive_groups=False 
    ).add_to(full_map)

    # SAVE MAP TO HTML FILE
    xbtmap_dir_path = os.path.join(outputParentDir, map_subdir)
    os.makedirs(xbtmap_dir_path, exist_ok=True)
    xbtmap_file_path = os.path.join(xbtmap_dir_path, fname)
    full_map.save(xbtmap_file_path)
    print(f"> XBT Map saved in {xbtmap_file_path}")

# creates a circle marker and returns the marker object
def create_map_marker(lat, lon, radius, extcolor, fillcolor, popup_text, tip_text):
    myobj = folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=extcolor,
        fill=True,
        fill_color=fillcolor,
        fill_opacity=0.7,
        popup=popup_text,
        tooltip=tip_text
    )
    return myobj

# generates a random rgb color
def generate_random_rgb_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)