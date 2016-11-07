#!/usr/bin/env python
# -*- coding: utf-8 -*-
####################################################
# This is a program switching off electric kettle  #
# using Energenie RC socket when water temperature #
# reaches 80 centegree and is good for brewing     #
# green tea. Single pund sign "#" denotes comments #
# while double pound signs "##" commnts out print  #
# stateents that might be useful for debugging     #
####################################################
# this program calls for major improvement,
# where separate thread will be taking temperature measures
# and the rest will be done in other thread


import time
import sys
import TeaCookBook as TCB

sys.path.insert (0, '/home/pi/Programy/pyenergenie-master/src/')
import RC_socket

# swich on electric socket
RC_socket.switch(1,"on")

# get rid of potential wrong first temperature reading
# (my sensor shows 85 on a firstreading when plugged before boot)
try:
    get_rid_of_first_reading_quietly = TCB.read_temperature ()
except IOError, e:
    print "Houston, mamy problem! Nie widze termometru. A dokladniej, to: \n"
    print e
    raw_input ("press button and RUUUUUUUUUUUUUUUUUUUN!!!!!!!!!")
    quit()
print "Temperature probe detected :)))"

# when to stop the kettle
target_1 = 77
# get pointzero for time reading
T_zero=time.time()
# load vectors with first readings of temperature (y) time(x) and count of measurements (i) (for a and b calculation to make sense in the following loop
y=[TCB.read_temperature()]
x=[time.time()-T_zero]
i=1
# Start gathering readings and feed-back to the user

while y[-1] < target_1:
    time.sleep (0.96)
    y.append (TCB.read_temperature())
    x.append (time.time()-T_zero)
    a, b = TCB.basic_linear_regression(x[i-15:], y[i-15:])

    ReminingTime = TCB.ReminingTime (y[-1], target_1, a)
##    print ("a and b ", a, b)
##    print ("x and y ", x , y)
##    print ("ReminingTime ", ReminingTime)
    print "Water will be ready in " + ReminingTime + "; Current temperature: " + str(y[-1])

# Water is ready

RC_socket.switch(1,"off")
print "\nWater Reeady!!!"


# Look at temperature changes to spot the moment the probe is removed from the kettle

# using measures from the boiling phase take 20 temperature differences between measures from last 21 measurements
#### testing new option #### last20tempDiff = [i_th-j_th for i_th, j_th in zip(y[i-21:-1], y[i-20:])] 
last20tempDiff = [i_th-j_th for i_th, j_th in zip(y[-21:-1], y[-20:])] #use 20 elements; _th is to distinguish beteween variable i = len(x) and indicators (i nd j) used in this loop here.
# now get the standard deviation for those readings (benchmark)
squares = map (lambda var_y: var_y**2, last20tempDiff)
StDev = (sum(squares)/20.0 - (sum (last20tempDiff)/20.0)**2)**(1/2.0)
##print "Bencmark StDev is" + str (StDev)
# In case StDev is to small, I will set the minimum at 0.1
StDev = max (0.1, StDev)

# To know if the probe is still in a kettle, monitor temperature change between measures
# You expect those differences to be fairly similar
# So if you suddenly see unusualy large drop in temperature, that means the probe was taken out.

temp1 = TCB.read_temperature() # first reading
##print "Temperatura: " + str(temp1)
time.sleep (1)
temp2 = TCB.read_temperature() # second reading
##print "Temperatura: " + str(temp2)
time.sleep (1)
temp3 = TCB.read_temperature() # third reading
##print "Temperatura: " + str(temp3)
time.sleep (1)

# with 3 measures we can now see if temperature change is steady: (T3-T2) = (T2-T1)
# or maybe temperature dropped suddenly: (T3-T2) << (T2-T1)
temperature_change_deviation = (temp3 - temp2) - (temp2 - temp1)
##print "Current deviation is" + str(temperature_change_deviation)
while abs(temperature_change_deviation)/5.0 <  StDev or temp3 > temp2:
    temp1 = TCB.read_temperature() # first measure
    time.sleep (1)
    print "Current deviation is " + str(temp1 - 2*temp3 +temp2) + " Temp: " + str(temp1)

    if abs (temp1 - 2*temp3 +temp2)/5.0 > StDev and temp1 < temp3:
        break
    temp2 = TCB.read_temperature() # first measure
    time.sleep (1)
    print "Current deviation is " + str(temp2 - 2*temp1 +temp3) + " Temp: " + str(temp2)

    if abs (temp2 - 2*temp1 +temp3)/5.0 > StDev and temp2 < temp1:
        break
    temp3 =TCB.read_temperature()
    temperature_change_deviation = temp3 - 2*temp2 + temp1
    time.sleep (1)
    print "Current deviation is" + str(temperature_change_deviation) + " Temp: " +str (temp3)


print "Probe removed from the kettle" ##+ "Benchmark StDev = " + str(StDev)

# using the same method as above - check when probe is inserted into hot tea.
temp1 = TCB.read_temperature() # first measure
##print "Temperatura: " + str(temp1)
time.sleep (1)
temp2 = TCB.read_temperature() # second measure
##print "Temperatura: " + str(temp2)
time.sleep (1)
temp3 = TCB.read_temperature() # third measure
##print "Temperatura: " + str(temp3)
time.sleep (1)
temperature_change_deviation = (temp3 - temp2) - (temp2 - temp1) #fluctuations in level of temp change between measurements
##print "Current deviation is" + str(temperature_change_deviation)

while abs(temperature_change_deviation)/5.0 < StDev or temp3<temp2:
    temp1 = TCB.read_temperature() # first measure
    time.sleep (1)
    ##print "Deviation is " + str (temp1 - 2*temp3 +temp2) + " Temp1 is " + str (temp1)
    print "Current Temperature is " + str (temp1)

    if abs (temp1 - 2*temp3 +temp2)/5.0 > StDev and temp1>temp3:
        break
    temp2 = TCB.read_temperature() # first measure
    time.sleep (1)
    ##print "Deviation is " + str(temp2 - 2*temp1 +temp3) + " Temp2 is " + str (temp2)
    print "Current Temperature is " + str (temp2)

    if abs (temp2 - 2*temp1 +temp3)/5.0 > StDev and temp2 > temp1:
        break
    temp3 = TCB.read_temperature() # third measure
    temperature_change_deviation = temp3 - 2*temp2 + temp1
    time.sleep (1)
    ##print "Deviation is " + str(temperature_change_deviation) + " Temp3 is " + str (temp3)
    print "Current Temperature is " + str (temp3)
# when probe is in the hot tea, start measuring prewing time  
BrewingStartTime = time.time()
print "Probe in your Tea "




#########################################
##  FAZA 3 - zaalarmowac, gdy herbata
##  gotowa do picia
#########################################


# all is basically kettle fase but upside-down, so temperature goes down to "drinkable" level
target_2 = 68
T_zero = time.time()
print "Please wait on minute whille temperature probe is calibrating"
i=1
x = [time.time()-T_zero]
y = [TCB.read_temperature()]
while i <=12: # Collect records for the first minute in a background while temperature probe still calibrates.
    y.append (TCB.read_temperature())
    x.append (time.time()-T_zero)    
    time.sleep(5)
    i+=1


while y[-1]>target_2 or a > 0:
    y.append (TCB.read_temperature())
    x.append (time.time()-T_zero)
    a, b = TCB.basic_linear_regression(x[-10:], y[-10:])

    BrewingTime = TCB.TimeAsText(BrewingStartTime)
    ReminingTime = TCB.ReminingTime(y[-1], target_2, a)     # TimeAsText(T, TransformOnly=True)
    print "Tea will be ready to drink in " + ReminingTime
    print "Brewing time so far is: " + BrewingTime
    print "Current temperature is: " + str(y[-1])
    time.sleep(5) #Cooling down takes much more time, so gaps are larger.

# Tea is ready now
TCB.TeaIsReady(T_zero)


