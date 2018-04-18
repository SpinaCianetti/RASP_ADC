import numpy
from obspy.core import read,Trace,Stream,UTCDateTime
import Queue
from threading import Thread
import os.path
import subprocess
import time
from scipy import signal
from scipy.interpolate import interp1d

import Adafruit_ADS1x15
sps = 250        #samples per second
adc = Adafruit_ADS1x15.ADS1115()  #create class identifing model used
smoothing = 2   #this controls how much the values are smoothed, 1 is none , >1 is more smoothing
GAIN = 4
frequency = 50
period = 1.0 / frequency
deltaperiod = period*0.15

#this is how after how many samples a block is saved
#block_length=224
time1=1
block_length = int(time1*frequency)
#print block_length

#directories for data
mseed_directory = '/home/pi/RASP_ADC/mseed/'
os.system('rm '+mseed_directory+'*.mseed')

#declare the q from library
queue = Queue.Queue()


adc.start_adc_difference(0,gain=GAIN,data_rate=sps)

def read_data():
        value = 0
        startTime=time.time()                   # Time of first sample
        t1=startTime                            # T1 is last sample time
        t2=t1
#        t3=t1                                   # T2 is current time
        
        while True:
#                if ((t1-t3)/frequency>=0.1):
#                   t3=t2
#                   t2=t1
#                   print 'aggiorno'               # T3 aggiorno tempo
                #this array is for sample & sample_time
                packet=[]

#               sample = adc.readADCDifferential23(256, sps)*1000
#                sample = adc.read_adc_difference(0, gain=GAIN)
#                sample = adc.get_last_result()
#                timenow=UTCDateTime()
                
                #this smooths the value, removing high freq
#                value += (sample - value ) / smoothing

#                packet[0]=value
#                packet[1]=timenow
#                packet[0]=adc.get_last_result()
#                packet[1]=UTCDateTime()
                packet.append(adc.get_last_result())
                packet.append(t1)


                #print sample,timeno

                queue.put(packet)

                while ((t2-t1) <= period) : # Check if t2-t1 is less then sample period, if it is then update t2
                   t2=time.time() # and check again
                t1+=period                      # Update last sample time by the sampling period



def test_data():
        while True:
                if queue.qsize()>=block_length:

                        #one arrays for reading samples into
                        data=numpy.zeros([block_length],dtype=numpy.int16)

                        #this is the loop without storing jitter value and calcs
                        packet = queue.get()
                        data[0] = packet[0]
                        starttime = UTCDateTime(packet[1])
                        queue.task_done()

                        for x in range (1,block_length):
                                packet = queue.get()
                                data[x] = packet[0]
                                queue.task_done()

                        factor=1

##                        tth = numpy.linspace(0,float(block_length-1)/frequency,block_length)
##                        f = interp1d(tth,data)
##                        g = signal.decimate(f(tth),factor,ftype='iir',zero_phase=True)

        
                        samplingrate = 1 / (time1/float(block_length/factor))
#                        print(avg_samplingrate)
                        stats = {'network': 'TV', 'station': 'RASPI', 'location': '00',
                                        'channel': 'BHZ', 'npts': block_length/factor, 'sampling_rate': samplingrate, 
                                        'mseed': {'dataquality': 'D'},'starttime': starttime}
                        
                        sample_stream = Stream([Trace(data=data, header=stats)])
##                        sample_stream = Stream([Trace(data=g, header=stats)])

                        #write sample data
                        File = mseed_directory + str(sample_stream[0].stats.starttime.date) + '.mseed'
                        temp_file = mseed_directory + ".temp.tmp"
                        
                        if os.path.isfile(File):
                                #writes temp file, then merges it with the whole file, then removes file after
                                sample_stream.write(temp_file,format='MSEED',reclen=512)
 #                               sample_stream.write(mseed_directory +UTCDateTime.now().isoformat()+".mseed",format='MSEED',reclen=512)
                                subprocess.call("cat "+temp_file+" >> "+File,shell=True)
                                subprocess.call(["rm",temp_file])
                        else:
                        #if this is the first block of day
                                sample_stream.write(File,format='MSEED',reclen=512)
#                                sample_stream.write(File,format='MSEED',encoding='INT16',reclen=512)

                        


worker_sample = Thread(target=test_data)
#worker_sample = Thread(target=save_data)
worker_sample.start()

read_data()
