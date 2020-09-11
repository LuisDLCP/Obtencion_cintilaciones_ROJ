import pandas as pd

# Read ismr file
data = pd.read_csv("ljic219b15.20_.ismr", header=None, usecols=[0,1,2,7,4,5], squeeze=True)
#
WN = data[0] # Week number, since first epoch
TOW = data[1] # Time of week (s)
PRN = data[2]
S4 = data[7] # S4 in "Sig1"
alpha = data[4]
epsilon = data[5]

# GPS time: week & seconds; to UTC time.
# OJO: It's missing the leapseconds, these value get from the navigation file
def WeekSeconds2UTC(gpsweek,gpsseconds,leapseconds):
    import datetime

    datetimeformat = "%Y-%m-%d %H:%M:%S"
    first_epoch = datetime.datetime.strptime("1980-01-06 00:00:00",datetimeformat)
    elapsed = datetime.timedelta(days=(gpsweek*7),seconds=(gpsseconds-leapseconds))

    # LISN date format: 2 digit year, day of year, seconds since midnight for a day
    date = datetime.datetime.strftime(first_epoch + elapsed,"%y-%j;%H:%M:%S")

    year = int(date[:2])
    day = int(date[3:6])
    hour = int(date[7:9])
    minute = int(date[10:12])
    second = int(date[13:15])
    seconds_day = second*1 + minute*60 + hour*60*60

    return {"year":year, "day_year":day, "seconds_day": seconds_day}

# The PRNs code were obtained from PolaRx5S Reference Guide
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

# Create new columns of lisn file
yr = [] # year
dyr = [] # day_year
sd = [] # seconds_day
nd = [1]*len(WN)
prn = [] # prn
#
for i in range(len(WN)):
    fecha = WeekSeconds2UTC(int(WN[i]), int(TOW[i]), 0)
    yr.append(fecha["year"])
    dyr.append(fecha["day_year"])
    sd.append(fecha["seconds_day"])
    prn.append(get_PRN(int(PRN[i])))

# Create the lisn dataframe
list_tuples = list(zip(yr,dyr,sd,nd,prn)) # creates a list of tuples
dataFrame = pd.DataFrame(list_tuples, columns=['year','day','seconds','Ndata','PRN']) # creates a pandas dataframe

# Adding other pandas series
dataFrame['S4'] = S4
dataFrame['alpha'] = alpha
dataFrame['epsilon'] = epsilon

# Create a row dataFrame
def create_row(seconds):
    # Select a subset of data
    subset1 = dataFrame[dataFrame["seconds"] == seconds]
    # Create the list header
    header = list(subset1.iloc[0,:3])
    header.append(len(subset1))
    # Create the list body
    ss1 = subset1.loc[:,"PRN":] # Select some columns
    # Merge the list header and body
    for i in range(len(ss1)):
        header += list(ss1.iloc[i])
    # Create the row dataframe
    parameters = pd.DataFrame([header])

    return parameters

seconds_list = dataFrame['seconds']
seconds_list = list(seconds_list.drop_duplicates())

for i in range(len(seconds_list)):
    if i == 0:
        result = create_row(seconds_list[i])
    else:
        result = result.append(create_row(seconds_list[i]),ignore_index=True)
result = result.round(3) # round decimal numerical values to 3 numbers

# Save dataFrame to csv file
result.to_csv("ljic_21.s4", sep='\t',index=False,header=False,encoding='utf-8') # sep='\b'
