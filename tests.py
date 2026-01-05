from xbtutils import database
from xbtweb import xbtstats

dbfile = "xbtData.db"

# # Create database report and optionally export as a text file
# database.database_summary(dbfile, start_date="2025-01-01", end_date="2025-03-01",outputDir="output", fname="myreport.txt", export=False)

# # read all database tables in raw format
# database.read_database_all(dbfile, 10)

# # read all profiles matching a callsign, and optionally plot all profiles
# database.read_database_profile(dbfile, callsign="9V8584", plot_profiles=True)

# # read all profile matching a callsign without plotting profiles
# database.read_database_profile(dbfile, "9V8584")

# # read database profile headers within a date range
# database.read_database_date_range(dbfile, "2025-10-20", "2025-10-22")

# # list all tables and columns in the database
# database.list_database_tables(dbfile)

# # The most complete filter. Read database filtering by callsign, shipname, soop line, rider, dates and optionally export a json file for each entry
# Use wildcard '%' for incomplete strings i.e. 'A%' filters all variable values starting in 'A'
# database.read_database_filtered(dbfile, callsign = "%", shipname = "%", soopline = "AX07", ridername = "%", 
#                                 date_start="2025-01-01", date_end="2025-10-31", export_json=True, response_limit=100)

# STATISTICS PLOTTING EXAMPLES

# plot stats by soopline for last 2 fiscal years
# dictlist_soop = database.stats_by_soopline_2fy(dbfile, yearOffset = 0, show = False)
# xbtstats.make_plot_by_soopline(dictlist_soop, outputDir="test_output", fname = "plot_by_soopline_bar.html")
# xbtstats.make_plot_by_soopline_pie(dictlist_soop, outputDir="test_output", fname = "plot_by_soopline_pie.html")

# plot stats by map temperature for current fiscal year
# dictlist_sst = database.stats_by_map_temperature(dbfile, yearOffset = 0, show = False)
# xbtstats.make_plot_by_map_temperature(dictlist_sst, outputDir="test_output", fname = "plot_by_map_temperature.html")

# plot stats chart by agency for current and previous fiscal year
dictlist_agency = database.stats_by_agency(dbfile, yearOffset = 0, show = False)
xbtstats.make_plot_by_agency_bar(dictlist_agency, outputDir="test_output", fname = "plot_by_agency_bar.html")
xbtstats.make_plot_by_agency_pie(dictlist_agency, outputDir="test_output", fname = "plot_by_agency_pie.html")