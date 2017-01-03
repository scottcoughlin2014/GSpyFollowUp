from matplotlib import use
use('agg')
from matplotlib import (pyplot as plt, cm)
import pdb
import numpy as np

import pandas
from gwpy.timeseries import TimeSeries

noglitchdf       = pandas.DataFrame.from_csv('No_Glitch.csv')
scratchyglitchdf = pandas.DataFrame.from_csv('Scratchy_metadata_ML_H1_Selected.csv')
blipdf           = pandas.DataFrame.from_csv('Blip_metadata.csv')


Scratchy10HzASD = []  
NoGlitch10HzASD = []
Blip10HzASD     = []
Scratchy10HzSNR = []
NoGlitch10HzSNR = []
Blip10HzSNR     = []

numScratchy = 300
numNoGlitch = 100
numBlip     = 80
duration    = 120
secpfft     = 8
overlap     = 0.75

badtime     = scratchyglitchdf.GPStime.iloc[0]
goodtime    = noglitchdf.GPStime.iloc[0]
uncleartime = blipdf.GPStime.iloc[0]

gooddata    = TimeSeries.get('H1:SUS-RM2_M1_DAMP_P_IN1_DQ',goodtime-duration/2,goodtime+duration/2)
baddata     = TimeSeries.get('H1:SUS-RM2_M1_DAMP_P_IN1_DQ',badtime-duration/2,badtime+duration/2)
uncleardata = TimeSeries.get('H1:SUS-RM2_M1_DAMP_P_IN1_DQ',uncleartime-duration/2,uncleartime+duration/2)

goodasdall    = gooddata.asd(secpfft,overlap)
badasdall     = baddata.asd(secpfft,overlap)
unclearasdall = uncleardata.asd(secpfft,overlap)

Scratchy10HzASD.append(badasdall.value[80])
NoGlitch10HzASD.append(goodasdall.value[80])
Blip10HzASD.append(unclearasdall.value[80])
Scratchy10HzSNR.append(scratchyglitchdf.snr.iloc[0])
NoGlitch10HzSNR.append(noglitchdf.snr.iloc[0])
Blip10HzSNR.append(blipdf.snr.iloc[0])


iT=1
for iTime in scratchyglitchdf.GPStime.iloc[1:numScratchy]:

    baddata = TimeSeries.get('H1:SUS-RM2_M1_DAMP_P_IN1_DQ',iTime-duration/2,iTime+duration/2)
    Scratchy10HzASD.append(baddata.asd(secpfft,overlap).value[80])
    Scratchy10HzSNR.append(scratchyglitchdf.snr.iloc[iT])
    badasdall += baddata.asd(secpfft,overlap)
    
    print(iT)
    iT= iT+1

iT =1
for iTime in noglitchdf.GPStime.iloc[1:numNoGlitch]:
    gooddata = TimeSeries.get('H1:SUS-RM2_M1_DAMP_P_IN1_DQ',iTime-duration/2,iTime+duration/2)
    NoGlitch10HzASD.append(gooddata.asd(secpfft,overlap).value[80])
    NoGlitch10HzSNR.append(noglitchdf.snr.iloc[iT])
    goodasdall += gooddata.asd(secpfft,overlap)
    print(iT)
    iT= iT+1

iT =1
for iTime in blipdf.GPStime.iloc[1:numBlip]:
    uncleardata = TimeSeries.get('H1:SUS-RM2_M1_DAMP_P_IN1_DQ',iTime-duration/2,iTime+duration/2)
    Blip10HzASD.append(uncleardata.asd(secpfft,overlap).value[80])
    Blip10HzSNR.append(blipdf.snr.iloc[iT])
    unclearasdall += uncleardata.asd(secpfft,overlap)
    print(iT)
    iT= iT+1


# Plot ASD verse SNR
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.scatter(NoGlitch10HzASD, NoGlitch10HzSNR, s=20, c='r', marker="s", label='No Glitch')
ax1.scatter(Scratchy10HzASD,Scratchy10HzSNR, s=20, c='b', marker="o", label='Scratchy')
ax1.scatter(Blip10HzASD,Blip10HzSNR, s=20, c='k', marker="*", label='Blip')
ax1.set_xlabel('ASD at 10 Hz SUS-RM2_M1_DAMP_P')
ax1.set_ylim(7.5,15)
ax1.set_ylabel('omicron trigger SNR')
plt.legend(loc='upper left');
plt.savefig('/home/scoughlin/public_html/ScratchyFollowup/ASD_vs_ANR_Bp_S_NG.png')

badasdall = badasdall/numScratchy
plot = badasdall.plot(label='Scratchy')
ax = plot.gca()
ax.set_xlabel('Frequency [Hz]')
ax.set_xlim(6,20)
ax.set_ylim(1e-6,10)
ax.grid(True,'both','both')
goodasdall = goodasdall/numNoGlitch
ax.plot(goodasdall,label='No Glitch')
unclearasdall = unclearasdall/numBlip
ax.plot(unclearasdall,label='Blip')
plot.savefig('/home/scoughlin/public_html/ScratchyFollowup/ASDAverage_Bp_S_NG.png')

