# -*-coding: utf-8 -*-
"""
this is the φ18 balance data's translation programming.

Author: liuchao
Date: 2014-09-05
"""

from numpy import (genfromtxt, zeros, deg2rad, sin, cos, savetxt, hstack)

AIR_DENSITY = 1.2250  # 空气密度

#aircraft's area, characteristic chord, free flow pressure, _dx, _dy, _dz, air speed:V, flow pressure.
s = 0.0312                      # unit: m2
l = 0.225                       # unit: m
ba = 0.15                       # unit: pa
dx = -0.156                     # unit: m
dy = -0.02                      # unit: m
dz = 0                          # unit: m
V = 8                           # unit: m/s
q = 0.5*AIR_DENSITY*V**2        # unit: pa
#data file's names
staFile = 'pw10v8j.dat'      # static file's name
dynFile = 'pw10v8d.dat'      # dynamic file's name
bodyFile = 'Body.dat'        # body file's name
aeroFile = 'Aero.dat'        # aero file's name

headerRows = 2          # data file's header nums
footerRows = 0          # data file's footer nums
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
# read the file's headers and footers
rawList = open(staFile).readlines()
headerList = rawList[:headerRows] if headerRows else []
footerList = rawList[-footerRows:] if footerRows else []

#calculate the "body frame"'s fore and moment's coefficient
Fe = dynForce - staForce                  # Fe: the raw Force and moment of Balance at the "Body frame"in the experiment
Fbb = zeros(shape=(m, forceCols))         # Fbb: Force and moment of Balance at the "Body frame"

Fbb[:, 0] = 6.11960*Fe[:, 0]
Fbb[:, 1] = 12.33276*Fe[:, 1]
Fbb[:, 2] = 4.76279*Fe[:, 2]
Fbb[:, 3] = 0.38218*Fe[:, 3]
Fbb[:, 4] = 0.19456*Fe[:, 4]
Fbb[:, 5] = 0.69732*Fe[:, 5]
for i in range(100):
    Fbb[:, 0] = 6.11960*Fe[:, 0] + \
        0.00548*Fbb[:, 1] + 0.10290*Fbb[:, 2] + 0.12796*Fbb[:, 3] + 1.03638*Fbb[:, 4] - 0.21182*Fbb[:, 5] + \
        0.00090*Fbb[:, 0]*Fbb[:, 0] - 0.00023*Fbb[:, 0]*Fbb[:, 1] + 0.00034*Fbb[:, 0]*Fbb[:, 2] + \
        0.00198*Fbb[:, 0]*Fbb[:, 3] + 0.00447*Fbb[:, 0]*Fbb[:, 4] - 0.00065*Fbb[:, 0]*Fbb[:, 5] - \
        0.00001*Fbb[:, 1]*Fbb[:, 2] - 0.00444*Fbb[:, 1]*Fbb[:, 3] - 0.00041*Fbb[:, 1]*Fbb[:, 4] + \
        0.00512*Fbb[:, 1]*Fbb[:, 5] + 0.00014*Fbb[:, 2]*Fbb[:, 2] - 0.00243*Fbb[:, 2]*Fbb[:, 3] - \
        0.00292*Fbb[:, 2]*Fbb[:, 4] + 0.00033*Fbb[:, 2]*Fbb[:, 5] - 0.31818*Fbb[:, 3]*Fbb[:, 3] + \
        0.04225*Fbb[:, 3]*Fbb[:, 4] + 0.27065*Fbb[:, 3]*Fbb[:, 5] - 0.02223*Fbb[:, 4]*Fbb[:, 4] - \
        0.01045*Fbb[:, 4]*Fbb[:, 5] - 0.02171*Fbb[:, 5]*Fbb[:, 5]
    Fbb[:, 1] = 12.33276*Fe[:, 1] - \
        0.01686*Fbb[:, 0] + 0.01297*Fbb[:, 2] - 0.23388*Fbb[:, 3] - 0.19139*Fbb[:, 4] + 0.18227*Fbb[:, 5] - \
        0.00010*Fbb[:, 1]*Fbb[:, 1] - 0.00010*Fbb[:, 1]*Fbb[:, 0] + 0.00004*Fbb[:, 1]*Fbb[:, 2] - \
        0.00274*Fbb[:, 1]*Fbb[:, 3] + 0.00056*Fbb[:, 1]*Fbb[:, 4] + 0.00107*Fbb[:, 1]*Fbb[:, 5] + \
        0.00045*Fbb[:, 0]*Fbb[:, 0] + 0.00030*Fbb[:, 0]*Fbb[:, 2] + 0.00077*Fbb[:, 0]*Fbb[:, 3] + \
        0.00181*Fbb[:, 0]*Fbb[:, 4] - 0.00549*Fbb[:, 0]*Fbb[:, 5] - 0.00006*Fbb[:, 2]*Fbb[:, 2] - \
        0.01497*Fbb[:, 2]*Fbb[:, 3] + 0.00340*Fbb[:, 2]*Fbb[:, 4] + 0.00213*Fbb[:, 2]*Fbb[:, 5] - \
        0.03901*Fbb[:, 3]*Fbb[:, 3] - 0.15065*Fbb[:, 3]*Fbb[:, 4] + 0.02407*Fbb[:, 3]*Fbb[:, 5] + \
        0.00754*Fbb[:, 4]*Fbb[:, 4] + 0.02244*Fbb[:, 4]*Fbb[:, 5] - 0.01096*Fbb[:, 5]*Fbb[:, 5]
    Fbb[:, 2] = 4.76279*Fe[:, 2] - \
        0.02295*Fbb[:, 1] + 0.00338*Fbb[:, 0] - 0.17365*Fbb[:, 3] - 0.36139*Fbb[:, 4] + 0.00857*Fbb[:, 5] + \
        0.00032*Fbb[:, 2]*Fbb[:, 2] - 0.00009*Fbb[:, 2]*Fbb[:, 1] - 0.00016*Fbb[:, 2]*Fbb[:, 0] + \
        0.00366*Fbb[:, 2]*Fbb[:, 3] - 0.00382*Fbb[:, 2]*Fbb[:, 4] + 0.00146*Fbb[:, 2]*Fbb[:, 5] + \
        0.00031*Fbb[:, 1]*Fbb[:, 1] - 0.00050*Fbb[:, 1]*Fbb[:, 0] + 0.02079*Fbb[:, 1]*Fbb[:, 3] - \
        0.00222*Fbb[:, 1]*Fbb[:, 4] - 0.00709*Fbb[:, 1]*Fbb[:, 5] + 0.00045*Fbb[:, 0]*Fbb[:, 0] + \
        0.00588*Fbb[:, 0]*Fbb[:, 3] + 0.01732*Fbb[:, 0]*Fbb[:, 4] - 0.00223*Fbb[:, 0]*Fbb[:, 5] - \
        0.12878*Fbb[:, 3]*Fbb[:, 3] + 0.09362*Fbb[:, 3]*Fbb[:, 4] - 0.24968*Fbb[:, 3]*Fbb[:, 5] + \
        0.08996*Fbb[:, 4]*Fbb[:, 4] + 0.01747*Fbb[:, 4]*Fbb[:, 5] + 0.01161*Fbb[:, 5]*Fbb[:, 5]
    Fbb[:, 3] = 0.38218*Fe[:, 3] + \
        0.00068*Fbb[:, 1] - 0.00015*Fbb[:, 2] + 0.00010*Fbb[:, 0] - 0.0073*Fbb[:, 4] + 0.01998*Fbb[:, 5] - \
        0.00141*Fbb[:, 3]*Fbb[:, 3] - 0.00067*Fbb[:, 3]*Fbb[:, 1] - 0.00055*Fbb[:, 3]*Fbb[:, 2] + \
        0.00016*Fbb[:, 3]*Fbb[:, 0] - 0.00475*Fbb[:, 3]*Fbb[:, 4] + 0.00236*Fbb[:, 3]*Fbb[:, 5] - \
        0.00001*Fbb[:, 1]*Fbb[:, 1] + 0.00001*Fbb[:, 2]*Fbb[:, 1] + 0.00002*Fbb[:, 1]*Fbb[:, 0] + \
        0.00025*Fbb[:, 1]*Fbb[:, 4] + 0.00025*Fbb[:, 1]*Fbb[:, 5] - 0.00003*Fbb[:, 2]*Fbb[:, 2] + \
        0.00002*Fbb[:, 2]*Fbb[:, 0] + 0.00026*Fbb[:, 2]*Fbb[:, 4] + 0.00004*Fbb[:, 2]*Fbb[:, 5] - \
        0.00004*Fbb[:, 0]*Fbb[:, 0] - 0.00042*Fbb[:, 0]*Fbb[:, 4] + 0.00023*Fbb[:, 0]*Fbb[:, 5] - \
        0.00954*Fbb[:, 4]*Fbb[:, 4] - 0.00136*Fbb[:, 4]*Fbb[:, 5] + 0.00219*Fbb[:, 5]*Fbb[:, 5]
    Fbb[:, 4] = 0.19456*Fe[:, 4] - \
        0.00007*Fbb[:, 1] + 0.00227*Fbb[:, 2] + 0.00113*Fbb[:, 3] - 0.00012*Fbb[:, 0] + 0.00488*Fbb[:, 5] + \
        0.00714*Fbb[:, 4]*Fbb[:, 4] + 0.00000*Fbb[:, 4]*Fbb[:, 1] - 0.00010*Fbb[:, 4]*Fbb[:, 2] - \
        0.00955*Fbb[:, 4]*Fbb[:, 3] + 0.00158*Fbb[:, 0]*Fbb[:, 0] - 0.00279*Fbb[:, 4]*Fbb[:, 5] + \
        0.00001*Fbb[:, 1]*Fbb[:, 1] + 0.00058*Fbb[:, 1]*Fbb[:, 3] - 0.00035*Fbb[:, 1]*Fbb[:, 5] + \
        0.00001*Fbb[:, 2]*Fbb[:, 2] - 0.00035*Fbb[:, 2]*Fbb[:, 3] - 0.00005*Fbb[:, 2]*Fbb[:, 0] - \
        0.00006*Fbb[:, 2]*Fbb[:, 5] - 0.00180*Fbb[:, 3]*Fbb[:, 3] + 0.00022*Fbb[:, 3]*Fbb[:, 0] - \
        0.02256*Fbb[:, 3]*Fbb[:, 5] - 0.00005*Fbb[:, 0]*Fbb[:, 0] + 0.00090*Fbb[:, 0]*Fbb[:, 5] - \
        0.00117*Fbb[:, 5]*Fbb[:, 5]
    Fbb[:, 5] = 0.69732*Fe[:, 5] + \
        0.00041*Fbb[:, 1] - 0.00087*Fbb[:, 2] - 0.05093*Fbb[:, 3] - 0.03029*Fbb[:, 4] + 0.00121*Fbb[:, 0] - \
        0.00147*Fbb[:, 5]*Fbb[:, 5] - 0.00009*Fbb[:, 5]*Fbb[:, 1] + 0.00000*Fbb[:, 5]*Fbb[:, 2] + \
        0.00302*Fbb[:, 5]*Fbb[:, 3] - 0.00159*Fbb[:, 5]*Fbb[:, 4] + 0.00169*Fbb[:, 5]*Fbb[:, 0] - \
        0.00019*Fbb[:, 1]*Fbb[:, 3] - 0.00007*Fbb[:, 1]*Fbb[:, 4] + 0.00001*Fbb[:, 1]*Fbb[:, 0] - \
        0.00001*Fbb[:, 2]*Fbb[:, 2] + 0.00035*Fbb[:, 2]*Fbb[:, 3] + 0.00011*Fbb[:, 2]*Fbb[:, 4] + \
        0.00001*Fbb[:, 2]*Fbb[:, 0] - 0.00497*Fbb[:, 3]*Fbb[:, 3] + 0.01545*Fbb[:, 3]*Fbb[:, 4] - \
        0.00069*Fbb[:, 3]*Fbb[:, 0] - 0.00108*Fbb[:, 4]*Fbb[:, 4] + 0.00031*Fbb[:, 4]*Fbb[:, 5] + \
        0.00001*Fbb[:, 0]*Fbb[:, 0]


#the balance's "body frame" data translation to aircraft 's "body frame"
Fb = zeros(shape=(m, forceCols))      # Fb: Force and moment of aircraft at the "Body frame"
Fb[:, 0] = Fbb[:, 0]*0.95
Fb[:, 1] = Fbb[:, 1]*0.98
Fb[:, 2] = Fbb[:, 2]
Fb[:, 3] = Fbb[:, 3] + Fbb[:, 2]*dy - Fbb[:, 1]*dz
Fb[:, 4] = Fbb[:, 4] - Fbb[:, 0]*dz - Fbb[:, 2]*dx
Fb[:, 5] = (Fbb[:, 5] + Fbb[:, 0]*dy + Fbb[:, 1]*dx)*0.56

#calculate the aero data
Fa = zeros(shape=(m, forceCols))      # Fa: aero's Force and moment
Fa[:, 0] = cos(angleR[:, 0])*cos(angleR[:, 1])*Fb[:, 0]+sin(angleR[:, 0])*cos(angleR[:, 1])*Fb[:, 1]-sin(angleR[:, 1])*Fb[:, 2]
Fa[:, 1] = -sin(angleR[:, 0])*Fb[:, 0]+cos(angleR[:, 0])*Fb[:, 1]
Fa[:, 2] = cos(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 0]+sin(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 1]+cos(angleR[:, 1])*Fb[:, 2]
Fa[:, 3] = cos(angleR[:, 0])*cos(angleR[:, 1])*Fb[:, 3]-sin(angleR[:, 0])*cos(angleR[:, 0])*Fb[:, 4]+sin(angleR[:, 1])*Fb[:, 5]
Fa[:, 4] = sin(angleR[:, 0])*Fb[:, 3]+cos(angleR[:, 0])*Fb[:, 4]
Fa[:, 5] = -cos(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 3]+sin(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 4]+cos(angleR[:, 1])*Fb[:, 5]

# Cb: Coefficient of force and moment at the Body frame
Cb = zeros(shape=(m, forceCols))
Cb[:, :3] = Fb[:, :3]*9.8/(q*s)
Cb[:, 3:5] = Fb[:, 3:5]*9.8/(q*s*l)
Cb[:, 5] = Fb[:, 5]*9.8/(q*s*ba)
# Ca: Coefficient of force and moment at the Aero frame
Ca = zeros(shape=(m, forceCols))
Ca[:, :3] = Fa[:, :3]*9.8/(q*s)
Ca[:, 3:5] = Fa[:, 3:5]*9.8/(q*s*l)
Ca[:, 5] = Fa[:, 5]*9.8/(q*s*ba)

Mb = hstack((angle, Cb))
Ma = hstack((angle, Ca))

savetxt(bodyFile, Mb, fmt='%-15.8f',
        header=''.join(headerList).strip(),
        footer=''.join(footerList).strip(),
        comments='')
savetxt(aeroFile, Ma, fmt='%-15.8f',
        header=''.join(headerList).strip(),
        footer=''.join(footerList).strip(),
        comments='')