import Adafruit_ADS1x15
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.interpolate import interp1d

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 2
sps = [64,128,250,475,860]    
frequency = input("Input sampling frequency (Hz):     ")    # Get sampling frequency from user
#    sps = input("Input sps (Hz) :     ")                        # Get ads1115 sps value from the user
time1 = input("Input sample time (seconds):     ")          # Get how long to sample for from the user

# Function to print sampled values to the terminal
def logdata():

#    print "sps value should be one of: 8, 16, 32, 64, 128, 250, 475, 860, otherwise the value will default to 250"
    print ("sps value = "+ str(y))
        
    period = 1.0 / frequency        # Calculate sampling period

    datapoints = int(time1*frequency)       # Datapoints is the total number of samples to take, which must be an integer
    dataarray=np.zeros([datapoints,2])      # Create numpy array to store value and time at which samples are taken
    adc.start_adc_difference(0,gain=GAIN,data_rate=y)   # Begin continuous conversion on input A0
##    adc.start_adc_difference(0,gain=GAIN,data_rate=sps)   # Begin continuous conversion on input A0
#    adc.start_adc(0,gain=GAIN,data_rate=sps)   # Begin continuous conversion on input A0
    
#    print "Press ENTER to start sampling"   
#    raw_input()

    startTime=time.time()                   # Time of first sample
    t1=startTime                            # T1 is last sample time
    t2=t1                                   # T2 is current time
    
    for x in range (0,datapoints) :         # Loop in which data is sampled
            
            dataarray[x,0]= adc.get_last_result()          # Get the result of the last conversion from the ADS1115 and store in numpy array
##            dataarray[x,0]= adc.read_adc_difference(0,gain=GAIN,data_rate=y)          # Get the result of the last conversion from the ADS1115 and store in numpy array
            dataarray[x,1] = time.time()-startTime          # Store the sample time in the numpy array

            while (t2-t1 < period) :        # Check if t2-t1 is less then sample period, if it is then update t2
                t2=time.time()              # and check again       
            t1+=period                      # Update last sample time by the sampling period
    adc.stop_adc()               
    return (dataarray)

for y in sps:

    dataSamples = logdata()                     # Call function to log data

#printchoice=raw_input("Do you want to save data to CSV (Y/N): ")    # Ask user if they want to save sampled values

#if (printchoice == "Y" or "y") :
#        np.savetxt('dataSamples.txt',dataSamples, fmt='%.3f', delimiter = ',')  # Save dataSamples to the file 'dataSamples.txt' using comma separated values


# Calculate time between succesive samples, store in sampleIntervals array

    number_samples = len(dataSamples)                 # Number of samples taken
    print(number_samples)
    sampleIntervals = np.zeros(number_samples-1)    # Create numpy array of length equal to the number of samples taken

    for i in range(0, number_samples-1):        # Store time difference between sample i and sample i+1 in each element of the sampleIntervals array
        sampleIntervals[i]=dataSamples[i+1,1]-dataSamples[i,1]

    plt.figure()
##    plt.figure(1)
##    plt.subplot(211)
#plt.plot(dataSamples[:,0])
#plt.subplot(212)
#plt.plot(sampleIntervals)


    factor=1

    tth = np.linspace(0,float(number_samples-1)/frequency,number_samples)
    f = interp1d(tth,dataSamples[:,0])
#    f = signal.resample(dataSamples[:,0],number_samples)
##    f = dataSamples[:,0]

##    xnew = np.linspace(0, number_samples, number_samples, endpoint=False)    
    g=signal.decimate(f(tth),factor,ftype='iir',zero_phase=True)
    xg = np.linspace(0,number_samples,number_samples/factor,endpoint=False)
    plt.plot(dataSamples[:,0],'go-',f(tth),'.-',xg,g,'ro-')

#    plt.show()
    plt.savefig(str(y))
