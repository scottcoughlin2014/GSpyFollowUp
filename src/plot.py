from matplotlib import use
use('agg')
from matplotlib import (pyplot as plt, cm)
import pdb
import numpy as np

import pandas
from gwpy.timeseries import TimeSeries

import ConfigParser
import optparse

def parse_commandline():
    """Parse the options given on the command-line.
    """
    parser = optparse.OptionParser()
    parser.add_option("--inifile", help="Name of ini file of params")
    parser.add_option("--pathToNoGlitch", help="Location of No Glitch data")
    parser.add_option("--pathToScratchy", help="Location of Scratchy data")
    parser.add_option("--verbose", action="store_true", default=False,help="Run in Verbose Mode")    
    parser.add_option("--pathToSaveASDvsANR", help="Location of where to save figure of ASD vs ANR")
    parser.add_option("--pathToSaveASDAvg", help ="Location of where to save figure of ASD average")
    opts, args = parser.parse_args()
    return opts    

opts = parse_commandline()

# ---- Create configuration-file-parser object and read parameters file.
cp = ConfigParser.ConfigParser()
cp.read(opts.inifile)
channelName = cp.get('channels','channelName')
numScratchy = cp.getint('parameters','numScratchy')
numNoGlitch = cp.getint('parameters','numNoGlitch')
duration = cp.getint('parameters','duration')
secpfft = cp.getint('parameters','secpfft')
overlap = cp.getfloat('parameters','overlap')


noglitchdf       = pandas.DataFrame.from_csv(opts.pathToNoGlitch)
scratchyglitchdf = pandas.DataFrame.from_csv(opts.pathToScratchy)

Scratchy10HzASD = []  
NoGlitch10HzASD = []
Scratchy10HzSNR = []
NoGlitch10HzSNR = []

badtime     = scratchyglitchdf.GPStime.iloc[0]
goodtime    = noglitchdf.GPStime.iloc[0]

gooddata    = TimeSeries.get(channelName,goodtime-duration/2,goodtime+duration/2)
baddata     = TimeSeries.get(channelName,badtime-duration/2,badtime+duration/2)

goodasdall    = gooddata.asd(secpfft,overlap)
badasdall     = baddata.asd(secpfft,overlap)

Scratchy10HzASD.append(badasdall.value[80])
NoGlitch10HzASD.append(goodasdall.value[80])
Scratchy10HzSNR.append(scratchyglitchdf.snr.iloc[0])
NoGlitch10HzSNR.append(noglitchdf.snr.iloc[0])


iT=1
for iTime in scratchyglitchdf.GPStime.iloc[1:numScratchy]:

    baddata = TimeSeries.get(channelName,iTime-duration/2,iTime+duration/2)
    Scratchy10HzASD.append(baddata.asd(secpfft,overlap).value[80])
    Scratchy10HzSNR.append(scratchyglitchdf.snr.iloc[iT])
    badasdall += baddata.asd(secpfft,overlap)
    
    print(iT)
    iT= iT+1

iT =1
for iTime in noglitchdf.GPStime.iloc[1:numNoGlitch]:
    gooddata = TimeSeries.get(channelName,iTime-duration/2,iTime+duration/2)
    NoGlitch10HzASD.append(gooddata.asd(secpfft,overlap).value[80])
    NoGlitch10HzSNR.append(noglitchdf.snr.iloc[iT])
    goodasdall += gooddata.asd(secpfft,overlap)
    print(iT)
    iT= iT+1


# Plot ASD verse SNR
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.scatter(NoGlitch10HzASD, NoGlitch10HzSNR, s=20, c='r', marker="s", label='No Glitch')
ax1.scatter(Scratchy10HzASD,Scratchy10HzSNR, s=20, c='b', marker="o", label='Scratchy')
ax1.set_xlabel('ASD at 10 Hz SUS-RM2_M1_DAMP_P')
ax1.set_ylim(7.5,15)
ax1.set_ylabel('omicron trigger SNR')
plt.legend(loc='upper left')
plt.savefig(opts.pathToSaveASDvsANR)

badasdall = badasdall/numScratchy
plot = badasdall.plot(label='Scratchy')
ax = plot.gca()
ax.set_xlabel('Frequency [Hz]')
ax.set_xlim(6,20)
ax.set_ylim(1e-6,10)
ax.grid(True,'both','both')
goodasdall = goodasdall/numNoGlitch
ax.plot(goodasdall,label='No Glitch')
plot.savefig(opts.pathToSaveASDAvg)

