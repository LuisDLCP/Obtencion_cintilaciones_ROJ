#!/usr/bin/python3.6
# This script gets s4 files in the LISN format 
# Author: Luis De La Cruz
import numpy as np
import pandas as pd
import datetime
import glob
import os 

root_path = "/home/cesar/Desktop/luisd/scripts/Obtencion_cintilaciones/"
input_files_path = root_path + "data_input/Data_set/"
input_files_path_op = root_path + "data_input/Data_procesada/"
output_files_path = root_path + "data_output/lisn_enriched/"

# Read ISMR files
def readISMR(input_file_name):
    # Read ismr file
    data = pd.read_csv(input_files_path + input_file_name, 
                        usecols=[0,1,2,4,5,7,8], header=None, squeeze=True)
    return data

# Convert an ISMR to LISN format file
def ismr2lisn(data):
    # Filter only the GPS constellation 
    mask1 = data[2].astype('int')<38 # SVID=PRN
    mask2 = data[2].astype('int')>0
    mask = mask1 & mask2 
    data = data[mask]

    # Get YY, DOY, SOD
    data[["YY","DOY","SOD"]] = data[[0,1]].astype('float').apply(WeekSeconds2UTC, axis=1)
    del data[0]
    del data[1]

    # Rename columns
    data.rename(columns={2:"PRN", 4: "Azim", 5:"Elev"}, inplace=True)

    # Calculate the corrected S4
    def get_correctedS4(row):
        s4 = row.iloc[0]
        correction= row.iloc[1]
        # Treat nan numbers 
        if pd.isnull(s4) or pd.isnull(correction):
            return np.nan
        else:
            # Calculate the corrected S4
            x = s4**2-correction**2
            if x>0:
                return x**0.5
            else:
                return 0
    
    data['S4'] = data[[7,8]].astype("float").apply(get_correctedS4, axis=1)
    del data[7]
    del data[8]

    # Rearrange columns 
    dataFrame = data[["YY","DOY","SOD","PRN","S4","Azim","Elev"]]

    # Create the final dataFrame
    def create_rowDataFrame(seconds):
        # Select a subset of data
        subset1 = dataFrame[dataFrame["SOD"] == seconds]
        # Create the list header
        header = list(subset1.iloc[0,:3].astype("int"))
        header.append(len(subset1))
        # Create the list body
        ss1 = subset1.loc[:,"PRN":] # Select some columns
        # Merge the list header and body
        for i in range(len(ss1)):
            body = list(ss1.iloc[i]) # float values
            body = [int(body[0])]+body[1:] # change PRN datatype: float -> int 
            header += body
        # Create the row dataframe
        parameters = pd.DataFrame([header])

        return parameters

    seconds_list = dataFrame['SOD']
    seconds_list = list(seconds_list.drop_duplicates())

    for i in range(len(seconds_list)):
        if i == 0:
            result = create_rowDataFrame(seconds_list[i])
        else:
            result = result.append(create_rowDataFrame(seconds_list[i]),ignore_index=True)
    result = result.round(3) # round decimal numerical values to 3 numbers

    return result

# Convert GPS time: week & seconds; to UTC time.
# OJO: It's missing the leapseconds, these value get from the navigation file
def WeekSeconds2UTC(row):
    gpsweek = row[0]
    gpsseconds = row[1]
    leapseconds = 0 # specify in the argument if it is given 

    datetimeformat = "%Y-%m-%d %H:%M:%S"
    first_epoch = datetime.datetime.strptime("1980-01-06 00:00:00",datetimeformat)
    elapsed = datetime.timedelta(days=(gpsweek*7),seconds=(gpsseconds-leapseconds))

    # LISN date format: 2 digit year, day of year, seconds since midnight for a day
    date = datetime.datetime.strftime(first_epoch + elapsed,"%y-%j;%H:%M:%S")

    year = int(date[:2])
    day_year = int(date[3:6])
    hour = int(date[7:9])
    minute = int(date[10:12])
    second = int(date[13:15])
    seconds_day = second*1 + minute*60 + hour*60*60

    return pd.Series({'YY':year, 'DOY':day_year, 'SOD':seconds_day})

# Convert SVIDs to PRN codes. The PRNs code were obtained from PolaRx5S Reference Guide.
def get_PRN(svid):
    if 1<=svid<=37:
        prn = "G"+str(svid)
    elif 38<=svid<=61:
        prn = "R"+str(svid-37)
    elif svid==62:
        prn = "NA"
    elif 63<=svid<=68:
        prn = "R"+str(svid-38)
    elif 71<=svid<=106:
        prn = "E"+str(svid-70)
    elif 107<=svid<=119:
        prn = "NA"
    elif 120<=svid<=140:
        prn = "S"+str(svid-100)
    elif 141<=svid<=177:
        prn = "C"+str(svid-140)
    elif 181<=svid<=187:
        prn = "J"+str(svid-180)
    elif 191<=svid<=197:
        prn = "I"+str(svid-190)
    elif 198<=svid<=215:
        prn = "S"+str(svid-157)
    elif 216<=svid<=222:
        prn = "I"+str(svid-208)
    else:
        prn = "svid not valid!"

    return prn

# Generate lisn file name
def get_file_name(file_name): # filename: ljic2710.20_.ismr
    station_name = file_name[:4] # ljic

    YY = file_name[-8:-6] # 20
    DOY = file_name[4:7] # 271
    today = YY + "-" + DOY # e.g. '21-271'
    fecha = datetime.datetime.strptime(today,"%y-%j")
    fecha = datetime.datetime.strftime(fecha,"%y-%m-%d") #e.g. '20-08-06'
    year = fecha[:2]
    month = fecha[3:5]
    day = fecha[6:8]

    file_name = station_name + "_" + year + month + day + ".s4"

    return file_name

def save_csv(file_name, value):
    s4_name = get_file_name(file_name)
    # Save dataFrame to csv file
    value.to_csv(output_files_path + s4_name, sep='\t',index=False,header=False,encoding='utf-8')
    return "Ok"

def main():
    list_input_files = glob.glob(input_files_path + "*.ismr")
    if len(list_input_files) > 0:
        for file_i in list_input_files:
            file_name = file_i[len(input_files_path):]    
            dframe_ismr = readISMR(file_name)
            dframe_lisn = ismr2lisn(dframe_ismr)
            save_csv(file_name, dframe_lisn)
            # Move input files to a permanent directory
            os.rename(file_i, input_files_path_op+file_name)

if __name__ == '__main__':
    main()
    print("Finished succesfully!")
