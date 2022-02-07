import keyboard
import random
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
#import numpy as np

plt.style.use('fivethirtyeight')

x_vals = []
y_vals = []
a_vals = []


#Hardware
dac_bitwidth = 12
adc_bitwidth = 12
gain = 50

#Calibration Settings
max_bound = 2**adc_bitwidth - 1
min_bound = 1
lowBound = 2047 - 10
upperBound = 2047 + 10
length = 1
dacIncrement = 1023


#global variables
dt = 0
adc_val = 0
dac_val = 0
runCalibrate = True
runSensor = True
flag = 0
sensor_val = 0



def sensor(base, e, gf):
    noise = random.randint(-9,9) * .0001
    
    vref = 5
    r = gf * e * base
    vout = vref*(r/(base + r)) + noise
    return vout

def dac(inp, bitwidth):
    noise = random.randint(-9,9) * .0001
    
    vref = 5
    res = 2**bitwidth-1
    return inp * vref/res + noise

def adc(inp, bitwidth):
    noise = random.randint(-9,9)
    
    vref = 5
    res = 2**bitwidth-1
    
    Vout = int(inp * res/vref + noise)

    if(Vout < 0):
        return 0
    elif(Vout >= res):
        return res
    else:
        return Vout

def inamp(INp, INn, bias, gain):
    noise = random.randint(-9,9) * .0001
    Vmax = 5.5 - 0.05
    Vmin = 0.05
    Vout = (INp - INn)*gain + bias + noise

    if(Vout < Vmin):
        return Vmin
    elif(Vout > Vmax):
        return Vmax
    else:
        return Vout
    

def calibrate():

    global adc_val, runCalibrate, dac_val, dacIncrement, sensor_val, flag, dt
    
    while (runCalibrate):
        adc_val = adc(inamp(sensor_val, dac(dac_val, dac_bitwidth), 2.5, gain), adc_bitwidth)
        dt += 1

        #CHANGES THE DAC OUTPUT
        if(adc_val <= lowBound):
            dac_val -= dacIncrement
            flag = 0
        elif (adc_val >= upperBound):
            dac_val += dacIncrement
            flag = 1


        adc_val = adc(inamp(sensor_val, dac(dac_val, dac_bitwidth), 2.5, gain), adc_bitwidth)

        #CHECKS IF ADC READING IS WITHIN RANGE
        if((adc_val >= lowBound) and (adc_val <= upperBound)):
            runCalibrate = False
            print('Successfullly Calibrated')
        elif(dacIncrement == 0):
            dacIncrement += 1


        #CHANGES DAC INCREMENT
        if((adc_val <= lowBound) and (flag == 1)):
            dacIncrement = int(dacIncrement * .5)
        elif((adc_val >= upperBound) and (flag == 0)):
            dacIncrement = int(dacIncrement * .5)

        #print(adc(inamp(sensor_val, dac(dac_val, dac_bitwidth), 2.5, gain), adc_bitwidth))
        #print(dacIncrement)
        time.sleep(.1)

def sensorReading():
    global sensor_val, dt

    while True:
        sensor_val = sensor(100, length, 1)
        dt += 1
        time.sleep(.001)
    

def check_key():
    global run, length, runCalibrate, dacIncrement, runSensor, sensor_val, dac_val, dt

    while True:
        if keyboard.is_pressed('9'):
            length -= .01
            print(length)
            time.sleep(.2)
        elif keyboard.is_pressed('0'):
            length += .01
            print(length)
            time.sleep(.2)
        elif keyboard.is_pressed('1'):
            runCalibrate = True
            calibrate()
            dacIncrement = 200
            time.sleep(.2)
        else:
            print('inamp volt: ', inamp(sensor_val, dac(dac_val, dac_bitwidth), 2.5, gain))
            print('sensor volt: ', round(float(sensor_val), 2))
            print('length: ', length)
            print(dac_val)
            print('')
            time.sleep(.1)

t1 = threading.Thread(target=check_key)
t2 = threading.Thread(target=sensorReading)


def animate(i):
    global sensor_val, dt
    
    x_vals.append(dt)
    y_vals.append(round(float(sensor_val), 5))  #sensor voltage
    a_vals.append(round(float(inamp(sensor_val, dac(dac_val, dac_bitwidth), 2.5, gain)), 5)) #inamp voltage

    plt.cla()
    plt.plot(x_vals, y_vals, label = "sensor")
    plt.plot(x_vals, a_vals, label = "inamp")
    plt.ylabel('volt')


dac_bitwidth = int(input('Enter DAC Bitwidth: '))
adc_bitwidth = int(input('Enter ADC Bitwidth: '))
gain = int(input('Enter IN-AMP Gain: '))

      
t1.start()
t2.start()
ani = FuncAnimation(plt.gcf(), animate, interval=10)
plt.tight_layout()
plt.show()





