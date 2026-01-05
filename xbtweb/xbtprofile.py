
import matplotlib.pyplot as plt
import os
import json
from xbtutils import utilities
from xbtutils.gear_info import GearClass


# Create profile plot as PNG image with matplotlib (~35kB each)
def make_profile_plot_image(profileDict, outputDir="output", extension = ".png"):
    try:
        # extract filename
        filename = profileDict['fileName'].split(".")[0]
        outputFilename = filename + extension
        # Extract depth and temperature data from the profile dictionary
        depths, temperatures = utilities.get_depth_temperature_pairs(profileDict)
        
        plt.figure(figsize=(6,8))
        plt.plot(temperatures, depths, color='red', linewidth=2)
        plt.gca().invert_yaxis()
        plot_title = f"{filename}\n{profileDict['soopLine']} | {profileDict['datetime']} | ( {profileDict['latitude']},{profileDict['longitude']} )"
        plt.title(plot_title, fontsize=10)
        plt.xlabel("Temperature (°C)", fontsize=10)
        plt.ylabel("Depth (m)", fontsize=10)
        plt.grid()

        # Save the plot as a PNG image
        file_path = os.path.join(outputDir, outputFilename)
        plt.savefig(file_path)
        plt.close()

    except Exception as e:
        print(f"> Error creating profile plot for {profileDict['fileName']}: {e}")


# Append profile row to existing html table in profiles page
# The table includes links to the plot image and json file for each profile
def append_profile_to_html_table(html_table, profileDict, index, plots_subdir, json_subdir):
    # get filenames and paths for plot and json
    plot_filename = profileDict['fileName'].replace(".bin", ".png")
    json_filename = profileDict['fileName'].replace(".bin", ".json")
    json_file_path = os.path.join( json_subdir, json_filename)
    plot_file_path = os.path.join( plots_subdir, plot_filename)

    # create html table row for profile
    profile_row = f"""
    <tr>
        <td class="checkbox"><input type="checkbox"></td>
        <td class="index">{index}</td>
        <td>{profileDict['soopLine']}</td>
        <td>{profileDict['datetime']}</td>
        <td>{profileDict['fileName']}</td>        
        <td>{profileDict['latitude']} , {profileDict['longitude']}</td>      
        <td><a href="{plot_file_path}" alt="Profile Plot">PLOT</a></td>
        <td><a href="{json_file_path}" alt="Profile JSON">JSON</a></td>        
    </tr>
    """
    # append to existing html table
    html_table += profile_row
    return html_table


# Complete html table with header and footer for profiles page
# used after all profile rows have been appended
def complete_profile_html_table(html_table):
    html_table_header = "<tr>\n\t<th>-</th>\n\t<th>Index</th>\n\t<th>soopLine</th>\n\t<th>datetime</th>\n\t<th>fileName</th>\n\t<th>coordinates</th>\n\t<th>plot</th>\n\t<th>json</th>\n</tr>\n\t"
    html_table = html_table_header + html_table
    html_table = "<table id=\"profilesTable\">\n\t" + "<tbody id=\"profilesTableBody\">" + html_table + "</tbody>\n</table>\n" 
    html_table = html_table + """<div class="pagination-container">\n\t<button id="backButton">Back</button>\n\t<span id="pageInfo">Page 1 / 1</span>\n\t
        <button id="nextButton">Next</button>\n\t</div>\r\n<script src="static/js/table_script.js"></script> """
    return html_table   


# Create JSON file from profile dictionary
# The JSON file includes all profile metadata and data points, as well as calculated depths
def make_json_file_from_database(profileDict, outputDir):    
    try:
        # extract filename
        filename = profileDict['fileName'].split(".")[0]
        outputFilename = filename + ".json"

        # create json file path
        file_path = os.path.join(outputDir, outputFilename)

        # add depths to dictionary before saving to json
        gear = GearClass()
        gear.probe.coefA = profileDict['coefA']
        gear.probe.coefB = profileDict['coefB']
        gear.recorder.frequency = profileDict['recorderFrequency']
        depthList = utilities.get_profile_depths( profileDict['dataPoints'], gear) # calculate depths based on data points and gear info
        sep = ","
        depthProfile_str = sep.join(map(str, depthList)) # convert list to string for storage in json
        profileDict['depths'] = depthProfile_str

        # write profile dictionary to json file
        with open(file_path, 'w') as json_file:
            json.dump(profileDict, json_file, indent=4)

    except Exception as e:
        print(f"> Error creating JSON file for {profileDict['fileName']}: {e}")



############################## CODE ENDS HERE ##############################
# The following code creates interactive HTML plots using plotly, but it's not currently used in the project
# given the large file size of the HTML plots.


# import plotly.express as px
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go

# Create profile plot as interactive HTML with plotly
# HTML files are 4.7 MB
# def make_profile_plot_html(profileDict, outputDir="output"):

#     try:
#         # extract filename
#         filename = profileDict['fileName'].split(".")[0]
#         outputFilename = filename + "_plot.html"
#         # Extract depth and temperature data from the profile dictionary
#         depths, temperatures = utilities.get_depth_temperature_pairs(profileDict)

#         fig = go.Figure()
#         fig.add_trace( go.Scatter(x=temperatures, y=depths, mode='lines', name='XBT Profile', line_color="red" ))
#         fig.update_yaxes(autorange="reversed", title_text="Depth (m)")
#         fig.update_xaxes(title_text="Temperature (°C)")
#         plot_title = f"<b>{filename}</b><br>{profileDict['soopLine']}<br>{profileDict['datetime']}<br>({profileDict['latitude']},{profileDict['longitude']})"
#         fig.update_layout(title_text=plot_title, height=800, width=600, title_x=0.5)
#         # Save the plot as an HTML file

#         file_path = os.path.join(outputDir, outputFilename)
#         fig.write_html(file_path)

#     except Exception as e:
#         print(f"> Error creating profile plot for {profileDict['fileName']}: {e}")