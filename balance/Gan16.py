# -*-coding: utf-8 -*-
"""
this is the φ16 balance data's translation programming.

Author: liuchao
Date: 2014-09-05
"""

from numpy import (genfromtxt, zeros, deg2rad, sin, cos, savetxt, hstack)

#aircraft's area, characteristic chord, free flow pressure, _dx, _dy, _dz, air speed:V
s = 0.0312      # unit: m2
l = 0.225       # unit: m
ba = 0.15       # unit: pa
dx = -0.156     # unit: m
dy = -0.02      # unit: m
dz = 0          # unit: m
V = 8           # unit: m/s
#data file's names
staFile = 'pw10v8j.dat'      # static file's name
dynFile = 'pw10v8d.dat'      # dynamic file's name
bodyFile = 'Body.dat'     # body file's name
aeroFile = 'Aero.dat'     # aero file's name

headerRows = 2         # data file's header nums
footerRows = 0         # data file's footer nums
angleStartCol = 1       # angle start column
angleEndCol = 3         # angle end column
angleCols = angleEndCol - angleStartCol + 1     # angle columns
forceStartCol = 4       # force and moment start column
forceEndCol = 9         # force and moment end column
forceCols = forceEndCol - forceStartCol + 1     # force and moment columns

#load static file and dynamic file
staData = genfromtxt(fname=staFile, skip_header=headerRows, skip_footer=footerRows)
dynData = genfromtxt(fname=dynFile, skip_header=headerRows, skip_footer=footerRows)
staAngle, staForce = staData[:, (angleStartCol-1):angleEndCol], staData[:, (forceStartCol-1):forceEndCol]
dynAngle, dynForce = dynData[:, (angleStartCol-1):angleEndCol], dynData[:, (forceStartCol-1):forceEndCol]
staAngleR, dynAngleR = deg2rad(staAngle), deg2rad(dynAngle)         # change the degrees to radius
angle = (staAngle + dynAngle)/2.
angleR = (staAngleR + dynAngleR)/2.
m, n = staData.shape
rawList = open(staFile).readlines()
headerList = rawList[:headerRows] if headerRows else []
footerList = rawList[-footerRows:] if footerRows else []

#calculate the "body frame"'s fore and moment's coefficient
Fe = dynForce - staForce            # Fe: the raw Force and moment of Balance at the "Body frame"in the experiment
Fbb = zeros(shape=(m, forceCols))         # Fbb: Force and moment of Balance at the "Body frame"
Fbb[:, 0] = 0.2554675*Fe[:, 0] - 0.0154822*Fe[:, 1] + 0.00390868*Fe[:, 2] - 0.0051715*Fe[:, 3] - \
    0.00178511*Fe[:, 4] - 0.0024596*Fe[:, 5]
Fbb[:, 1] = 0.00068324*Fe[:, 0] + 0.6661034*Fe[:, 1] + 0.0120892*Fe[:, 2] - 0.0109143*Fe[:, 3] + \
    0.0391122*Fe[:, 4] + 0.0151383*Fe[:, 5]
Fbb[:, 2] = 0.00096904*Fe[:, 0] + 0.00120306*Fe[:, 1] + 0.585989*Fe[:, 2] + 0.027769*Fe[:, 3] + \
    0.014161*Fe[:, 4] + 0.00452654*Fe[:, 5]
Fbb[:, 3] = 0.000095445*Fe[:, 0] + 0.00029407*Fe[:, 1] + 0.00726843*Fe[:, 2] + 0.03304980*Fe[:, 3] + \
    0.0082689*Fe[:, 4] + 0.000152507*Fe[:, 5]
Fbb[:, 4] = -0.00036007*Fe[:, 0] - 0.00009756*Fe[:, 1] + 0.00098957*Fe[:, 2] + 0.00055426*Fe[:, 3] + \
    0.02351212*Fe[:, 4] - 0.000134249*Fe[:, 5]
Fbb[:, 5] = -0.000025559*Fe[:, 0] + 0.00075648*Fe[:, 1] + 0.000344149*Fe[:, 2] - 0.000585242*Fe[:, 3] - \
    0.0022913*Fe[:, 4] + 0.0276978*Fe[:, 5]

#the balance 's "body frame" data translation to aircraft 's "body frame"
Fb = zeros(shape=(m, forceCols))      # Fb: Force and moment of aircraft at the "Body frame"
Fb[:, :3] = Fbb[:, :3]
Fb[:, 3] = Fbb[:, 3] + Fbb[:, 2]*dy - Fbb[:, 1]*dz
Fb[:, 4] = Fbb[:, 4] - Fbb[:, 0]*dz - Fbb[:, 2]*dx
Fb[:, 5] = Fbb[:, 5] + Fbb[:, 0]*dy + Fbb[:, 1]*dx

#calculate the aero data
Fa = zeros(shape=(m, forceCols))      # Fa: aero's Force and moment
Fa[:, 0] = cos(angleR[:, 0])*cos(angleR[:, 1])*Fb[:, 0] + sin(angleR[:, 0])*cos(angleR[:, 1])*Fb[:, 1] - \
    sin(angleR[:, 1])*Fb[:, 2]
Fa[:, 1] = - sin(angleR[:, 0])*Fb[:, 0] + cos(angleR[:, 0])*Fb[:, 1]
Fa[:, 2] = cos(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 0] + sin(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 1] + \
    cos(angleR[:, 1])*Fb[:, 2]
Fa[:, 3] = cos(angleR[:, 0])*cos(angleR[:, 1])*Fb[:, 3] - sin(angleR[:, 0])*cos(angleR[:, 0])*Fb[:, 4] + \
    sin(angleR[:, 1])*Fb[:, 5]
Fa[:, 4] = sin(angleR[:, 0])*Fb[:, 3] + cos(angleR[:, 0])*Fb[:, 4]
Fa[:, 5] = - cos(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 3] + sin(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 4] + \
    cos(angleR[:, 1])*Fb[:, 5]

# Cb: Coefficient of force and moment at the Body frame
Cb = zeros(shape=(m, forceCols))
Cb[:, :3] = Fb[:, :3]*9.8/(39.2*s)
Cb[:, 3:5] = Fb[:, 3:5]*9.8/(39.2*s*l)
Cb[:, 5] = Fb[:, 5]*9.8/(39.2*s*ba)
# Ca: Coefficient of force and moment at the Aero frame
Ca = zeros(shape=(m, forceCols))
Ca[:, :3] = Fa[:, :3]*9.8/(39.2*s)
Ca[:, 3:5] = Fa[:, 3:5]*9.8/(39.2*s*l)
Ca[:, 5] = Fa[:, 5]*9.8/(39.2*s*ba)

Mb = hstack((angle, Cb))
Ma = hstack((angle, Ca))

savetxt(bodyFile, Mb, fmt='%-15.8f', header=''.join(headerList).strip(), footer=''.join(footerList).strip(), comments='')
savetxt(aeroFile, Ma, fmt='%-15.8f', header=''.join(headerList).strip(), footer=''.join(footerList).strip(), comments='')