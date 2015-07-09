#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys
import math
from operator import itemgetter
import xml.etree.ElementTree as ET

def get_points_from_xml(element_name, root_element):
    points = []
    element = root_element.find(element_name)
    for point in element.findall('point'):
        points.append((float(point[0].text), float(point[1].text)))
    return points


def get_point_from_xml(element_name, root_element):
    point = root_element.find(element_name)[0]
    return (float(point[0].text), float(point[1].text))


class GroundSettings():

    def __init__(self, root_element):
        self.points = get_points_from_xml('vertices', root_element)
        self.left = min(self.points, key=itemgetter(0))
        self.right = max(self.points, key=itemgetter(0))
        self.bottom = min(self.points, key=itemgetter(1))

    def get_left(self):
        return self.left

    def get_right(self):
        return self.right

    def get_bottom(self):
        return self.bottom

    def create_shapes(self):
        shapes = []
        for p1, p2 in zip(self.points[:-1:1], self.points[1::1]):
            shapes.append(b2EdgeShape(vertices=[p1, p2]))
        return shapes


class StartSettings():

    def __init__(self):
        self.getFromXML()

    def getFromXML(self):
        tree = ET.parse('INPUT.dat')
        root = tree.getroot()

        model = root.find('model')
#       self.visualized = model.find('visualized').text == "True"
        self.velocity_iterations = int(model.find('velocity_iterations').text)
        self.position_iterations = int(model.find('position_iterations').text)
        self.hz = float(model.find('hz').text)
        self.epsilon_lin_velocity = float(model.find('epsilon_lin_velocity').text)

        ground = root.find('ground')
        self.ground_settings = GroundSettings(ground)

        body = root.find('body')
        self.lin_velocity_amplitude = float(body.find('lin_velocity_amplitude').text)
        self.lin_velocity_angle = float(body.find('lin_velocity_angle').text)
        self.angular_velocity = float(body.find('angular_velocity').text)
        self.angle = float(body.find('angle').text)
        self.position = get_point_from_xml('position', body)
        self.throwable_body = get_points_from_xml('throwable_body', body)

        hole = root.find('hole')
        self.hole_target = get_point_from_xml('hole_target', hole) 
        self.hole_position = get_point_from_xml('hole_position', hole) 
        self.left_side_of_hole = get_points_from_xml('left_side_of_hole', hole) 
        self.right_side_of_hole = get_points_from_xml('right_side_of_hole', hole) 


# start_settings = StartSettings()
if len(sys.argv) > 1:
    visualised = sys.argv[1] == "True"
else:
    visualised = False
if visualised:
    from framework import *
    class Decorator(Framework):
        name = "Throwable" # Name of the class to display
        description = "First example" 

        def get_the_world_set(self):
            super(Decorator, self).__init__()

        def make_world_step(self, settings):
            super(Throwable, self).Step(settings)

else:
    from Box2D import *
    class Decorator(object):
        
        def get_the_world_set(self):
            self.world = b2World(gravity=(0,-10), doSleep=True)

        def make_world_step(self, settings):
            timeStep = 1.0 / settings.hz
            self.world.Step(
                    timeStep, 
                    settings.velocity_iterations, 
                    settings.position_iterations
                    )

        def run(self):
            while not self.finalized:
                self.Step(self.start_settings)


class Throwable(Decorator):
    iterationNumber = 0

    def save_iteration_in_xml_tree(self):
        iteration = ET.SubElement(self.iterations, "iteration")
        iteration.set("num", str(self.iterationNumber))

        x = ET.SubElement(iteration, "x")
        x.text = str(self.body.position.x)
        
        y = ET.SubElement(iteration, "y")
        y.text = str(self.body.position.y)
        
        distance = ET.SubElement(iteration, "distance")
        vector_distance = self.body.position - self.start_settings.hole_position
        distance.text = str(vector_distance.lengthSquared)

    def __init__(self, start_settings):

        # Initialising settings
        # It should be the first execute
        sett = self.start_settings = start_settings

        self.get_the_world_set()

        # Ground
        self.world.CreateBody(
                    shapes=sett.ground_settings.create_shapes()
                )

        # Hole
        self.world.CreateStaticBody(
                    position=sett.hole_position,
                    shapes=[
                            b2PolygonShape(vertices=sett.left_side_of_hole),
                            b2PolygonShape(vertices=sett.right_side_of_hole),
                        ]
                )

        # Body
        self.shapes = (
                b2PolygonShape(vertices=sett.throwable_body)
                       )
        self.body=self.world.CreateDynamicBody(
                    position=sett.position, 
                    angle=sett.angle,
                    shapes=self.shapes,
                    shapeFixture=b2FixtureDef(density=1),
                    angularVelocity=sett.angular_velocity,
                    linearVelocity=(
                            sett.lin_velocity_amplitude *
                            math.cos(sett.lin_velocity_angle),
                            sett.lin_velocity_amplitude *
                            math.sin(sett.lin_velocity_angle)
                        )
                )
        self.fixtures = self.body.fixtures

        # Create output xml tree
        self.result_tree = ET.Element("data")
        self.iterations = ET.SubElement(self.result_tree, "iterations")
        self.save_iteration_in_xml_tree()
        self.finalized = False

    # Reset Thowable object
    def Restart(self):
        sett = self.start_settings
        self.body.position = sett.position
        self.body.linearVelocity = (
                            sett.lin_velocity_amplitude *
                            math.cos(sett.lin_velocity_angle),
                            sett.lin_velocity_amplitude *
                            math.sin(sett.lin_velocity_angle)
                        )
        self.body.angle = sett.angle
        self.body.angularVelocity = sett.angular_velocity

    def Keyboard(self, key):
        sett = self.start_settings

        if key == Keys.K_r:
            self.Restart()
            print "Linear Velocity:", self.body.linearVelocity
            print "Angle:", sett.lin_velocity_angle / b2_pi * 180

        if key == Keys.K_w and sett.lin_velocity_amplitude < 60:
            sett.lin_velocity_amplitude += 1

        if key == Keys.K_s and sett.lin_velocity_amplitude > 0:
            sett.lin_velocity_amplitude -= 1

        if key == Keys.K_a:
            sett.lin_velocity_angle += 1.0 / 180.0 * b2_pi
            if sett.lin_velocity_angle > 2 * b2_pi:
                sett.lin_velocity_angle -= 2 * b2_pi

        if key == Keys.K_d:
            sett.lin_velocity_angle -= 1.0 / 180.0 * b2_pi
            if sett.lin_velocity_angle < 0:
                sett.lin_velocity_angle += 2 * b2_pi

    def Step(self, settings):
        self.make_world_step(settings)
        self.iterationNumber += 1
        self.save_iteration_in_xml_tree()
        self.is_finished()

    # Actions to do in the end
    def finalize(self):
        if self.finalized == False:
            tree = ET.ElementTree(self.result_tree)
            tree.write('OUTPUT.dat')
            self.finalized = True
         
    # Should modelling be stopped
    def is_finished(self):
        if self.finalized == False:
            pos = self.body.position
            left = self.start_settings.ground_settings.get_left()
            right = self.start_settings.ground_settings.get_right()
            bottom = self.start_settings.ground_settings.get_bottom()
         
            if pos[0] < left[0] or pos[0] > right[0] or pos[0] < bottom[1]:
                print "Object is out of field"
                self.finalize()
            
            velocity = self.body.linearVelocity
            if velocity.lengthSquared < self.start_settings.epsilon_lin_velocity ** 2:
                print "Too slow"
                self.finalize()

if __name__=="__main__":
    start_settings = StartSettings()
    world = Throwable(start_settings)
    world.run()
    world.finalize()
