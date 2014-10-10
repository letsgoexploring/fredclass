from fredclass import fred, quickplot
'''This program downloads and plots current unemployment data from FRED.

Created by: Brian C Jenkins. Email comments and suggestions to bcjenkin@uci.edu. Version date: August 29, 2014'''

unemp = fred('UNRATE')

quickplot(unemp,recess=True,save=True,name='fig_fredclass_example1')