# This program generates for each userid, a list of 10 (maximum) events which other users who are 'similar' to userid
# are attending on RA. 
from scipy import sparse
from numpy import linalg
from numpy.random import rand
import pandas as pd
from scipy.sparse import coo_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import KNeighborsClassifier
from scipy.sparse.linalg import eigs
import numpy as np
from scipy import linalg

# Load in all lists of userids/event pairs generated by RAEventMatrixGenerator.py

df_eventurl0 = pd.read_csv('../RAUseridEventurl.csv', delim_whitespace=True, error_bad_lines=False)
df_eventurl1 = pd.read_csv('../RAUseridEventurl-1.csv', delim_whitespace=True, error_bad_lines=False)
df_eventurl2 = pd.read_csv('../RAUseridEventurl-2.csv', delim_whitespace=True, error_bad_lines=False)
df_eventurl3 = pd.read_csv('../RAUseridEventurl-3.csv', delim_whitespace=True, error_bad_lines=False)
df_uidevent = pd.read_csv('../RA_row_cols_indexreset2.csv', delim_whitespace=True)

# List of row/columns of user attendances. 
df_rowcols1 = pd.read_csv('RA_row_col_id_urlSept25_2.csv', delim_whitespace=True)
df_rowcols2 = pd.read_csv('../RA_row_col_id_urlSept25_2Part2.csv', delim_whitespace=True)
rowcols = [df_rowcols1,df_rowcols2]

# Concatenate the two files into one.
df_rowcols = pd.concat(rowcols, ignore_index=True).drop_duplicates()

# Merge all of the data files which contain the userid/eventurl pairs.
df_eventurl0 = df_eventurl0.drop_duplicates()
df_eventurl1 = df_eventurl1.drop_duplicates()
df_eventurl2 = df_eventurl2.drop_duplicates()
df_eventurl3 = df_eventurl3.drop_duplicates()
mylist = [df_eventurl0, df_eventurl1, df_eventurl2, df_eventurl3]
df_eventurl = pd.concat(mylist, ignore_index=True).drop_duplicates()
rows = df_uidevent['row']


# Some data was corrupt - check by looking for h and cut out the bad indices where there isn't a valid URL.

bad_index1 = df_eventurl['userid'].str.contains("h")
df_eventurl = df_eventurl[bad_index1 == False]
df_eventurl = df_eventurl[df_eventurl['url'].str.contains("http") == True]


# Generate the sparse matrix of users/events.
rows = np.array(df_rowcols['row'])
columns = np.array(df_rowcols['column'])
data = [1]*len(columns)
X = coo_matrix((data, (rows,columns)), shape=(75988+1,25022+1))


# Load the file of nearest neighbor rows for each userid.

df_nn = pd.read_csv('RA_nearest_neighbors_normalizedOct1.csv', delim_whitespace=True)


# Get the future events of user on user_row. Modify -100 depending on date.
def get_events(user_row):
    user_events = np.squeeze(np.asarray(X.getrow(user_row).todense()))[-100:]
    nonzeroind = np.nonzero(user_events)[0]
    nonzeroind = np.add(nonzeroind, 25022+1-120)
    return nonzeroind
        

# For each of the nearest neighbors, find the future events they are attending and append them to event_list.
def print_top_events(user_row_list):
    event_list = []
    reversed_list = user_row_list[::-1]
    for user_row in reversed_list[2:]:
        events = get_events(user_row)
        for event in events:
                event_object = df_rowcols[df_rowcols['column'] == event]['url'].drop_duplicates()
                event_object = str(event_object)[str(event_object).find('http:'):str(event_object).find('\n')]
                event_list.append(event_object)
    return event_list


# print urls at the top of the csv file so pandas can read them easily later.
print 'userid',
for i in range(1,11):
	mystr = 'url' + str(i)
	print mystr,
print ''

# For each user, get their list of nearest neighbors, print userid and the top 10 events suggested.
for i in range(0,len(df_nn)): 
    sample = np.squeeze(np.asarray(df_nn.ix[i]))
    event_list = print_top_events(sample)
    max_num=0
    if len(event_list) > 0:
	print str(df_rowcols[df_rowcols['row']==i]['userid'].drop_duplicates()).split()[1],
        for event in event_list:
            if max_num >= 10:
                break
            else:
                print event,
                max_num += 1
        print ''
