from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

import matplotlib as mpl
import pylab
import sys
import csv
import Image

import subprocess

sys.dont_write_bytecode = True

#  jmLIBS
import rfiReachCalc as RFI

earthRad=            6371     # km
km_deg=              np.pi*2*earthRad
deg_km=              360.0/km_deg

dataFILE =           "../01fmListExtract/resultsWorld/worldDataCoverage.csv"
#dataFILE =           "../01fmListExtract/results/MEXCoverage.csv"

baseGRID =           "baseGRID.png"
baseSTATIONS =       "baseSTATIONS.png"
baseMASK =           "baseMASK.png"
baseCOLORSCALE =     "baseCOLORSCALE.png"
colorSTATIONS =      "colorSTATIONS.png"
mapRESULT =          "mapRESULT.png"

mRES = 'l'           # Map coastline resoluion
                     # c - crude    # l - low      # i - intermediate
                     # h - high     # f - full
dpiRES =             500
outDIMS =            40,20 
limitWest =          -180
limitEast =          180
limitNorth =         75
limitSouth =         -75

lineOfSight = RFI.lineOfSight(1200, 1200, R=6371, extend=4.0/3.0)

# Lat., Lon., Name
siteLabels =         [
                        [26.685937, -103.747155, 'Z. del S.']
                     ]

siteLabels =         [ ]


def cutColumn(array,columnIN):
   columnOUT = []
   for i in array:
      columnOUT.append(i[columnIN])
   return columnOUT


def callConsole(msg):
   p1 = subprocess.Popen(["dmesg"], stdout=subprocess.PIPE)
   p2 = subprocess.Popen([msg], stdin=p1.stdout, stdout=subprocess.PIPE, shell=True)
   p1.stdout.close()
   cnsResponde = p2.communicate()[0]
   cnsResponde = cnsResponde[:-1]
   p1.kill()
   return cnsResponde


def inegiTOdec(dataIN):
   DEG= np.trunc(dataIN/10000)
   MIN= np.trunc ((dataIN - (DEG*10000))/100)
   SEC= (dataIN - (DEG*10000) - (MIN*100))
   OUTPUT= DEG + (MIN/60.0) + (SEC/3600.0)
   return OUTPUT


def distance_dBm(pwrW, pwrRCVdbm, freqMHz):
   p6 = RFI.distance_dBm(pwrW/1000.0, pwrRCVdbm, freqMHz, G1=10.15, G2=1.28)
   return p6


def createMask(fileIN, maskOUT):
   cmd01    = "convert " + fileIN + " -negate " + maskOUT
   cmd02    = "convert " + maskOUT + " -level 0,01% " + maskOUT
   cmd03    = "convert " + maskOUT + " -negate " + maskOUT
   callConsole(cmd01)
   callConsole(cmd02)
   callConsole(cmd03)


def createColorScale(fileOUT):
   cmd00    = "convert "
   #     THIS IS VIRIDIS
   cmd00   += "xc:indigo "
   cmd00   += "xc:darkslateblue "
   cmd00   += "xc:steelblue "
   cmd00   += "xc:cadetblue "
   cmd00   += "xc:limegreen "
   cmd00   += "xc:yellow "

   #     THIS IS PLASMA
   #cmd00   += "xc:navy "
   #cmd00   += "xc:darkviolet "
   #cmd00   += "xc:fuchsia "
   #cmd00   += "xc:salmon "
   #cmd00   += "xc:darkorange "
   #cmd00   += "xc:yellow "

   cmd00   += "+append -filter Cubic -resize 600x30! -flop "
   cmd00   += fileOUT
   callConsole(cmd00)


def readStationsFmList(inFILE):
   data= csv.reader(open(inFILE), delimiter=",")
   data.next()

   power=[]
   latitude=[]
   longitude=[]
   frequency=[]

   # Read and match format
   i=1
   for col in data:
      # Frequency
      tmpFrecuencia=str(col[0])
      tmpFrecuencia = float(tmpFrecuencia)
      frequency.append(tmpFrecuencia)

      # Power (kW)
      tmpPotencia=str(col[1])
      tmpPotencia = float(tmpPotencia)*1000
      power.append(tmpPotencia)

      # On file: GGMMSS
      tmpLatitud=float(col[2])
      latitude.append(tmpLatitud)

      # On file: GGMMSS
      tmpLongitud=float(col[3])
      longitude.append(tmpLongitud)

      i=i+1

   return latitude, longitude, power, frequency

def plotStation(map, station, rad=10, limitRange=lineOfSight):

   r = rad*deg_km

   map.tissot( station['lon'], station['lat'], r, 100, facecolor='k',
               zorder=10, alpha=1.0)


def plotStations(outFile, rad=10):
   for i in range(len(longitude)):
      station = [longitude[i], latitude[i], power[i], frequency[i]]
      station = { 'lon': longitude[i], 'lat':latitude[i],\
                  'watts':power[i], 'freq':frequency[i]}
                  
      plotStation(my_map, station, rad)

   plt.savefig(outFile, dpi=dpiRES)


def configurePlot():
   global my_map
   # + + + Configuring plot + + +
   # High resolutions take longer
   fig = plt.figure()
   plt.axis([limitWest, limitEast, limitSouth, limitNorth])
   plt.axis('off')
   fig = mpl.pyplot.gcf()
   fig.set_size_inches(outDIMS)
   topright=   [  limitEast, limitNorth]
   bottomleft= [  limitWest, limitSouth]
   center=     [  (topright[0]+bottomleft[0])/2.0,
                  (topright[1]+bottomleft[1])/2.0]
   #stere, merc
   my_map = Basemap(projection='merc', lon_0=center[0], lat_0=center[1],
       resolution = mRES, area_thresh = 1.0,
       urcrnrlon=topright[0],    urcrnrlat=topright[1],
       llcrnrlon=bottomleft[0],  llcrnrlat=bottomleft[1])


def plotGrid():
   configurePlot()
   plt.title("FM broadcast stations", fontsize=40)
   plt.figtext(0.6,0.1,'With information from fmlist.org, \n \
         Jose M. Jauregui-Garcia, Edgar Castillo-Dominguez')
   my_map.drawcoastlines()
   my_map.drawcountries()
   my_map.fillcontinents(color='white')
   my_map.drawmapboundary()
   my_map.drawmeridians(np.arange(180, -180, -30), labels=[True,False,False,True])
   my_map.drawparallels(np.arange(-90, 90, 30), labels=[False,True,True,False])

   # Site labels
   if len(siteLabels) > 0:
      lats = cutColumn(siteLabels,0)
      lons = cutColumn(siteLabels,1)
      labels = cutColumn(siteLabels,2)

      x,y = my_map(lons, lats)

      for label, xpt, ypt in zip(labels, x, y):
         plt.text(xpt, ypt, label, va="top", ha="center")

      for i in range(0,len(lats)):
         lon = lons[i]
         lat = lats[i]
         x,y = my_map(lon, lat)
         my_map.plot(x, y, 'kx', markersize=3)

   #  Grid for MAP & change white to transparent
   plt.savefig(baseGRID, dpi=dpiRES)
   createMask(baseGRID, baseGRID)
   callConsole("convert " + baseGRID + " -transparent white " + baseGRID)
   plt.savefig(baseGRID, dpi=dpiRES)
   createMask(baseGRID, baseGRID)
   callConsole("convert " + baseGRID + " -transparent white " + baseGRID)



if __name__=="__main__":

   runNOW = True

   if runNOW:

      print "This MIGHT take a long time, you can go for coffee"

      print "\n+ + + Reading stations + + +"
      latitude, longitude, power, frequency = readStationsFmList(dataFILE)
      print "Stations readed"


      listDB=[10,50,100,150]

      # Plot stations
      for i in listDB:
         plt.clf()
         outName = 'm{0}.png'.format(-i)
         print outName

         configurePlot()
         plotStations(outName,i)

         # Convert images to truecolor
         cmd = 'convert ' + outName + ' -type truecolor ' + outName
         callConsole(cmd)

      # Grig plot
      plt.clf()
      plotGrid()

      # Average images
      fileListAverage= ''
      for i in listDB:
         plt.clf()
         outName = 'm{0}.png'.format(-i)
         fileListAverage = fileListAverage + outName + ' '
      cmd = 'convert ' + fileListAverage + '-evaluate-sequence mean '
      cmd+= baseSTATIONS
      callConsole(cmd)

      # Create mask
      createMask(baseSTATIONS, baseMASK)

      # Create colorscale
      createColorScale(baseCOLORSCALE)

      # Create color map
      # - Convert to color
      callConsole(   "convert " + baseSTATIONS + \
                     " -colorspace gray " + baseCOLORSCALE + \
                     " -clut " + colorSTATIONS)

      #  Mask stations and create stations layer
      callConsole(   "composite -compose Screen " + colorSTATIONS + " " + \
                     baseMASK + " " + colorSTATIONS)

      #  Overlay all data
      callConsole("composite " + baseGRID + " " + colorSTATIONS + " " + mapRESULT)

      #  Append bar
      callConsole("convert +append " + mapRESULT + " GradientScale.png " + mapRESULT)

      #  Convert to PDF
      callConsole("convert "+ mapRESULT + " " + mapRESULT[:-4] + ".pdf") 
