'''
Simulates a token bucket traffic shaper w/ infinite queue (i.e. packets are never dropped).
Note: In this version of the algorithm, each token = 1 packet.

Click the "run" button up top to run the simulation. The output plots
will appear in the list of files on the left.

Input parameters (see INPUT PARAMS below):
    - Number of packets received by the shaper
    - Long term average arrival rate of packets (per second)
    - Token generation rate of the token bucket algorithm (per second)
    - Bucket size of token bucket algorithm

Output plots:
    - Arrival vs departure empirical envelopes
    - CDFs of inter-packet arrival & departure times
    - Packets in system (waiting or being serviced) at a given time
    - Total wait time (waiting or being serviced) of each packet

Author: Thomas Lin (t.lin@mail.utoronto.ca) 2018
'''
####### INPUT PARAMS #######
numPackets = 1000 # Integer number
arrRate = 350 # Packet arrival rate
tokenRate = 350 # Token generation rate
bucketSize = 5 # Max tokens in bucket
##### END INPUT PARAMS #####

# Library imports
import sys
from random import expovariate
import numpy as np

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

print "Simulating %s packets arriving at avg. rate %s" % (numPackets, arrRate)
print "Token generation rate of %s and max bucket size of %s" % (tokenRate, bucketSize)

# Initialize figure
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)

interArrivals = [expovariate(arrRate) for i in range(numPackets)]
arrEmpEnv = np.cumsum(interArrivals)
departEmpEnv = [0] * numPackets

# Assume bucket was initially full
# Assume first packet was immediately transmitted upon arrival
departEmpEnv[0] = arrEmpEnv[0]
numTokens = bucketSize - 1
waitCount = 0

for i in range(1, numPackets):
    currTime = arrEmpEnv[i]
    dt = currTime - departEmpEnv[i - 1]

    numTokens = min(numTokens + tokenRate * dt, bucketSize)

    if numTokens >= 1:
        # Can transmit packets
        numTokens -= 1
        departEmpEnv[i] = currTime
    else:
        # No available token
        # Calculate time required to wait until we have 1 token
        dt = (1 - numTokens) / tokenRate
        departEmpEnv[i] = currTime + dt
        numTokens = 0

# Calculate inter-departure times
interDepartures = [0] * numPackets
for i in range(1, numPackets):
    interDepartures[i] = departEmpEnv[i] - departEmpEnv[i - 1]

print "\nPlotting figures ... please wait"

# Plot inter-packet time CDFs
# NOTE: Using matplotlib's histogram to generate CDF results in last point y = 0
#       Hacky workaround is to delete the last point: ret[2][0].set_xy(ret[2][0].get_xy()[:-1])
numBins = 10000 if numPackets > 10000 else numPackets
ret = ax.hist(interDepartures, numBins, density=True, cumulative=True, histtype='step', label="Inter-Departure Times", linewidth=2.0)
ret[2][0].set_xy(ret[2][0].get_xy()[:-1]) # Hack (see above)

ret = ax.hist(interArrivals, numBins, density=True, cumulative=True, histtype='step', label="Inter-Arrival Times", linewidth=2.0)
ret[2][0].set_xy(ret[2][0].get_xy()[:-1]) # Hack (see above)

ax.legend(loc='right')
plt.grid()
plt.xlabel("Inter-Packet Time (s)")
plt.title("Arrival vs Departure Inter-Packet Time CDF")

fig.savefig('interpacket-cdf.png')


# Plot empirical envelopes
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)
ax.plot(arrEmpEnv, range(numPackets), label="Arrivals", linewidth=2.0)
ax.plot(departEmpEnv, range(numPackets), label="Departures", linewidth=2.0)
ax.legend(loc='right')
plt.grid()
plt.xlabel("Time (s)")
plt.ylabel("Packet Count")
plt.title("Arrival vs Departure Empirical Envelopes")

fig.savefig('empirical-env.png')


# Plot packets in system
# Logically, PacketsInSystem(t) = ArrivalEmpEnv(t) - DepartureEmpEnv(t)
# Split time into discrete number of intervals (max 10000) and calculate backlog for each
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
# For each packet, it's just departure time - arrival time
# Bar plots get exponentially slow when number of points is large (over ~1000), so let's switch to "fill"
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)
packetWaitTimes = [departEmpEnv[i] - arrEmpEnv[i] for i in range(numPackets)]
if numPackets > 1000:
    packetWaitTimes.append(0) # To close the polygon for "fill" to work
    ax.fill(range(numPackets + 1),
            packetWaitTimes, '.',
            label="Wait Time", linewidth=2.0)
else:
    ax.bar(range(1, numPackets + 1),
            packetWaitTimes,
            label="Wait Time", linewidth=0.5)
ax.legend(loc='right')
plt.grid()
plt.xlabel("i-th Packet")
plt.ylabel("Time (s)")
plt.title("Total Wait Times (Queuing + Service) per Packet")

fig.savefig('pkts-wait-time.png')


print "Finished plotting all figures!"
