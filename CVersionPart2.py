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

    def __init__(self, rootElement):
        self.masOfPoints = getMasOfPointsFromXML('vertices', rootElement)
        self.left = b2Vec2(min(self.masOfPoints, key=lambda el : el[0]))
        self.right = b2Vec2(max(self.masOfPoints, key=lambda el : el[0]))
        self.bottom = b2Vec2(min(self.masOfPoints, key=lambda el : el[1]))

    def getLeft(self):
        return self.left

    def getRight(self):
        return self.right

    def getBottom(self):
        return self.bottom

    def createMasOfShapes(self):
        mas = []
        previousPoint = self.masOfPoints[0]
        for point in self.masOfPoints[1:]:
            mas.append(b2EdgeShape(vertices=[previousPoint, point]))
            previousPoint = point
        return mas


class StartSettings():

    def __init__(self):
        self.getFromXML()

    def getFromXML(self):
        tree = ET.parse('INPUT.dat')
        root = tree.getroot()

        model = root.find('model')
        self.epsilonLinVelocity = float(model.find('epsilonLinVelocity').text)

        ground = root.find('ground')
        self.groundSettings = GroundSettings(ground)

        body = root.find('body')
        self.linVelocityAmplitude = float(body.find('linVelocityAmplitude').text)
        self.linVelocityAngle = float(body.find('linVelocityAngle').text)
        self.angularVelocity = float(body.find('angularVelocity').text) / 180 * b2_pi   # Convert from degree to radians
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
                    shapes=sett.groundSettings.createMasOfShapes()
                )

        # Hole
        self.world.CreateStaticBody(
                    position=sett.holePosition,
                    shapes=[
                            b2PolygonShape(vertices=sett.leftSideOfHole),
                            b2PolygonShape(vertices=sett.rightSideOfHole),
                        ]
                )

        # Body
        self.shapes = (
                b2PolygonShape(vertices=sett.thowableBody)
                       )
        self.body=self.world.CreateDynamicBody(
                    position=sett.position, 
                    angle=sett.angle,
                    shapes=self.shapes,
                    shapeFixture=b2FixtureDef(density=1),
                    angularVelocity=sett.angularVelocity,
                    linearVelocity=(
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
        self.finalized = False

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
        self.body.angularVelocity = sett.angularVelocity

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
        self.isFinished()

    def finalize(self):
        if self.finalized == False:
            tree = ET.ElementTree(self.resultTreeRoot)
            tree.write('OUTPUT.dat')
            self.finalized = True
         
    def isFinished(self):
        if self.finalized == False:
            pos = self.body.position
            left = self.startSettings.groundSettings.getLeft()
            right = self.startSettings.groundSettings.getRight()
            bottom = self.startSettings.groundSettings.getBottom()
         
            if pos.x < left.x or pos.x > right.x or pos.y < bottom.y:
                print "Object is out of field"
                self.finalize()
            
            velocity = self.body.linearVelocity
            if velocity.lengthSquared < self.startSettings.epsilonLinVelocity ** 2:
                print "Too slow"
                self.finalize()

#        mass = b2MassData()
#        self.body.GetMassData(mass)
#        print mass.mass

if __name__=="__main__":
#    main(Throwable)
    world = Throwable()
    world.run()
    world.finalize()
