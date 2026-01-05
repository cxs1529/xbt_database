from xbtutils import utilities, decode, database
import os

############################################### DESCRIPTION ###############################################
# This script creates/updates a database with XBT profile data decoded from binary files
# It processes all binary files in the specified input directory and its year subdirectories
# It filters out repeated profiles based on file names before adding them to the database to avoid reprocessing a binary file
# The database will only include data from the specified calendar years (these directories must exist in inputDir)

############################################## CONFIGURATION ##############################################

# inputDir = "data"
inputDir = "C:\\Users\\christian.saiz\\Documents\\0_NOAA\\1_NOAA_work\\1_XBT\\ftp" # Process files in this directory
dbfile = "xbtData.db" # database name
displayHeader = False # display header info when decoding binary files
years = ["2024", "2025", "2026", "2027"] # create database only for these calendar years (these directories must exist in inputDir)

############################################# CODE STARTS HERE #############################################


# Create database from all binary files in parent directory
# input: parentDir - parent directory containing year subdirectories with binary files
#        year - year subdirectory to process
# output: filteredFiles - list of unique binary files in year directory
def get_unique_binaries(parentDir, year):
    yearDir = os.path.join(parentDir, year)
    # list files if it's a directory
    if os.path.isdir(yearDir):
        # list all binary files in directory
        binFiles = utilities.list_dir_files(yearDir, extension = ".bin")
        # filter repeated profiles based on file name
        filteredFiles = utilities.filter_repeated_profiles(binFiles)        
    else:
        print(f"> WARNING: {yearDir} not a valid directory!")
        filteredFiles = []
        
    return filteredFiles



# MAIN START
def main():    
    print("\r\n*** XBT BINARY DECODER - MAKE DATABASE FROM ALL FILES IN DIRECTORIES ***\r\n")
    # list files already in database that should be already unique
    processedFiles = database.list_files_in_database(dbfile)
    # loop through year directories to get all unique binary files and check which are new to add to database
    for year in years:
        uniqueBinaries = get_unique_binaries(inputDir, year)
        # if no files in directory, skip to next year
        if len(uniqueBinaries) == 0:
            print(f"> No binary files found in {year} directory!")
            continue
        # check which files are new and add to database
        for cnt,f in enumerate(uniqueBinaries):
            print(f"\r\n> File {cnt + 1} of {len(uniqueBinaries)}:")
            if f not in processedFiles:                
                filePath = os.path.join(inputDir, year, f)
                # decode XBT binary into ascii
                profileData, file_ok = decode.decode_binary(filePath) # returns xbtBinaryClass object including all metadata and profile data
                # add to database if no errors
                if file_ok:
                    # display header info if flag is set to True
                    if displayHeader == True:
                        profileData.print_binary_header() # display header info
                    # add profile header and data (except depths, as these values are redundant) to database if file is ok
                    database.xbt_add_to_database(profileData, dbfile)
                else:
                    print(f"> WARNING: {f} could not be decoded!")
            else:
                print(f"> File {f} already in database, skipping...")


# MAIN END
if __name__ == "__main__":
    main()


        










# print("\r\n*** XBT BINARY DECODER - MAKE DATABASE ONLY FOR DATE RANGE ***\r\n")
# current_fy = "fy25"
# list binary files in input directory by date range
# bin_list_raw = utilities.list_dir_binaries_by_date(inputDir, fiscal_year[current_fy])

# print(bin_list_raw)