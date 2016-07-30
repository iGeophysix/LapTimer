# This is Open Lap Timer project
# Hardware to use : Raspberri Pi, GPS, Two WebCams
# TO DO list:
# 1) make a class to process GPS data
# 1.1) store gps position + speed + azimuth
# 1.2) detect finish line crossing
# 1.3) make lap statistics
# 2) make a class to receive GPS data from Serial port
# 3)
###

import serial
from math import sin, cos, sqrt, atan2, radians,floor



class lapDataProcessing:
    gpsReceiver = None
    topSpeed = 0
    finishLineCoords = []
    trackName = "Somewhere"
    prevLat = 0.0
    prevLon = 0.0
    startTime = 0
    lapCatalogue = {
        'ADM Raceway': [55.564698,37.991055,55.564420,37.990999],
        'Firsanovka':[55.971814,37.255240,55.971925,37.254937],
        'KrekshinoRaceway':[55.587631, 37.100228,55.587420, 37.100162]
    }



    def __init__(self):
        self.gpsReceiver = None
        return None


    def processGPSData(self, gpsSentence):
        # $GPRMC,hhmmss.sss,A,GGMM.MM,P,gggmm.mm,J,v.v,b.b,ddmmyy,x.x,n,m*hh<CR><LF>
        if (gpsSentence[3:6] != "RMC"): # break if string is not RMC
            return 0,0
        gpsString = gpsSentence.split(",")
        #print gpsString

        fixType = gpsString[2]
        if fixType != 'A':
            return 0, 0

        day = int(gpsString[9][0:2])
        month = int(gpsString[9][2:4])
        year = int(gpsString[9][4:])
        hours   = int(gpsString[1][0:2])
        minutes = int(gpsString[1][2:4])
        seconds = float(gpsString[1][4:9])

        latitude = int(gpsString[3][0:2])+float(gpsString[3][2:])/60   #in dec degrees
        if (gpsString[4]=="S"):
            latitude = -latitude
        longitude = int(gpsString[5][0:3]) + float(gpsString[5][3:]) / 60  # in dec degrees
        if (gpsString[6] == "W"):
            longitude = -longitude
        speed = float(gpsString[7])*1.852  #in km/h
        azimuth = float(gpsString[8])


        if self.trackName != "Somewhere":
            latCross, lonCross = self.crossFinishLine([latitude,longitude, self.prevLat, self.prevLon], self.finishLineCoords)
            if (latCross != -1 and lonCross != -1):
                lapTime = self.getLapTime((hours*3600) + (minutes*60) + seconds)
                print("LAP", self.startTime, lapTime, gpsString[1])
                self.saveLapTime(self.getTrackName(), lapTime, day,month,year)
                self.saveRawDataToFile("run1.txt")

        rawData = [latitude, longitude, hours, minutes, seconds, day, month, year, speed]
        self.saveRawDataToFile("run1.txt", rawData)

        self.prevLat = latitude
        self.prevLon = longitude

        return latitude, longitude

    def getLapTime(self,currentTime):
        lapTime = currentTime - self.startTime
        print "Lap time =",lapTime, "Current time =", currentTime, "Start at =", self.startTime
        self.startTime = currentTime
        return lapTime

    def saveLapTime(self,track,time,day,month,year):
        f = open(track+".txt", "a")

        hours_part =   int(time / 3600)
        minutes_part = int((time - hours_part*3600)/ 60)
        seconds_part = time - hours_part*3600 - minutes_part*60



        string = "{track}\t{hh:02.0f}:{mm:02.0f}:{ss:02.3f} on {day:02d}/{month:02d}/{year:02d}\n" \
                    .format(track=track,hh=hours_part, mm=minutes_part, ss=seconds_part, day=day, month=month,year=year)

        f.write(string)
        f.close()

    def convertTime(self,decHours):


        time_hours = decHours
        time_minutes = time_hours * 60
        time_seconds = time_minutes * 60

        hours_part = floor(time_hours)
        minutes_part = floor(time_minutes % 60)
        seconds_part = floor(time_seconds % 60)

    def getDataFromGPS(self):
        gpsString = ""
        if self.gpsReceiver.isOpen() :
            gpsString = self.gpsReceiver.readline()
            #print gpsString
        return gpsString


    def connectGPS(self, path="/dev/ttyUSB0"):
        self.gpsReceiver = serial.Serial(path,115200)
        self.gpsReceiver.close()
        self.gpsReceiver.open()

    def crossFinishLine(self, cp = [-1.0,-1.0,-2.0,-3.0], fl=[0.0,0.0,10.0,10.0]): # cp - current Position, fl - finish line

        #print cp

        #A1 = y1_1 - y1_2
        A1 = fl[1] - fl[3]
        #B1 = x1_2 - x1_1
        B1 = fl[2] - fl[0]
        #C1 = x1_1 * y1_2 - x1_2 * y1_1
        C1 = fl[0] * fl[3]- fl[2]* fl[1]
        #A2 = y2_1 - y2_2
        A2 = cp[1] - cp[3]
        #B2 = x2_2 - x2_1
        B2 = cp[2] - cp[0]
        #C2 = x2_1 * y2_2 - x2_2 * y2_1
        C2 = cp[0] * cp[3] - cp[2]*cp[1]


        if B1 * A2 - B2 * A1 != 0:
            y = (C2 * A1 - C1 * A2) / (B1 * A2 - B2 * A1)
            x = (-C1 - B1 * y) / A1
            #print fl[0], x, fl[2], "\t", fl[1], y, fl[3]
            if min(cp[0], cp[2]) <= x and x <= max(cp[0], cp[2]) and \
                            min(cp[1], cp[3]) <= y and y <= max(cp[1], cp[3]) and \
                            min(fl[0], fl[2]) <= x and x <= max(fl[0], fl[2]) and \
                            min(fl[1], fl[3]) <= y and y <= max(fl[1], fl[3]):
                #print "LAP!", x, y
                return x,y
            else:
                return -1,-1
        # intervals are parallel
        if B1 * A2 - B2 * A1 == 0:
            return -1,-1
        return False

    def saveRawDataToFile(self,filename="test.txt",data=[0,0,0,0,0,0,0,0,0]):
        f = open(filename,"a")
        #string = "{track}\t{hh:02.0f}:{mm:02.0f}:{ss:02.3f} on {day:02d}/{month:02d}/{year:02d}\n" \
        #    .format(track=track, hh=hours_part, mm=minutes_part, ss=seconds_part, day=day, month=month, year=year)

        string = "{lat:02.10f}\t{lon:02.10f}\t{hh:02.0f}:{mm:02.0f}:{ss:02.3f}\t{day:02d}/{month:02d}/{year:02d}\t{speed:02.2f}\n" \
                .format(lat=data[0], lon=data[1],hh=data[2], mm=data[3], ss=data[4], day = data[5], month=data[6],year=data[7],speed=data[8])
        f.write(string)
        f.close()

    def defineFinishLine(self,latitude, longitude):
        minDist = 999999999

        # approximate radius of earth in km
        R = 6373.0

        lat1 = radians(latitude)
        lon1 = radians(longitude)

        for key, value in self.lapCatalogue.iteritems():

            lat2 = radians(value[0])
            lon2 = radians(value[1])

            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a)) * R


            if c < minDist:
                minDist = c
                self.trackName = key
                self.finishLineCoords = value


        return self.trackName

    def getTrackName(self):
        return self.trackName


moto = lapDataProcessing()
moto.connectGPS("/dev/cu.usbmodemFA131")
for i in range(4):
    gpsMsg = moto.getDataFromGPS()
lat,lon = moto.processGPSData(gpsMsg)
moto.defineFinishLine(lat,lon)
print "Welcome to " + moto.getTrackName()

while True:
    gpsMsg = moto.getDataFromGPS()
    moto.processGPSData(gpsMsg)

