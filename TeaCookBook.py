# -*- coding: utf-8 -*-
import time

# temperature rader
def read_temperature ():
   tfile = open("/sys/bus/w1/devices/28-8000001efd57/w1_slave")
   reading = tfile.read()
   tfile.close()
   # extract temperature value from file content (extracted part is a string)
   temperature = float ((reading.split(" t=")[1]).split(" ")[0])/1000
   return temperature

# linear regression formula (I prefer not to import numpy for one simple formula)
def basic_linear_regression(x, y):
    length = float (len(x))
    sum_x = sum(x)
    sum_y = sum(y)
    sum_x_squared = sum(map(lambda a: a * a, x))
    sum_of_products = sum([x[i] * y[i] for i in range(int(length))])
    try:
        a = (sum_of_products - (sum_x * sum_y) / length) / (sum_x_squared - ((sum_x ** 2) / length))
    except ZeroDivisionError:
        a= 0.0
    b = (sum_y - a * sum_x) / length
    return a, b

# how long untill the tea is ready
def ReminingTime(current, target, a): #number of seconds before the tea is ready
    if a==0: ###-1/1800.0  < a < 1/1800.0:	# if a too close to zero, code seem to break, but TimeAsText might be a culprit actually
        return "never (temperature doesn't seem to change, or sensor is calibrating)"
    else:
        T = int ((target - current) / a)
        if T <0:
            return "never (temperature sensor is calibrating)"
        else:
            return TimeAsText(T, TransformOnly=True)

# show seconds since T0 in XXmin XXsec fromat
'''
TransformOnly allows to pass count of seconds for transformation (if True)
If TransformOnly is False, then program will substract T0 from current system time
To calculate number of seconds
'''
def TimeAsText(T0,TransformOnly=False):
    if TransformOnly == False:
        seconds = int (time.time() - T0 + 0.5)
    else : seconds = int(T0)
    nice_format = str( seconds//60) +"min "+ ("0"+str (seconds%60))[-2:] +"sec"
    return nice_format




   
# this function does not protect against an empty vector - x=[] will halt execution
def mean_var (x,square_x,i=None): #function of a vector, vector of squares and i as their length (optional)
		# Compute squares outside this function since I will use them over and over.
		# So every time I compute variance I would have my function to square a vector again.
		# Mean and variance need to be recalculated each time new result is observed
    if i is None: # Is this if necessary?
        i = len(x)
    get_mean_square = sum(square_x)/i
    get_mean = sum(x)/i
    get_variance = get_mean_square - get_mean
    return get_mean, get_variance



# Display tea brewing parameters when tea is ready to drink (temperature wise)
def TeaIsReady (BrewingStartTime):
    i=1
    BrewingTime = time.time() - BrewingStartTime
    Temp = int(read_temperature())
    while Temp > 35 or BrewingTime < 1200:
        time.sleep (0.75)
        BrewingTimeSec = time.time() - BrewingStartTime
        BrewingTime = TimeAsText (BrewingTimeSec, TransformOnly=True)
        Temp = int(read_temperature())
        print Tea_alert [(-1)**i]
        print ("Tea is ready. Current temperature is " + str(Temp) + "°C.\n\
Current brewing time is " + BrewingTime + ".\nTo stop the program, press Ctrl+c")
        i+=1
    print "Tea is too cold now. Good bye."


# Kind of nice looking graphical blinking sign for terminal
Tea_alert = {-1:"\n\
####################################################\n\
###                                              ###\n\
###   ########  ########    ##      ##  ##  ##   ###\n\
###   ########  ########   ####     ##  ##  ##   ###\n\
###      ##     ##        ##  ##    ##  ##  ##   ###\n\
###      ##     #####     ##  ##    ##  ##  ##   ###\n\
###      ##     #####     ##  ##    ##  ##  ##   ###\n\
###      ##     ##       ########   ##  ##  ##   ###\n\
###      ##     ##       ########                ###\n\
###      ##     ######## ##    ##   ##  ##  ##   ###\n\
###      ##     ######## ##    ##   ##  ##  ##   ###\n\
###                                              ###\n\
####################################################\n"
,
1:"\n\
####################################################\n\
####################################################\n\
######        ##        ####  ######  ##  ##  ######\n\
######        ##        ###    #####  ##  ##  ######\n\
#########  #####  ########  ##  ####  ##  ##  ######\n\
#########  #####     #####  ##  ####  ##  ##  ######\n\
#########  #####     #####  ##  ####  ##  ##  ######\n\
#########  #####  #######        ###  ##  ##  ######\n\
#########  #####  #######        ###################\n\
#########  #####        #  ####  ###  ##  ##  ######\n\
#########  #####        #  ####  ###  ##  ##  ######\n\
####################################################\n\
####################################################\n"
}


