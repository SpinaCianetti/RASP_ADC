import numpy
from obspy.core import Trace,Stream,UTCDateTime

# Import the ADS1x15 module.
import Adafruit_ADS1x15
# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()
# Note you can change the I2C address from its default (0x48), and/or the I2C
# bus by passing in these optional parameters:
#adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)
# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1
sps = 250        #samples per second

time = 10
datapoints = 2000
sampling = 1/(time/float(datapoints))
print sampling

data=numpy.zeros([datapoints],dtype=numpy.int16)

starttime=UTCDateTime()
adc.start_adc_difference(0,gain=GAIN,data_rate=sps)

for x in range (datapoints):
#	sample = adc.read_adc_difference(0, gain=GAIN)
	sample = adc.get_last_result()
	data[x]=sample
	timenow=UTCDateTime()
	#print sample,timenow
adc.stop_adc()

stats= {'network': 'TV',
		'station': 'RASPI',
		'location': '00',
		'channel': 'BHZ',
		'npts': datapoints,
		'sampling_rate': sampling,
		'mseed' : {'dataquality' : 'D'},
		'starttime': starttime}

stream =Stream([Trace(data=data, header=stats)])

stream.write('test.mseed',format='MSEED',encoding='INT16',reclen=512)
stream.plot()
