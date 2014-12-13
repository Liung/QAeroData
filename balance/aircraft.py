# -*-coding: utf-8 -*-
"""
this is aircraft file.
it contains a AircraftModel class

Author: liuchao
Date: 2014-09-05
"""


class AircraftModel(object):
    def __init__(self, area=0., span=0., rootChord=0., refChord=0.,
                 dx=0., dy=0., dz=0., speed=25.):
        self.area = area
        self.span = span
        self.rootChord = rootChord
        self.refChord = refChord
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.speed = speed

    def setArea(self, area):
        self.area = area

    def setSpan(self, span):
        self.span = span

    def setRootChord(self, rootChord):
        self.rootChord = rootChord

    def setRefChord(self, refChord):
        self.refChord = refChord

    def setWindSpeed(self, windSpeed=0.):
        self.speed = windSpeed

    def setDx(self, dx=0):
        self.dx = dx

    def setDy(self, dy=0.):
        self.dy = dy

    def setDz(self, dz=0.):
        self.dz = dz
