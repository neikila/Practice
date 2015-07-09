#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import math
import xml.etree.ElementTree as ET
from framework import *


def getMasOfPointsFromXML(elementName, rootElement):
    mas = []
    element = rootElement.find(elementName)
    for point in element.findall('point'):
        mas.append((float(point[0].text), float(point[1].text)))
    return mas


def getPointFromXML(elementName, rootElement):
    point = rootElement.find(elementName)[0]
    return (float(point[0].text), float(point[1].text))


class GroundSettings():
    masOfPoints = [(-40,0), (40,0)]

    def createMasOfShapes(self):
        mas = []
        previousPoint = self.masOfPoints[0]
        for point in self.masOfPoints[1:]:
            mas.append(b2EdgeShape(vertices = [previousPoint, point]))
            previousPoint = point
        return mas


class StartSettings():

    def __init__(self):
        self.getFromXML()
        self.groundSettings = GroundSettings()

    def getFromXML(self):
        tree = ET.parse('INPUT.dat')
        root = tree.getroot()

        body = root.find('body')
        self.linVelocityAmplitude = float(body.find('linVelocityAmplitude').text)
        self.linVelocityAngle = float(body.find('linVelocityAngle').text)
        self.angle = float(body.find('angle').text)
        self.position = getPointFromXML('position', body)
        self.thowableBody = getMasOfPointsFromXML('thowableBody', body)

        hole = root.find('hole')
        self.holePosition = getPointFromXML('holePosition', hole) 
        self.leftSideOfHole = getMasOfPointsFromXML('leftSideOfHole', hole) 
        self.rightSideOfHole = getMasOfPointsFromXML('rightSideOfHole', hole) 


class Throwable(Framework):
    name = "Throwable" # Name of the class to display
    description = """w/s - increase/dicrease spead\
                a/d - increase/decrease angle"""
    iterationNumber = 0

    def SaveIterationInXMLTree(self):
        iteration = ET.SubElement(self.iterations, "iteration")
        iteration.set("num", str(self.iterationNumber))

        x = ET.SubElement(iteration, "x")
        x.text = str(self.body.position.x)
        
        y = ET.SubElement(iteration, "y")
        y.text = str(self.body.position.y)
        
        distance = ET.SubElement(iteration, "distance")
        distance.text = str((self.body.position - self.startSettings.holePosition).lengthSquared)

    def __init__(self):
        super(Throwable, self).__init__()

        # Initialising settings
        sett = self.startSettings = StartSettings()

        # Ground
        self.world.CreateBody(
                    shapes = sett.groundSettings.createMasOfShapes()
                )

        # Hole
        self.world.CreateStaticBody(
                    position = sett.holePosition,
                    shapes = [
                            b2PolygonShape(vertices = sett.leftSideOfHole),
                            b2PolygonShape(vertices = sett.rightSideOfHole),
                        ]
                )

        # Body
        self.shapes = (
                b2PolygonShape(vertices = sett.thowableBody)
                       )
        self.body=self.world.CreateDynamicBody(
                    position = sett.position, 
                    angle = sett.angle,
                    shapes = self.shapes,
                    shapeFixture = b2FixtureDef(density=1),
                    linearVelocity = (
                            sett.linVelocityAmplitude *
                            math.cos(sett.linVelocityAngle),
                            sett.linVelocityAmplitude *
                            math.sin(sett.linVelocityAngle)
                        )
                )
        self.fixtures = self.body.fixtures

        # Create output xml tree
        self.resultTreeRoot = ET.Element("data")
        self.iterations = ET.SubElement(self.resultTreeRoot, "iterations")
        self.SaveIterationInXMLTree()

    # Reset Thowable object
    def Restart(self):
        sett = self.startSettings
        self.body.position = sett.position
        self.body.linearVelocity = (
                            sett.linVelocityAmplitude *
                            math.cos(sett.linVelocityAngle),
                            sett.linVelocityAmplitude *
                            math.sin(sett.linVelocityAngle)
                        )
        self.body.angle = sett.angle


    def Keyboard(self, key):
        sett = self.startSettings
        if key == Keys.K_r:
            self.Restart()
            print "Linear Velocity:", self.body.linearVelocity
            print "Angle:", sett.linVelocityAngle / b2_pi * 180
        if key == Keys.K_w and sett.linVelocityAmplitude < 60:
            sett.linVelocityAmplitude += 1

        if key == Keys.K_s and sett.linVelocityAmplitude > 0:
            sett.linVelocityAmplitude -= 1

        if key == Keys.K_a:
            sett.linVelocityAngle += 1.0 / 180.0 * b2_pi
            if sett.linVelocityAngle > 2 * b2_pi:
                sett.linVelocityAngle -= 2 * b2_pi

        if key == Keys.K_d:
            sett.linVelocityAngle -= 1.0 / 180.0 * b2_pi
            if sett.linVelocityAngle < 0:
                sett.linVelocityAngle += 2 * b2_pi

    def Step(self, settings):

        super(Throwable, self).Step(settings)
        
        self.iterationNumber += 1
        self.SaveIterationInXMLTree()

    def Finalize(self):
        tree = ET.ElementTree(self.resultTreeRoot)
        tree.write('OUTPUT.dat')
         

    def ShapeDestroyed(self, shape):
        """
        Callback indicating 'shape' has been destroyed.
        """
        pass

    def JointDestroyed(self, joint):
        """
        The joint passed in was removed.
        """
        pass

    # More functions can be changed to allow for contact monitoring and such.
    # See the other testbed examples for more information.

if __name__=="__main__":
#    main(Throwable)
    world = Throwable()
    world.run()
    world.Finalize()
