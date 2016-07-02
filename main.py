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

class lapDataProcessing:
    def processGPSData(self, gpsSentence):
        # $GPRMC,hhmmss.sss,A,GGMM.MM,P,gggmm.mm,J,v.v,b.b,ddmmyy,x.x,n,m*hh<CR><LF>
        if (gpsSentence[3:5] != "RMC"): # break if string is not RMC
            return 0
