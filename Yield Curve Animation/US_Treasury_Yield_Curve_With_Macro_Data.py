'''This program creates .pm4 animation of the US Treasury yield curve from Jan. 1965 through Dec. 2013

Created by: Brian C Jenkins. Email comments and suggestions to bcjenkin@uci.edu. Version date: August 29, 2014.'''

from __future__ import division
import matplotlib
matplotlib.use("Agg")
import fredclass, urllib, dateutil, datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as dts
from yield_curve import yc

# Initial and final dates for video
date_alpha = '1965-01-01'
date_omega = '2013-12-31'
#date_omega = '2000-12-31'
win        = [date_alpha,date_omega]
dateT      = dateutil.parser.parse(date_omega)
t          = dateutil.parser.parse(date_alpha)
N          = 0
day        = datetime.timedelta(days =1)
dates, date_strs, maturities, yield_curves,masks = [],[],[],[],[]

# Create Fred objects
y1m= fredclass.fred('DTB4WK')
y3m= fredclass.fred('DTB3')
y6m= fredclass.fred('DTB6')
y1 = fredclass.fred('DGS1')
y5 = fredclass.fred('DGS5')
y10= fredclass.fred('DGS10')
y20= fredclass.fred('DGS20')
y30= fredclass.fred('DGS30')

y1m.window(win)
y3m.window(win)
y6m.window(win)
y1.window(win)
y5.window(win)
y10.window(win)
y20.window(win)
y30.window(win)

all_yields = [y1m,y3m,y6m,y1,y5,y10,y20,y30] 

gdp = fredclass.fred('GDPC1')
gdp.apc()
gdp.window(win)

cpi = fredclass.fred('CPIAUCSL')
cpi.apc()
cpi.window(win)

# Set up formatting for the movie files
Writer = animation.writers['ffmpeg']
writer = Writer(fps=50, metadata=dict(artist='Brian C Jenkins'), bitrate=50000)

# Initialize figure
fig = plt.figure(figsize=(16,9))
years    = dts.YearLocator(10)

ax1 = fig.add_subplot(2, 2, 1)
line1, = ax1.plot([], [], lw=4)
ax1.grid()
ax1.set_xlim(0,6)
ax1.set_ylim(0,18)
ax1.set_title('U.S. Treasury Bond Yield Curve',fontsize=18)
ax1.set_xticks(range(7))
ax1.set_yticks([2,4,6,8,10,12,14,16,18])
xlabels = ['1m','3m','6m','2y','5y','10y','30y']
ylabels = [2,4,6,8,10,12,14,16,18]
ax1.set_xticklabels(xlabels)
ax1.set_yticklabels(ylabels)
# ax1.set_xlabel('Time to Maturity',fontsize=20)
ax1.set_ylabel('%')#,fontsize=20)
#ax1.text(3.1125,.25, 'Created by Brian C Jenkins',fontsize=11, color='black',alpha=0.5)#,
ax1.text(3.75,.25, 'Created by Brian C Jenkins',fontsize=11, color='black',alpha=0.5)#,
date_text = ax1.text(0.125, 16.25, '',fontsize=18)

ax2 = fig.add_subplot(2, 2, 2)
ax2.plot_date(gdp.datenums,gdp.data,'r-',lw = 3)
line2, = ax2.plot_date([],[],'b-',lw = 3)
gdp.recessions()
ax2.set_ylabel('%')
ax2.set_title('Real GDP Growth',fontsize=18)
ax2.set_yticks([-6,-4,-2,0,2,4,6,8,10])
ylabels = [-6,-4,-2,0,2,4,6,8,10]
ax2.set_yticklabels(ylabels)
ax2.xaxis.set_major_locator(years)
ax2.grid()

ax3 = fig.add_subplot(2, 2, 3)
ax3.plot_date(cpi.datenums,cpi.data,'r-',lw = 3)
line3, = ax3.plot_date([],[],'b-',lw = 3)
cpi.recessions()
ax3.set_ylabel('%')
ax3.set_title('CPI Inflation',fontsize=18)
ax3.set_yticks([-2,-4,0,2,4,6,8,10,12,14,16])
ylabels = [-2,-4,0,2,4,6,8,10,12,14,16]
ax3.set_yticklabels(ylabels)
ax3.xaxis.set_major_locator(years)
ax3.grid()

ax4 = fig.add_subplot(2, 2, 4)
ax4.plot_date(y3m.datenums,y3m.data,'r-',lw = 3)
line4, = ax4.plot_date([],[],'b-',lw = 3)
y3m.recessions()
ax4.set_ylabel('%')
ax4.set_title('3-Month T-Bill Yield',fontsize=18)
ax4.set_yticks([0,2,4,6,8,10,12,14,16,18])
ylabels = [0,2,4,6,8,10,12,14,16,18]
ax4.set_yticklabels(ylabels)
ax4.xaxis.set_major_locator(years)
ax4.grid()




while t <= dateT:
	date, maturity, yield_curve, ymask = yc(t.strftime('%Y-%m-%d'),all_yields)
	while all(y =='NaN' for y in yield_curve):
		t +=day
		date, maturity, yield_curve, ymask = yc(t.strftime('%Y-%m-%d'),all_yields)
	dates.append(t)
	date_strs.append(date)
	maturities.append(maturity)
	yield_curves.append(yield_curve)
	masks.append(ymask)
	t+=day
	N+=1


k=0
def run(*args):
	global dates, date_strs,maturities, yield_curves,masks,k
	# print k
	maturity = maturities[k]
	yield_curve = yield_curves[k]
	ymask = masks[k]
   	line1.set_data(maturity[ymask], yield_curve[ymask])
   	line2.set_data([dates[k],dates[k]],[-6,10])
   	line3.set_data([dates[k],dates[k]],[-4,16])
   	line4.set_data([dates[k],dates[k]],[0,18])
	date_text.set_text(date_strs[k])
	k +=1
	return line1, date_text, line2, line3, line4


ani = animation.FuncAnimation(fig, run, N-1, blit=False,repeat=False,interval=1)
ani.save('US_Treasury_Yield_Curve_With_Macro_Data.mp4',writer=writer)
plt.show()



