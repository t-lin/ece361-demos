'''
Simulates a packet multiplexing system with two packet types.
Assumes an infinite queue (i.e. packets are never dropped).
Default settings (configurable in input parameters):
    - 25% of packets are 40 Bytes
    - 75% of packets are 1500 Bytes
    - Outgoing bandwidth of 100 Mbps
    - Ingress link utilization of 50%

Click the "run" button up top to run the simulation. The output plots
will appear in the list of files on the left.

Input parameters (see INPUT PARAMS below):
    - Number of packets received by the queueing system
    - Packet lengths of the two types (Bytes)
    - Distribution / proportion of traffic of both types (decimal number < 1)
    - Outgoing link bandwidth of the multiplexer (bits per second)
    - System utilization (decimal number < 1)

Output plots:
    - Empirical CDF of M/G/1
    - Packets in system (waiting or being serviced) at a given time
    - Total wait time (waiting or being serviced) of each packet

Author: Thomas Lin (t.lin@mail.utoronto.ca) 2018
'''
# INPUT PARAMS
numPackets = 10000 # Integer number
packetLengths = [40, 1500] # List of packet lengths
packetDistribution = [0.25, 0.75] # Proportion of packets
outgoingBW = 10**8 # Outgoing link bandwidth (bits per second)
rho = 0.5 # System utilization
# END INPUT PARAMS

# Library imports
import sys
from random import expovariate
from numpy.random import binomial
import numpy as np

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

# Sanity checks
assert sum(packetDistribution) == 1,\
    "Packet distributions must sum to 1"
assert len(packetLengths) == 2,\
    "Length of packetLengths list must be 2"
assert len(packetDistribution) == 2,\
    "Length of packetDistribution list must be 2"

print("Simulating %s packets in M/G/1 system" % numPackets)
print("Outgoing link bandwidth = %s bps" % outgoingBW)
print("System utilization = %s%%" % (rho * 100))
print("Packet distribution:")
print("\t- %s%% of packets with length %s Bytes" % (packetDistribution[0] * 100, packetLengths[0]))
print("\t- %s%% of packets with length %s Bytes" % (packetDistribution[1] * 100, packetLengths[1]))

# Initialize figure
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)

# Convert lengths to Bits and calculate service times
packetLengths = [i * 8 for i in packetLengths]
serviceTimes = [float(i) / outgoingBW for i in packetLengths]

avgPktLength = 0
for i in range(len(packetLengths)):
    avgPktLength += packetLengths[i] * packetDistribution[i]

# List of Bernouli RVs
# Flip coin once per trial, P(success) = packetDistribution[1], repeat numPackets trials
packetSizeIndex = binomial(1, packetDistribution[1], numPackets)

servRate = outgoingBW / avgPktLength # Avg. packet tx rate (mu)
arrRate = rho * servRate # lambda = rho * mu
interArrivals = [expovariate(arrRate) for i in range(numPackets)]

# Simulate using Lindley's
# Lindley's equation: W(n) = max(0, W(n - 1) + serviceTime(n - 1) - interArrivalTime(n))
# Note: Service time for packet i dependent on packetSizeIndex[i]
waitTimes = [0] * numPackets
for i in range(1, numPackets):
    waitTimes[i] = max(0, waitTimes[i - 1] + serviceTimes[packetSizeIndex[i - 1]] - interArrivals[i])


print("\nPlotting figures ... please wait")

# Plot CDF
# NOTE: Using matplotlib's histogram to generate CDF results in last point y = 0
#       Hacky workaround is to delete the last point: ret[2][0].set_xy(ret[2][0].get_xy()[:-1])
numBins = 10000 if numPackets > 10000 else numPackets
ret = ax.hist(waitTimes, numBins, density=True,
                cumulative=True, histtype='step',
                label="Empirical (from Lindley's)", linewidth=2.0)
ret[2][0].set_xy(ret[2][0].get_xy()[:-1])

ax.legend(loc='right')
plt.grid()
plt.xlabel("Waiting Time (s)")
plt.title("Empirical Waiting Time CDF for M/G/1 System")

fig.savefig('empirical-cdf.png')
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

print("Finished plotting all figures!")
