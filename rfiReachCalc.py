#!/usr/bin/python -d
# -*- coding: utf-8 -*-

#  Public libs
import sys
import numpy as np

sys.dont_write_bytecode = True         # Prevent pyc creation

def lineOfSight(h1, h2, R=6371, extend=4.0/3.0):
   r =   R * 1000
   r =   r * extend

   d1 =  np.sqrt( h1*(2*r+h1) ) 
   d2 =  np.sqrt( h2*(2*r+h2) ) 

   d1 =  0.001*d1
   d2 =  0.001*d2

   return d1+d2


#  Distance when a pwrKW transmitter is received with
#  pwrRCVdbm on freqMHz frequency
def distance_dBm(pwrKW, pwrRCVdbm, freqMHz, G1=13.17, G2=1.28):
   #  +PT   Transmitter power (dBm)
   #
   #  +G1   gain transmitter(dB)
   #        13.71 typ. broadcast
   #
   #  +G2   gain receiver (db)
   #        1.28 Lambda/4 monopole
   #
   #  -P2   -20 * m * log(MHz)
   #        m = power on frequency variation (2 for free space)
   #
   #  -P3   -32,44
   #
   #  +P4   +10 * log(p) polarization mismatch (1 perfect match)
   #
   #  +P5   +10 * log(q) impedance mismatch (1 perfect match)
   #
   #  -L1 (dB) loss by height (transmitter)
   #  -L2 (dB) loss by height (receiver)
   #  -L3 (db) Clear air absorption
   #  -L4 (db) Hydrometeor absorption (ie. rain)
   #  -L5 (db) Outdoor <=> Indoor loss
   PT =     +10*np.log10(pwrKW*1000000)
   P2 =     -20*2*np.log10(freqMHz)
   P3 =     -32.44
   P4 =     +10*np.log10(1)
   P5 =     +10*np.log10(1)

   total =  pwrRCVdbm -PT -G1 -G2 -P2 -P3 -P4 -P5
   R =      np.power(10, (total/-20.0))
   return R

#  Received power (dBm) at R km from a pwrKM transmitter
#  operatint at freqMHz frequency.
#  G1 - Transmitter gain
#  G2 - Receiver gain
def dBm_at_KM(pwrKW, distance, freqMHz, G1=13.17, G2=1.28):
   #  Power on the receiver =
   #  +PT   Transmitter power (dBm)
   #
   #  +G1   gain transmitter(dB)
   #        13.71 typ. broadcast
   #
   #  +G2   gain receiver (db)
   #        1.28 Lambda/4 monopole
   #
   #  -P1   -10 * n * log(R)
   #        n = power on distance variation (2 for free space)
   #        R = distance (km)
   #
   #  -P2   -20 * m * log(MHz)
   #        m = power on frequency variation (2 for free space)
   #
   #  -P3   -32,44
   #
   #  +P4   +10 * log(p) polarization mismatch (1 perfect match)
   #
   #  +P5   +10 * log(q) impedance mismatch (1 perfect match)
   #
   #  -L1 (dB) loss by height (transmitter)
   #  -L2 (dB) loss by height (receiver)
   #  -L3 (db) Clear air absorption
   #  -L4 (db) Hydrometeor absorption (ie. rain)
   #  -L5 (db) Outdoor <=> Indoor loss
   PT =  +10*np.log10(pwrKW*1000000)
   P1 =  -10*2*np.log10(distance)
   P2 =  -20*2*np.log10(freqMHz)
   P3 =  -32.44
   P4 =  +10*np.log10(1)
   P5 =  +10*np.log10(1)

   total = PT + G1 + G2 + P1 + P2 + P3 + P4 + P5
   return total


## Main
if __name__=="__main__":
   #  Calculate power:
   #  10    transmitter power (kW)
   #  100   distance (km)
   #  98    frequency (MHz)
   #  G1    gain transmitter (dB)
   #  G2    gain receiver (dB)
   print dBm_at_KM(10, 100, 98, G1=10.51, G2=5.1)


   #  Calculate reach:
   #  10    transmitter power (kW)
   #  -66.  expected power on receiver(dBm)
   #  98    frequency (MHz)
   #  G1    gain transmitter (dB)
   #  G2    gain receiver (dB)
   print distance_dBm(10,-66.479043,98, G1=10.51, G2=5.1)

   #  Line of sight
   #  1000  transmitter height (m)
   #  500   receiver height (m)
   #  6371  Earth radius
   #  4/3   extension by atmosphere transmission
   print "Line of sight:"
   print lineOfSight(0,50, R=6371, extend=4.0/3.0)
