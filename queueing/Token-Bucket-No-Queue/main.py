'''
Simulates a token bucket traffic shaper w/ no queue (i.e. packets
are dropped if no token is available).
Note: In this version of the algorithm, each token = 1 packet.

Click the "run" button up top to run the simulation.

Input parameters (see INPUT PARAMS below):
    - Number of packets received by the shaper
    - Long term average arrival rate of packets (per second)
    - Token generation rate of the token bucket algorithm (per second)
    - Bucket size of token bucket algorithm

Output:
    - Simply prints the number of packets dropped by the system

Author: Thomas Lin (t.lin@mail.utoronto.ca) 2018
'''
# INPUT PARAMS
numPackets = 10000 # Integer number
arrRate = 350 # Packet arrival rate
tokenRate = 350 # Token generation rate
bucketSize = 2 # Max tokens in bucket
# END INPUT PARAMS

# Library imports
from random import expovariate

print "Simulating %s packets arriving at avg. rate %s" % (numPackets, arrRate)
print "Token generation rate of %s and max bucket size of %s" % (tokenRate, bucketSize)

interArrivals = [expovariate(arrRate) for i in range(numPackets)]

numTokens = 0
dropCount = 0

for i in range(numPackets):
    numTokens = min(numTokens + tokenRate * interArrivals[i], bucketSize)

    if numTokens >= 1:
        # Can transmit packets
        numTokens -= 1
    else:
        # No available token; Drop packet
        dropCount += 1

print
print "Number of packets dropped: %s" % dropCount


