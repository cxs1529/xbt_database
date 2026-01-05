from jinja2 import Environment, FileSystemLoader
from xbtutils import database, utilities
import os
from xbtweb import xbtmap, xbtprofile, xbtstats

################################ DESCRIPTION ################################
# This module contains functions to create HTML pages for the XBT website.
# It uses Jinja2 templates to generate the HTML content dynamically based on
# data retrieved from the database.



############################## CODE STARTS HERE ##############################

# Convert CSV string database report to HTML table
# It is used to create the summary reports in the home page
def to_html_table(csv_string):
    print("> Converting report to html table")
    # split cvs lines into list
    lines = csv_string.splitlines()

    # Check that the report has results
    if lines[0].startswith("WARNING") == False:

        html_table = ""
        for row,line in enumerate(lines):
            if row == 0:
                html_header = "<tr>\n\t"
                line_headers = line.split(",")
                for header in line_headers:
                    html_header = html_header + "\t<th>" + header + "</hr>\n\t"
                html_header = html_header + "</tr>\n\t"   
                html_table = html_table + html_header
            else:
                html_data = "<tr>\n\t"
                line_values = line.split(",")
                for value in line_values:
                    html_data = html_data + "\t<td>" + value + "</td>\n\t"
                html_data = html_data + "</tr>\n\t"
                html_table = html_table + html_data
        html_string = "<table>\n\t" + html_table + "</table>\n"
    else:
        html_string = "<p>No results</p>"    

    return html_string


# Create home page with current and previous fiscal year summary reports
# It creates index.html in the outputDir, based on the index_template.html in templates_dir
def create_home_page(dbfile, templates_dir, outputDir, now_timestamp):
    print("> Creating home page...")
    # CURRENT FY REPORT
    # get report text from database
    report_A_current = database.database_fy_summary_A(dbfile, yearOffset = 0, show=False)
    report_B_current = database.database_fy_summary_B(dbfile, yearOffset = 0, show=False)
    report_C_current = database.database_fy_summary_C(dbfile, yearOffset = 0, show=False)
    # create html tables
    html_report_A = to_html_table(report_A_current)
    html_report_B = to_html_table(report_B_current)
    html_report_C = to_html_table(report_C_current)

    # PREVIOUS FY REPORT
    report_A_previous = database.database_fy_summary_A(dbfile, yearOffset = -1, show=False)
    report_B_previous = database.database_fy_summary_B(dbfile, yearOffset = -1, show=False)
    report_C_previous = database.database_fy_summary_C(dbfile, yearOffset = -1, show=False)
    # create html tables
    html_report_A_prev = to_html_table(report_A_previous)
    html_report_B_prev = to_html_table(report_B_previous)
    html_report_C_prev = to_html_table(report_C_previous)

    # SETUP JINJA2 ENVIRONMENT WITH TEMPLATES
    env = Environment(loader=FileSystemLoader(templates_dir) )

    # CREATE HOME PAGE HTML    
    index_template = env.get_template("index_template.html")
    index_output = index_template.render(
        report_A_current=html_report_A,
        report_B_current=html_report_B,
        report_C_current=html_report_C,
        report_A_previous=html_report_A_prev,
        report_B_previous=html_report_B_prev,
        report_C_previous=html_report_C_prev,
        current_fy=utilities.get_current_fy_range(0).fiscalYear,
        timestamp=now_timestamp
    )  
    # write html to index file
    index_file_path = os.path.join(outputDir,"index.html")
    with open(index_file_path, 'w') as fout:
        fout.write(index_output)

    print("> Home page created.\r\n")
    

# Create map page with interactive map of profiles
# It creates map.html in the outputParentDir, based on the map_template.html in templates_dir
# It uses xbtmap module to create the map html file that is embedded in the map page as an iframe
# It also needs the subdirectories for json and plots files that are linked from the map markers
def create_map_page(dbfile, templates_dir, outputParentDir, map_subdir, json_subdir, plots_subdir, now_timestamp):
    print("> Creating map page...")
    # get fy date range to query database >> current and previous fy
    [fyStart, fyEnd] = [utilities.get_current_fy_range(-1).startDate, utilities.get_current_fy_range(0).endDate]
    # read profile list from database
    profile_list = database.read_database_map_info(dbfile, limit=15000, dateStart=fyStart, dateEnd=fyEnd)
    # create html map with folium
    xbtMapFile = "xbtmap.html"
    xbtmap.make_xbt_map(profile_list, outputParentDir, map_subdir, plots_subdir, json_subdir, xbtMapFile)
    # map html file path
    xbtmap_file_path = os.path.join(outputParentDir, map_subdir, xbtMapFile)

    # SETUP JINJA2 ENVIRONMENT WITH TEMPLATES
    env = Environment(loader=FileSystemLoader(templates_dir) )

    # CREATE MAP PAGE HTML
    # generate map page
    map_template = env.get_template("map_template.html")
    map_output = map_template.render(
        timestamp=now_timestamp,
        map_path=xbtmap_file_path
    )
    # write html to map file page
    map_page_path = os.path.join(outputParentDir,"map.html")
    with open(map_page_path, 'w') as fout:
        fout.write(map_output)

    print("> Map page created.\r\n")

# Create stats page with various statistics plots
# It creates stats.html in the outputDir, based on the stats_template.html in templates_dir
# It uses xbtstats module to create the plots that are embedded in the stats page as iframes
def create_stats_page(dbfile, templates_dir, outputDir, stats_subdir, now_timestamp):
    print("> Creating stats page...")
    # get fy date range to query database >> current and previous fy
    [fyStart, fyEnd] = [utilities.get_current_fy_range(-1).startDate, utilities.get_current_fy_range(0).endDate]
    # dirpath for all stats plots, create if it doesn't exist
    statsPlotDir = os.path.join(outputDir, stats_subdir)
    os.makedirs(statsPlotDir, exist_ok=True)

    # plot stats by soopline for last 2 fiscal years
    dictlist_soop = database.stats_by_soopline_2fy(dbfile, yearOffset = 0, show = False)
    xbtstats.make_plot_by_soopline(dictlist_soop, outputDir=statsPlotDir, fname = "plot_by_soopline_bar.html", w=1400, h=600)
    soopline_bar_path = os.path.join(stats_subdir, "plot_by_soopline_bar.html")
    xbtstats.make_plot_by_soopline_pie(dictlist_soop, outputDir=statsPlotDir, fname = "plot_by_soopline_pie.html", w=1200, h=550)
    soopline_pie_path = os.path.join(stats_subdir, "plot_by_soopline_pie.html")

    # plot stats by map temperature for current fiscal year
    dictlist_sst = database.stats_by_map_temperature(dbfile, yearOffset = 0, show = False)
    xbtstats.make_plot_by_map_temperature(dictlist_sst, outputDir=statsPlotDir, fname = "plot_by_map_temperature.html", w=1400, h=800)
    map_temperature_path = os.path.join(stats_subdir, "plot_by_map_temperature.html")
    # plot stats chart by agency for current and previous fiscal year
    dictlist_agency = database.stats_by_agency(dbfile, yearOffset = 0, show = False)
    xbtstats.make_plot_by_agency_bar(dictlist_agency, outputDir=statsPlotDir, fname = "plot_by_agency_bar.html", w=1400, h=600)
    agency_bar_path = os.path.join(stats_subdir, "plot_by_agency_bar.html")
    xbtstats.make_plot_by_agency_pie(dictlist_agency, outputDir=statsPlotDir, fname = "plot_by_agency_pie.html", w=1200, h=550)
    agency_pie_path = os.path.join(stats_subdir, "plot_by_agency_pie.html")
    # SETUP JINJA2 ENVIRONMENT WITH TEMPLATES
    env = Environment(loader=FileSystemLoader(templates_dir) )

    # CREATE STATS PAGE HTML
    stats_template = env.get_template("stats_template.html")
    stats_output = stats_template.render(
        timestamp=now_timestamp,
        plot_by_soopline_bar_path=soopline_bar_path,
        plot_by_soopline_pie_path=soopline_pie_path,
        plot_by_map_temperature_path=map_temperature_path,
        plot_by_agency_bar_path=agency_bar_path,
        plot_by_agency_pie_path=agency_pie_path
    )
    # write html to stats file page
    stats_file_path = os.path.join(outputDir,"stats.html")
    with open(stats_file_path, 'w') as fout:
        fout.write(stats_output)

    print("> Stats page created.\r\n")

# Create profiles page with a table of profiles and their depth-temperature plots and json links
# It creates profiles.html in the outputDir, based on the profiles_template.html in templates_dir
# It uses xbtprofile module to create the profile plots and json files that are linked from the table
def create_profiles_page(dbfile, templates_dir, outputDir, plots_subdir, json_subdir, now_timestamp, profileLimit = 15000, verbose=False):
    print("> Creating profiles page and plots...")
    # get fy date range to query database >> current and previous fy
    [fyStart, fyEnd] = [utilities.get_current_fy_range(-1).startDate, utilities.get_current_fy_range(0).endDate]
    # get profile data from database in the form of list of dictionaries
    profile_data_list = database.read_database_profiles_by_date_range(dbfile, limit = profileLimit, dateStart=fyStart, dateEnd=fyEnd, show=False)
    # create output dir for plots if it doesn't exist
    xbtplots_dir_path = os.path.join(outputDir, plots_subdir)
    os.makedirs(xbtplots_dir_path, exist_ok=True)
    # get list of already plotted files
    plotted_files = utilities.list_dir_files(xbtplots_dir_path, extension = ".png")

    html_profile_table_str = ""
    # create depth-temperature plots for each profile and save as html
    fileCount = len(profile_data_list)
    for i,profileDict in enumerate(profile_data_list):
        # get plot filename
        plot_filename = profileDict['fileName'].replace(".bin", ".png")
        # append to html table        
        html_profile_table_str = xbtprofile.append_profile_to_html_table(html_profile_table_str, profileDict, i+1, plots_subdir, json_subdir)
        # check if plots were previously created
        if plot_filename not in plotted_files:
            if verbose:
                print(f"> {i+1}:{fileCount} Creating profile plot {profileDict['fileName']}")
            xbtprofile.make_profile_plot_image(profileDict, outputDir=xbtplots_dir_path, extension = ".png")
        else:
            if verbose:
                print(f"> {i+1}:{fileCount} Profile plot for {profileDict['fileName']} already exists, skipping...")
            continue
        # add progress indicator
        if (i+1) % 100 == 0:
            print(f"> Processed {i+1} of {fileCount} plot profiles...")
    # complete html table with header and footer
    html_profile_table_str = xbtprofile.complete_profile_html_table(html_profile_table_str)

    # SETUP JINJA2 ENVIRONMENT WITH TEMPLATES
    env = Environment(loader=FileSystemLoader(templates_dir) )

    # CREATE PROFILES PAGE HTML
    profiles_template = env.get_template("profiles_template.html") 
    profiles_output = profiles_template.render(
        timestamp=now_timestamp,
        profile_table=html_profile_table_str        
    )
    # write html to profiles file page
    profiles_file_path = os.path.join(outputDir,"profiles.html")
    with open(profiles_file_path, 'w') as fout:
        fout.write(profiles_output)

    print(f"> Profiles page created and plots saved in {xbtplots_dir_path}\r\n")



# Create JSON files for profiles from database
# It creates json files in the outputDir for each profile in the database for the current and previous fiscal year
# checks if the json file already exists before creating it to avoid reprocessing the same profile
# It uses xbtprofile module to create the json files
def make_json_files(dbfile, outputDir, profileLimit=15000, verbose=False):
    print("> Creating JSON files for profiles...")
    # get fy date range to query database >> current and previous fy
    [fyStart, fyEnd] = [utilities.get_current_fy_range(-1).startDate, utilities.get_current_fy_range(0).endDate]

    # get list of profiles already plotted
    generated_json_files = utilities.list_dir_files(outputDir, extension = ".json")

    # create output dir for plots if it doesn't exist
    os.makedirs(outputDir, exist_ok=True)
    # read all profiles from database
    full_db_list = database.read_database_all_by_date_range(dbfile, limit=profileLimit, dateStart=fyStart, dateEnd=fyEnd)
    # create json file for each profile
    fileCount = len(full_db_list)
    for i,profileDict in enumerate(full_db_list):
        json_filename = profileDict['fileName'].replace(".bin", ".json")
        # check if json file was previously created
        if json_filename not in generated_json_files:
            if verbose:
                print(f"> {i+1}:{fileCount} Creating JSON file {profileDict['fileName']}")
            xbtprofile.make_json_file_from_database(profileDict, outputDir)
        else:
            if verbose:
                print(f"> {i+1}:{fileCount} JSON file for {profileDict['fileName']} already exists, skipping...")
    # add progress indicator
        if (i+1) % 100 == 0:
            print(f"> Processed {i+1} of {fileCount} json profiles...")

    print(f"> JSON files created and saved in {outputDir}\r\n")