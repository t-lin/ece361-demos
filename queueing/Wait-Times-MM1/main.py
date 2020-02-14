'''
Simulates an M/M/1 queueing system using Lindley's equation.
Assumes an infinite queue (i.e. packets are never dropped).
Calculates the empirical CDF from using Lindley's to the theoretical CDF.

Click the "run" button up top to run the simulation. The output plots
will appear in the list of files on the left.

Input parameters (see INPUT PARAMS below):
    - Number of packets received by the queueing system
    - Long term average arrival rate of packets (per second)
    - Long term average service rate for packets (per second)

Output plots:
    - Comparison of empirical vs theoretical CDFs of M/M/1
    - Packets in system (waiting or being serviced) at a given time
    - Total wait time (waiting or being serviced) of each packet

Author: Thomas Lin (t.lin@mail.utoronto.ca) 2018
'''
# INPUT PARAMS
numPackets = 1000 # Integer number
arrRate = 0.5 # Packet arrival rate
servRate = 1 # Packet service rate
# END INPUT PARAMS

# Library imports
import sys
from random import expovariate
from math import exp, ceil
import numpy as np

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

print "Simulating %s packets in M/M/1 system" % numPackets
print "Average arrival rate = %s; and average service rate = %s" % (arrRate, servRate)

# Initialize figure
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)

# Convert to float (in case integer was entered)
arrRate = float(arrRate)
servRate = float(servRate)

interArrivals = [expovariate(arrRate) for i in range(numPackets)]
serviceTimes = [expovariate(servRate) for i in range(numPackets)]

# Simulate using Lindley's
# Lindley's equation: W(n) = max(0, W(n - 1) + serviceTime(n - 1) - interArrivalTime(n))
waitTimes = [0] * numPackets
for i in range(1, numPackets):
    waitTimes[i] = max(0, waitTimes[i - 1] + serviceTimes[i - 1] - interArrivals[i])

# M/M/1 CDF equation: F(t) = 1 - ( (arrRate / servRate) * exp(-(servRate - arrRate) * t) )
numVals = int( ceil(max(waitTimes)) / 0.1 ) # Step size of 0.1
x_range = [i / 10.0 for i in range(numVals)]

theorWaitTimes = [0] * numVals
for i in range(numVals):
    theorWaitTimes[i] = 1 - ( arrRate / servRate * exp(-(servRate - arrRate) * x_range[i]) )


print "\nPlotting figures ... please wait"

# Plot CDFs
# NOTE: Using matplotlib's histogram to generate CDF results in last point y = 0
#       Hacky workaround is to delete the last point: ret[2][0].set_xy(ret[2][0].get_xy()[:-1])
numBins = 10000 if numPackets > 10000 else numPackets
ret = ax.hist(waitTimes, numBins, density=True,
                cumulative=True, histtype='step',
                label="Empirical (from Lindley's)", linewidth=2.0)
ret[2][0].set_xy(ret[2][0].get_xy()[:-1])

ax.plot(x_range, theorWaitTimes, label="Theoretical", linewidth=2.0)
ax.legend(loc='right')
plt.grid()
plt.xlabel("Waiting Time (s)")
plt.title("Empirical and Theoretical Waiting Time CDF for M/M/1 System")

fig.savefig('empirical-vs-theoretical.png')
#plt.show()


# Plot packets in system
# Logically, PacketsInSystem(t) = ArrivalEmpEnv(t) - DepartureEmpEnv(t)
# Split time into discrete number of intervals (max 10000) and calculate backlog for each
arrEmpEnv = np.cumsum(interArrivals)
departEmpEnv = [arrEmpEnv[i] + waitTimes[i] for i in range(numPackets)]

numPoints = 10000 if numPackets > 10000 else numPackets
timeInterval = max(departEmpEnv) / numPoints
pktInSys = [0] * numPoints
arrIndex = 0
departIndex = 0
for i in range(numPoints):
    intervalEnd = timeInterval * (i+1)

    for arrIndex in range(arrIndex, numPackets):
        if arrEmpEnv[arrIndex] > intervalEnd:
            break;

    for departIndex in range(departIndex, numPackets):
        if departEmpEnv[departIndex] > intervalEnd:
            break;

    numArrivals = arrIndex - 1 if arrIndex > 0 else 0
    numDepartures = departIndex - 1 if departIndex > 0 else 0
    pktInSys[i] = numArrivals - numDepartures

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)
ax.plot([i * timeInterval for i in range(numPoints)], pktInSys,
        label="Packets in System", drawstyle='steps', linewidth=2.0)
ax.legend(loc='right')
plt.grid()
plt.xlabel("Time (s)")
plt.ylabel("Packets in System")
plt.title("Packets Waiting or being Processed vs Time")

fig.savefig('pkts-in-system.png')


# Plot per-packet wait time
# Bar plots get exponentially slow when number of points is large (over ~1000), so let's switch to "fill"
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)
if numPackets > 1000:
    waitTimes.append(0) # To close the polygon for "fill" to work
    ax.fill(range(numPackets + 1),
            waitTimes, '.',
            label="Wait Time", linewidth=2.0)
else:
    ax.bar(range(1, numPackets + 1),
            waitTimes,
            label="Wait Time", linewidth=0.5)
ax.legend(loc='right')
plt.grid()
plt.xlabel("i-th Packet")
plt.ylabel("Time (s)")
plt.title("Total Wait Times (Queuing + Service) per Packet")

fig.savefig('pkts-wait-time.png')

print "Finished plotting all figures!"
