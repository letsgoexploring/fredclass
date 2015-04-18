'''This module defines a class of objects, called FRED objects, that make it easy to download and manipulate data from the Federal Reserve Economic Database (FRED). FRED is a rich database managed by the Federal Reserve Bank of St Louis. Learn more about FRED:

    http://research.stlouisfed.org/fred2/

An instance of a fred object is initialized with the command:

    fredclass.fred(series_id)

where series_id is the unique Series ID for the FRED data series that is to be retreived (string format).

Module dependencies: matplotlib, numpy, scipy, statsmodels

Created by: Brian C Jenkins. Email comments and suggestions to bcjenkin@uci.edu. Version date: August 29, 2014.'''

import urllib, dateutil, pylab, datetime
from scipy.signal import lfilter
import numpy as np
import statsmodels.api as sm
tsa = sm.tsa

#
# Oct. 27, 2013: Added:
#                   1. 4 quarter moving average method
#                   2. log method
#                   3. bp, hp, cf filters
#                   4. monthly-to-quarter frequency converter
#                   5. per capita
#                   6. quickplot  function
#                   7. window_equalize function
#                   8. quarter-to-annual fequency converter
#               Need to add:
#                   8. (log) linear detrend
# Oct.  8, 2013: Commented raw2.pop(), Line 45. I don't know why it's there.
# Oct.  8, 2013: Changed Line 109 to max0 = T from max0 = T-1        
# Jan. 22, 2014: Added:
#                   1. monthtoannual
#                Changed:
#                   1. quartertoannuala to quartertoannual and changed the arguments.
#                Removed / Commented out:
#                   1. quartertoannualb
# Apr. 17, 2014: Changed:
#                   1. the ouput of the filters to .cycle and .trend so save the 
#                      original data.
#                Added:
#                   1. A linear trend method.
#                   2. A first-difference method.
#                   3. A function for computing linear trends of a set of series with a 
#                      common trend.
#                   4. A function for computing first differences of a set of series with
#                      a common trend.
# Aug. 21, 2014: Added:
#                   1. Added better documentation for everything
#                   2. Added new attributes for filtering methods.
# Mar. 21, 2015: Added:
#                   1. Option to pc() method compute percentage change ahead. Default is still backwards
#                   2. Option to apc() method compute annual percentage change ahead. Default is still backwards
# Mar. 29, 2015: Added:
#                   1. Changed how per capita is computed. Formerly used average pop. Now has options to use 
#                       end of period or average
# April 18, 2015: Changed:
#                   1. Changed how the fred object is initialized so that no id will generate an empty object
#                 Added functions:
#                   1. date_numbers(): converts a list of yyy-mm-dd date strings to date numbers
#                   2. toFRED(): function for creating a FRED object from non-FRED data

class fred:

    def __init__(self,series_id=None):
        
        if series_id == None:
            self.data = []
            self.dates = []
            self.datenums = []
            self.title = None
            self.t = None
            self.season = None
            self.freq = None
            self.source = None
            self.units = None
            self.daterange = None
            self.idCode = None
            self.updated = None

        else:
            series_url = "http://research.stlouisfed.org/fred2/data/"
            series_url = series_url + series_id + '.txt'
            webs = urllib.urlopen(series_url)
            raw = [line for line in webs]

            for k, val in enumerate(raw):
                if raw[k][0:5] == 'Title':
                    self.title = " ".join(x for x in raw[k].split()[1:])
                elif raw[k][0:3] == 'Sou':
                    self.source = " ".join(x for x in raw[k].split()[1:])
                elif raw[k][0:3] == 'Sea':
                    self.season = " ".join(x for x in raw[k].split()[1:])
                elif raw[k][0:3] == 'Fre':
                    self.freq = " ".join(x for x in raw[k].split()[1:])
                    if self.freq[0:5] == 'Daily':
                        self.t=365
                    elif self.freq[0:6] == 'Weekly':
                        self.t=52
                    elif self.freq[0:7] == 'Monthly':
                        self.t=12
                    elif self.freq[0:9] == 'Quarterly':
                        self.t=4
                    elif self.freq[0:6] == 'Annual':
                        self.t=1
                elif raw[k][0:3] == 'Uni':
                    self.units    = " ".join(x for x in raw[k].split()[1:])
                elif raw[k][0:3] == 'Dat':
                    self.daterange = " ".join(x for x in raw[k].split()[1:])
                elif raw[k][0:3] == 'Las':
                    self.updated  = " ".join(x for x in raw[k].split()[1:])
                elif raw[k][0:3] == 'DAT':
                    raw2 = raw[k+1:]
                    break

            # raw2.pop()
            date=range(len(raw2))
            data=range(len(raw2))

            # Create data for FRED object. Replace missing values with NaN string
            for k,n in enumerate(raw2):
                date[k] = raw2[k].split()[0]
                if raw2[k].split()[1] != '.':
                    data[k] = float(raw2[k].split()[1])
                else:
                    data[k] = 'NaN'

            self.id    = series_id
            self.data  = data
            self.dates = date
            self.datenums = [dateutil.parser.parse(s) for s in self.dates]

    def pc(self,log=True,method='backward'):

        '''Transforms data into percent change'''
        
        T = len(self.data)
        t = self.t
        if log==True:
            pct = [t * 100 * np.log(self.data[k+1]/ self.data[k]) for k in range(T-1)]
        else:
            pct = [t * 100 * (self.data[k+1] - self.data[k]) / self.data[k] for k in range(T-1)]
        if method=='backward':
            dte = self.dates[t:]
        elif method=='forward':
            dte = self.dates[:T-t]
        self.data  =pct
        self.dates =dte
        self.datenums = [dateutil.parser.parse(s) for s in self.dates]
        self.units = 'Percent'
        self.title = 'Percentage Change in '+self.title

    def apc(self,log=True,method='backward'):

        '''Transforms data into percent change from year ago'''
        
        T = len(self.data)
        t = self.t
        if log==True:
            pct = [100 * np.log(self.data[k+t]/ self.data[k]) for k in range(T-t)]
        else:
            pct = [100 * (self.data[k+t] - self.data[k]) / self.data[k] for k in range(T-t)]
        if method=='backward':
            dte = self.dates[t:]
        elif method=='forward':
            dte = self.dates[:T-t]
        self.data  =pct
        self.dates =dte
        self.datenums = [dateutil.parser.parse(s) for s in self.dates]
        self.units = 'Percent'
        self.title = 'Annual Percentage Change in '+self.title

    def ma(self,length):

        '''Transforms data into a moving average of a specified length'''
        
        T = len(self.data)
        self.data = lfilter(np.ones(length)/length, 1, self.data)[length:]
        # self.dates =self.dates[length:]
        self.dates =self.dates[length/2:-length/2]
        self.datenums = [dateutil.parser.parse(s) for s in self.dates]
        self.daterange = self.dates[0]+' to '+self.dates[-1]
        self.title = 'Moving average of '+self.title

    
    def replace(self,new):

        '''Replaces the data attribue of object with a new series.
        Be sure that the new series has the same length as the original data. '''

        if len(new) != len(self.data):
            print('New series and original have different lengths!')
        self.data = new

    def recent(self,T=10):
        '''lag is the number of obs to include in the window'''
        t = self.t
        self.data  =self.data[-lag * t:]
        self.dates =self.dates[-lag * t:]
        self.datenums = [dateutil.parser.parse(s) for s in self.dates]
        self.daterange = self.dates[0]+' to '+self.dates[-1]

    def window(self,win):
        '''Constrains the data to a specified date window.

        win is an ordered pair: win = [win_min, win_max]

            win_min is the date of the minimum date
            win_max is the date of the maximum date
        
        both are strings in 'yyyy-mm-dd' format'''

        T = len(self.data)
        win_min = win[0]
        win_max = win[1]
        win_min_num = pylab.date2num(dateutil.parser.parse(win_min))
        win_max_num = pylab.date2num(dateutil.parser.parse(win_max))
        date_num    = pylab.date2num([dateutil.parser.parse(s) for s in self.dates])
        dumpy       = date_num.tolist()
        min0 = 0
        max0 = T
        t = self.t

        if win_min_num > min(date_num):
            for k in range(T):
                if win_min_num <= dumpy[k]:
                    min0 = k
                    break
                                              
        if win_max_num < max(date_num):
            'Or here'
            for k in range(T):
                if win_max_num < dumpy[k]:
                    max0 = k
                    break

        self.data = self.data[min0:max0]
        self.dates = self.dates[min0:max0]
        self.datenums = [dateutil.parser.parse(s) for s in self.dates]
        self.daterange = self.dates[0]+' to '+self.dates[-1]

    def log(self):
        
        '''Tansforms data into natural log of original series'''

        self.data = [np.log(s) for s in self.data]
        self.units= 'log '+self.units
        self.title = 'Log '+self.title

    def bpfilter(self):

        '''Computes the bandpass (Baxter-King) filter of the series. Adds attributes:

            self.bpcycle : cyclical component of series
            self.bpdates : dates of bp filtered data
            self.bpdatenums : date numbers of bp filtered data

        '''

        if self.t !=4:
            print 'Warning: data frequency is not quarterly!'
        self.bpcycle = tsa.filters.bkfilter(self.data)
        self.bpdates = self.dates[12:-12]
        self.bpdatenums = [dateutil.parser.parse(s) for s in self.bpdates]
        
    def hpfilter(self):

        '''Computes the Hodrick-Prescott filter of original series. Adds attributes:

            self.hpcycle : cyclical component of series
            self.hptrend : trend component of series

        '''

        if self.t !=4:
            print 'Warning: data frequency is not quarterly!'
        self.hpcycle, self.hptrend = tsa.filters.hpfilter(self.data)

    def cffilter(self):

        '''Computes the Christiano-Fitzgerald filter of original series. Adds attributes:

            self.cffcycle : cyclical component of series
            self.cfftrend : trend component of series

        '''

        if self.t !=4:
            print 'Warning: data frequency is not quarterly!'
        self.cffcycle, self.cfftrend = tsa.filters.cffilter(self.data)

    def lintrend(self):

        '''Computes the linear trend of original series. Adds attributes:

            self.lincycle : cyclical component of series
            self.lintrend : trend component of series

        '''

        Y     = self.data
        time  = np.arange(len(self.data))
        ones  = np.ones(len(self.data))
        X     = np.column_stack([ones,time])
        model = sm.OLS(Y, X)
        result= model.fit()
        pred  = model.predict(X)
        self.lincycle= [y-p for y,p in zip(Y,pred)]
        self.lintrend= pred

    def firstdiff(self):

        '''Computes the first difference of original series. Adds attributes:

            self.diffcycle : cyclical component of series
            self.difftrend : trend component of series
            self.diffdates : shorter date sequence
            self.diffdatenums : shorter date numbers
            self.diffdata  : shorter data series

        '''

        Y     = self.data[1:]
        YL    = self.data[0:-1]
        DY    = [y-yl for y,yl in zip(Y,YL)]
        gam   = np.mean(DY)
        self.diffcycle = [d - gam for d in DY]
        self.diffdates = self.dates[1:]
        self.diffdatenums= self.datenums[1:]
        self.diffdata  = self.data[1:]
        self.difftrend = [yl + gam for yl in YL]


    def monthtoquarter(self,method='AVG'):
        
        '''Converts monthly data to quarterly data using one of three methods:

            AVG : average of three months (default)
            SUM : sum of three months
            END : third month value only

        '''

        if self.t !=12:
            print 'Warning: data frequency is not monthly!'
        T = len(self.data)
        temp_data = self.data[0:0]
        temp_dates = self.datenums[0:0]
        if method == 'AVG':
            for k in range(1,T-1):
                if (self.datenums[k].month == 2) or (self.datenums[k].month == 5) or (self.datenums[k].month == 8) or (self.datenums[k].month == 11):
                    temp_data.append((self.data[k-1]+self.data[k]+self.data[k+1])/3)  
                    temp_dates.append(self.dates[k-1])
        elif method == 'SUM':
            for k in range(1,T-1):
                if (self.datenums[k].month == 2) or (self.datenums[k].month == 5) or (self.datenums[k].month == 8) or (self.datenums[k].month == 11):
                    temp_data.append((self.data[k-1]+self.data[k]+self.data[k+1]))  
                    temp_dates.append(self.dates[k-1])
        elif method== 'END':
            for k in range(1,T-1):
                if (self.datenums[k].month == 2) or (self.datenums[k].month == 5) or (self.datenums[k].month == 8) or (self.datenums[k].month == 11):
                    temp_data.append(self.data[k+1])
                    temp_dates.append(self.dates[k-1])
        self.data = temp_data
        self.dates = temp_dates
        self.datenums = [dateutil.parser.parse(s) for s in self.dates]
        self.t = 4

    def quartertoannual(self,method='AVG'):

        '''Converts quaterly data to annual using one of three methods:

            AVG : average of three months (default)
            SUM : sum of three months
            END : third month value only

        '''

        if self.t !=4:
            print 'Warning: data frequency is not quarterly!'
        T = len(self.data)
        temp_data = self.data[0:0]
        temp_dates = self.datenums[0:0]
        if method =='AVG':
            for k in range(0,T):
                '''Annual data is the average of monthly data'''
                if (self.datenums[k].month == 1) and (len(self.datenums[k:])>3):
                    temp_data.append((self.data[k]+self.data[k+1]+self.data[k+2]+self.data[k+3])/4)  
                    temp_dates.append(self.dates[k])
        elif method=='SUM':
            for k in range(0,T):
                '''Annual data is the sum of monthly data'''
                if (self.datenums[k].month == 1) and (len(self.datenums[k:])>3):
                    temp_data.append(self.data[k]+self.data[k+1]+self.data[k+2]+self.data[k+3])  
                    temp_dates.append(self.dates[k])
        else:
            for k in range(0,T):
                if (self.datenums[k].month == 1) and (len(self.datenums[k:])>3):
                    '''Annual data is the end of month value'''
                    temp_data.append(self.data[k+3])  
                    temp_dates.append(self.dates[k])
        self.data = temp_data
        self.dates = temp_dates
        self.datenums = [dateutil.parser.parse(s) for s in self.dates]
        self.t = 1

    def monthtoannual(self,method='AVG'):

        '''Converts monthly data to annual data using one of three methods:

            AVG : average of three months (default)
            SUM : sum of three months
            END : third month value only

        '''

        if self.t !=12:
            print 'Warning: data frequency is not monthly!'
        T = len(self.data)
        temp_data = self.data[0:0]
        temp_dates = self.datenums[0:0]
        if method =='AVG':
            for k in range(0,T):
                '''Annual data is the average of monthly data'''
                if (self.datenums[k].month == 1) and (len(self.datenums[k:])>11):
                    temp_data.append((self.data[k]+self.data[k+1]+self.data[k+2]+ self.data[k+3] + self.data[k+4] + self.data[k+5] 
                        + self.data[k+6] + self.data[k+7] + self.data[k+8] + self.data[k+9] + self.data[k+10] + self.data[k+11])/12)  
                    temp_dates.append(self.dates[k])
        elif method =='SUM':
            for k in range(0,T):
                '''Annual data is the sum of monthly data'''
                if (self.datenums[k].month == 1) and (len(self.datenums[k:])>11):
                    temp_data.append((self.data[k]+self.data[k+1]+self.data[k+2]+ self.data[k+3] + self.data[k+4] + self.data[k+5] 
                        + self.data[k+6] + self.data[k+7] + self.data[k+8] + self.data[k+9] + self.data[k+10] + self.data[k+11]))
                    temp_dates.append(self.dates[k])
        else:
            for k in range(0,T):
                '''Annual data is the end of year value'''
                if (self.datenums[k].month == 1) and (len(self.datenums[k:])>11):
                    temp_data.append(self.data[k+11])
                    temp_dates.append(self.dates[k])
        self.data = temp_data
        self.dates = temp_dates
        self.datenums = [dateutil.parser.parse(s) for s in self.dates]
        self.t = 1


    def percapita(self,pop_type = 1,method = 'END'):

        '''Converts data to per capita (US) using one of two methods:

            pop_type == 1 : total population US population
            pop_type != 1 : Civilian noninstitutional population is defined as persons 16 years of
                            age and older

            method == 'AVG': uses average population over the period
            method != 'AVG': uses end of period population

        '''

        T = len(self.data)
        temp_data   = self.data[0:0]
        temp_dates  = self.dates[0:0]
        if pop_type ==1:
            populate= fred('POP')
        else:
            populate= fred('CNP16OV')
        T2 = len(populate.data)

        # Generate quarterly population data.
        if self.t == 4:
            if method == 'AVG':
                populate.monthtoquarter(method='AVG')
            else:
                populate.monthtoquarter(method='END')
            window_equalize([self,populate])

        # Generate annual population data.
        if self.t == 1:
            if method == 'AVG':
                populate.monthtoannual(method='AVG')
            else:
                populate.monthtoannual(method='END')
            window_equalize([self,populate])

        if self.t == 12:
            window_equalize([self,populate])
        
        # edit self attributes
        self.data = [a/b for a,b in zip(self.data,populate.data)]
        self.title = self.title+' Per Capita'
        self.unit = self.units+' Per Thousand People'

    def recessions(self):
        '''Method creates gray recession bars for plots. Should be used after a plot has been made but
            before either (1) a new plot is created or (2) a show command is issued.'''

        peaks =[
        '1857-06-01',
        '1860-10-01',
        '1865-04-01',
        '1869-06-01',
        '1873-10-01',
        '1882-03-01',
        '1887-03-01',
        '1890-07-01',
        '1893-01-01',
        '1895-12-01',
        '1899-06-01',
        '1902-09-01',
        '1907-05-01',
        '1910-01-01',
        '1913-01-01',
        '1918-08-01',
        '1920-01-01',
        '1923-05-01',
        '1926-10-01',
        '1929-08-01',
        '1937-05-01',
        '1945-02-01',
        '1948-11-01',
        '1953-07-01',
        '1957-08-01',
        '1960-04-01',
        '1969-12-01',
        '1973-11-01',
        '1980-01-01',
        '1981-07-01',
        '1990-07-01',
        '2001-03-01',
        '2007-12-01']

        troughs =[
        '1858-12-01',
        '1861-06-01',
        '1867-12-01',
        '1870-12-01',
        '1897-03-01',
        '1885-05-01',
        '1888-04-01',
        '1891-05-01',
        '1894-06-01',
        '1897-06-01',
        '1900-12-01',
        '1904-08-01',
        '1908-06-01',
        '1912-01-01',
        '1914-12-01',
        '1919-03-01',
        '1921-07-01',
        '1924-07-01',
        '1927-11-01',
        '1933-03-01',
        '1938-06-01',
        '1945-10-01',
        '1949-10-01',
        '1954-05-01',
        '1958-04-01',
        '1961-02-01',
        '1970-11-01',
        '1975-03-01',
        '1980-07-01',
        '1982-11-01',
        '1991-03-01',
        '2001-11-01',
        '2009-06-01']

        if len(troughs) < len(peaks):
            today = datetime.date.today()
            troughs.append(str(today))

        T = len(self.data)
        S = len(peaks)

        date_num    = pylab.date2num([dateutil.parser.parse(s) for s in self.dates])
        peaks_num   = pylab.date2num([dateutil.parser.parse(s) for s in peaks])
        troughs_num = pylab.date2num([dateutil.parser.parse(s) for s in troughs])

        datesmin = min(date_num)
        datesmax = max(date_num)
        peaksmin = min(peaks_num)
        peaksax = max(peaks_num)
        troughsmin=min(troughs_num)
        troughsmax=max(troughs_num)
        
        if datesmin <= peaksmin:
            'Nothing to see here'
            min0 = 0
        else:
            'Or here'
            for k in range(S):
                if datesmin <= peaks_num[k]:
                    min0 = k
                    break
                                              
        if datesmax >= troughsmax:
            max0 = len(troughs)-1
        else:
            'Or here'
            for k in range(S):
                if datesmax < troughs_num[k]:
                    max0 = k
                    break

        if datesmax < troughsmax:
            if peaks_num[max0]<datesmax and troughs_num[min0-1]>datesmin:
                peaks2 = peaks[min0:max0]
                peaks2.append(peaks[max0])
                peaks2.insert(0,self.dates[0])
                troughs2 = troughs[min0:max0]
                troughs2.append(self.dates[-1])
                troughs2.insert(0,troughs[min0-1])
            
                peaks2num  = pylab.date2num([dateutil.parser.parse(s) for s in peaks2])
                troughs2num = pylab.date2num([dateutil.parser.parse(s) for s in troughs2])

            elif peaks_num[max0]<datesmax and troughs_num[min0-1]<datesmin:
                peaks2 = peaks[min0:max0]
                peaks2.append(peaks[max0])
                troughs2 = troughs[min0:max0]
                troughs2.append(self.dates[-1])
            
                peaks2num  = pylab.date2num([dateutil.parser.parse(s) for s in peaks2])
                troughs2num = pylab.date2num([dateutil.parser.parse(s) for s in troughs2])

            elif peaks_num[max0]>datesmax and troughs_num[min0]>datesmin:
                peaks2 = peaks[min0:max0]
                peaks2.insert(0,self.dates[0])
                
                troughs2 = troughs[min0:max0]
                troughs2.insert(0,troughs[min0-1])
                
                peaks2num  = pylab.date2num([dateutil.parser.parse(s) for s in peaks2])
                troughs2num = pylab.date2num([dateutil.parser.parse(s) for s in troughs2])


            else:
                peaks2 = peaks[min0:max0+1]
                troughs2 = troughs[min0:max0+1]
                peaks2num  = peaks_num[min0:max0+1]
                troughs2num= troughs_num[min0:max0+1]


        else:
            if peaks_num[max0]>datesmax and troughs_num[min0]>datesmin:
                peaks2 = peaks[min0:max0]
                peaks2.insert(0,self.dates[0])
                troughs2 = troughs[min0:max0]
                troughs2.insert(0,troughs[min0+1])
        
                peaks2num  = pylab.date2num([dateutil.parser.parse(s) for s in peaks2])
                troughs2num = pylab.date2num([dateutil.parser.parse(s) for s in troughs2])

            else:
                peaks2 = peaks[min0:max0+1]
                troughs2 = troughs[min0:max0+1]
                peaks2num  = peaks_num[min0:max0+1]
                troughs2num= troughs_num[min0:max0+1]

        self.pks = peaks2
        self.trs = troughs2
        self.recess_bars = pylab.plot()
        self.peaks = peaks
        
        for k in range(len(peaks2)):
            pylab.axvspan(peaks2num[k], troughs2num[k], edgecolor= '0.5', facecolor='0.5', alpha=0.5)


def quickplot(x,year_mult=10,show=True,recess=False,save=False,name='file',width=2):

    '''Create a plot of a FRED data series'''

    fig = pylab.figure()

    years  = pylab.YearLocator(year_mult)
    ax = fig.add_subplot(111)
    ax.plot_date(x.datenums,x.data,'b-',lw=width)
    ax.xaxis.set_major_locator(years)
    ax.set_title(x.title)
    ax.set_ylabel(x.units)
    fig.autofmt_xdate()
    if recess != False:
        x.recessions()
    ax.grid(True)
    if show==True:
        pylab.show()
    if save !=False:
        fullname = name+'.png'
        fig.savefig(fullname,bbox_inches='tight')

def window_equalize(fred_list):

    '''Takes a list of FRED objects and adjusts the date windows for each to the smallest common window.'''

    minimums = [ k.datenums[0].date() for k in fred_list]
    maximums = [ k.datenums[-1].date() for k in fred_list]
    win_min =  max(minimums).strftime('%Y-%m-%d')
    win_max =  min(maximums).strftime('%Y-%m-%d')
    windo = [win_min,win_max]
    for x in fred_list:
        x.window(windo)

def date_numbers(date_strings):

    '''Converts a list of date strings in yyy-mm-dd format to date numbers.'''
    datenums = [dateutil.parser.parse(s) for s in date_strings]
    return datenums

def toFRED(data,dates,title=None,t=None,season=None,freq=None,source=None,units=None,daterange=None,idCode=None,updated=None):
    '''function for creating a FRED object from a set of data.'''
    f = fred()
    f.data = data
    f.dates = dates
    f.datenums = [dateutil.parser.parse(s) for s in f.dates]
    f.title = title
    f.t = t
    f.season = season
    f.freq = freq
    f.source = source
    f.units = units
    f.daterange = daterange
    f.idCode = idCode
    f.updated = updated
    return f