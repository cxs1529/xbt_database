from xbtutils import utilities
from xbtweb import xbt_html
import os

############################## DESCRIPTION ##############################
# This script generates a static website for XBT profile data stored in a database (the database must exist and be populated).
# It creates HTML pages, plots, and JSON files for data visualization.
# The website includes a home page with table summary reports, a map page with interactive maps, stats page with 
# interactive statistics plots, and a profiles page with all profiles and links to see plots/json files.

############################## CCONFIGURATION ##############################

max_plot_json_profiles = 15000 # max number of profiles to create plots and json for (each time it runs)
create_map_page = True # set to False to skip creating the map page (useful for testing other parts of the website)
create_stats_page = True # set to False to skip creating the stats page (useful for testing other parts of the website)
create_profiles_page = True # set to False to skip creating the profiles page (useful for testing other parts of the website)
# INPUT PATHS
# directories relative to make_web.py
dbfile = "xbtData.db" # database file with all profile data
html_templates_dir = os.path.join("xbtweb", "templates") # directory with html templates to use with jinja to create the main webpages

# OUTPUT PATHS
outputParentDir = "website" # parent output directory for the website
# subdirectories within outputParentDir
plots_subdir = os.path.join("static", "plots")
json_subdir = os.path.join("static", "json")
map_subdir = os.path.join("static", "maps")
stats_subdir = os.path.join("static", "stats")

############################## CODE STARTS HERE ##############################


# START OF MAIN
def main():
    # get timestamp for the website
    now_timestamp = utilities.get_current_timestamp()
    # create output parent dir if it doesn't exist
    os.makedirs(outputParentDir, exist_ok=True)
    # CREATE HOME PAGE HTML
    xbt_html.create_home_page(dbfile, html_templates_dir, outputParentDir, now_timestamp)
    # CREATE MAP PAGE HTML
    if create_map_page:
        xbt_html.create_map_page(dbfile, html_templates_dir, outputParentDir, map_subdir, json_subdir, plots_subdir, now_timestamp)
    # CREATE STATS PAGE HTML
    if create_stats_page:
        xbt_html.create_stats_page(dbfile, html_templates_dir, outputParentDir, stats_subdir, now_timestamp)
    # CREATE PROFILES PAGE HTML AND PLOTS
    if create_profiles_page:
        xbt_html.create_profiles_page(dbfile, html_templates_dir, outputParentDir, plots_subdir, json_subdir, now_timestamp, max_plot_json_profiles)
        # Create JSON files for profiles page 
        jsonDir = os.path.join(outputParentDir, json_subdir)
        xbt_html.make_json_files(dbfile, jsonDir, max_plot_json_profiles)

    # copy/update template css directory to output web directory
    css_dir_dst = os.path.join(outputParentDir,"static", "css")
    css_dir_src = os.path.join("xbtweb", "static", "css") 
    utilities.copy_directory_replacing_existing(css_dir_src, css_dir_dst)
    # copy/update template js directory with table back/next functionality to output web directory
    js_dir_dst = os.path.join(outputParentDir,"static", "js")
    js_dir_src = os.path.join("xbtweb", "static", "js") 
    utilities.copy_directory_replacing_existing(js_dir_src, js_dir_dst)
    # copy/update template image directory with table back/next functionality to output web directory
    img_dir_dst = os.path.join(outputParentDir,"static", "img")
    img_dir_src = os.path.join("xbtweb", "static", "img") 
    utilities.copy_directory_replacing_existing(img_dir_src, img_dir_dst)
    
    # get end timestamp and calculate runtime ONLY FOR TESTING PURPOSES
    end_timestamp = utilities.get_current_timestamp()
    runtime = utilities.calculate_time_difference(now_timestamp, end_timestamp)
    print(f"> Website generation completed in {runtime} seconds.")


# END OF MAIN

if __name__ == "__main__":
    main()