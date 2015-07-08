#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from framework import *
import xml.etree.ElementTree as ET
import math

class StartSettings():
    def __init__(self):
        self.getFromXML()

    def getFromXML(self):
        tree = ET.parse('INPUT.dat')
        root = tree.getroot()
        body = root.find('body')
        self.linVelocityAmplitude = float(body.find('linVelocityAmplitude').text)
        self.linVelocityAngle = float(body.find('linVelocityAngle').text)
        self.angle = float(body.find('angle').text)
        point = body.find('position')[0]
        self.position = (float(point[0].text), float(point[1].text))
        self.thowableBody = []
        element = body.find('thowableBody')
        for point in element.findall('point'):
            self.thowableBody.append((float(point[0].text), float(point[1].text)))

        hole = root.find('hole')
        point = hole.find('holePosition')[0]
        self.holePosition = (float(point[0].text), float(point[1].text))
        self.leftSideOfHole = []
        element = hole.find('leftSideOfHole')
        for point in element.findall('point'):
            self.leftSideOfHole.append((float(point[0].text), float(point[1].text)))
        self.rightSideOfHole = []
        element = hole.find('rightSideOfHole')
        for point in element.findall('point'):
            self.rightSideOfHole.append((float(point[0].text), float(point[1].text)))

class Throwable(Framework):
    name = "Throwable" # Name of the class to display
    description = """w/s - increase/dicrease spead\
                a/d - increase/decrease angle"""
    iterationNumber = 0
    def __init__(self):
        super(Throwable, self).__init__()

        self.startSettings = StartSettings()
        self.resultTreeRoot = ET.Element("data")
        self.iterations = ET.SubElement(self.resultTreeRoot, "iterations")

        boundary_height = 2 * self.startSettings.position[1]
        left_edge = -100
        right_edge = 100

        # Ground
        self.world.CreateBody(
                    shapes = b2EdgeShape(vertices = [(left_edge, 0),(right_edge, 0)]) 
                )

        # Boundary
        self.world.CreateBody(
                    shapes = (
                        b2EdgeShape(vertices = [(left_edge, 0),(left_edge, boundary_height)]),
                        b2EdgeShape(vertices = [(right_edge, 0),(right_edge,
                                boundary_height)]),
                        b2EdgeShape(vertices = [(left_edge, boundary_height),(right_edge, boundary_height)])
                    )
                )
        # Hole
        self.world.CreateStaticBody(
                    position = self.startSettings.holePosition,
                    shapes = [
                            b2PolygonShape(vertices = self.startSettings.leftSideOfHole),
                            b2PolygonShape(vertices = self.startSettings.rightSideOfHole),
                        ]
                )

        self.shapes = (
                b2PolygonShape(vertices = self.startSettings.thowableBody)
                       )

        self.body=self.world.CreateDynamicBody(
                    position = self.startSettings.position, 
                    angle = self.startSettings.angle,
                    shapes = self.shapes,
                    shapeFixture = b2FixtureDef(density=1),
                    linearVelocity = (
                            self.startSettings.linVelocityAmplitude *
                            math.cos(self.startSettings.linVelocityAngle),
                            self.startSettings.linVelocityAmplitude *
                            math.sin(self.startSettings.linVelocityAngle)
                        )
                )

        self.fixtures = self.body.fixtures

    # Reset Thowable object
    def Restart(self):
        self.body.position = self.startSettings.position
        self.body.linearVelocity = (
                            self.startSettings.linVelocityAmplitude *
                            math.cos(self.startSettings.linVelocityAngle),
                            self.startSettings.linVelocityAmplitude *
                            math.sin(self.startSettings.linVelocityAngle)
                        )
        self.body.angle = self.startSettings.angle


    def Keyboard(self, key):
        if key == Keys.K_r:
            self.Restart()
            print "Linear Velocity:", self.body.linearVelocity
            print "Angle:", self.startSettings.linVelocityAngle / b2_pi * 180
        if key == Keys.K_w and self.startSettings.linVelocityAmplitude < 60:
            self.startSettings.linVelocityAmplitude += 1
        if key == Keys.K_s and self.startSettings.linVelocityAmplitude > 0:
            self.startSettings.linVelocityAmplitude -= 1
        if key == Keys.K_a:
            self.startSettings.linVelocityAngle += 1.0 / 180.0 * b2_pi
            if self.startSettings.linVelocityAngle > 2 * b2_pi:
                self.startSettings.linVelocityAngle -= 2 * b2_pi
        if key == Keys.K_d:
            self.startSettings.linVelocityAngle -= 1.0 / 180.0 * b2_pi
            if self.startSettings.linVelocityAngle < 0:
                self.startSettings.linVelocityAngle += 2 * b2_pi
        pass

    def Step(self, settings):

        super(Throwable, self).Step(settings)
        
        self.iterationNumber += 1
        iteration = ET.SubElement(self.iterations, "iteration")
        iteration.set("num", str(self.iterationNumber))
        x = ET.SubElement(iteration, "x")
        x.text = str(self.body.position.x)
        y = ET.SubElement(iteration, "y")
        y.text = str(self.body.position.y)

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
