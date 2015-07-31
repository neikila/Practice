#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

import xml.etree.ElementTree as ET

from startSettings import StartSettings
from simulation import *
import painter

# pretty_print of xml tree
def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i


# p, p0, p1 - b2Vec2; p0, p1 - segment
def distance(p, p0, p1):
  v = p1 - p0
  w = p - p0
  c1 = w.dot(v)
  if c1 <= 0:
    return (p - p0).lengthSquared
  c2 = v.dot(v)
  if c2 <= c1:
    return (p - p1).lengthSquared
  b = c1 / c2 
  h = p0 + b * v
  return (p - h).lengthSquared


def shapes_from_points(points):
  shapes = []
  for p1, p2 in zip(points[:-1:1], points[1::1]):
    shapes.append(b2EdgeShape(vertices=[p1, p2]))
  return shapes

class Throwable(Simulation):
  iteration_number = 0

  def save_iteration_in_xml_tree(self, distance):
    iteration = ET.SubElement(self.trajectory, "iteration")
    iteration.set("num", str(self.iteration_number))

    self.body.GetMassData(self.mass_data)
    center = self.body.GetWorldPoint(self.mass_data.center)
    x = ET.SubElement(iteration, "x")
    x.text = str(center.x)
    
    y = ET.SubElement(iteration, "y")
    y.text = str(center.y)
    
    distance_element = ET.SubElement(iteration, "distance")
    distance_element.text = str(distance)

  def save_final_state(self, distance):
    result = ET.SubElement(self.result_tree, "result")

    distance_element = ET.SubElement(result, "distance")
    distance_element.text = str(distance)

    min_distance_element = ET.SubElement(result, "min_distance")
    min_distance_element.text = str(self.min_distance)

    mass = ET.SubElement(result, "mass")
    mass.text = str(self.mass_data.mass)

    inertia = ET.SubElement(result, "inertia")
    inertia.text = str(self.mass_data.I)

    sett = self.start_settings

    body = ET.SubElement(result, "body")
    body_vertices = self.shapes.vertices
    for vertice in body_vertices:
      temp = self.body.GetWorldPoint(vertice)
      vertice = ET.SubElement(body, "vertice")
      x = ET.SubElement(vertice, "x")
      x.text = str(temp.x)
      
      y = ET.SubElement(vertice, "y")
      y.text = str(temp.y)

  def __init__(self, start_settings):

    # Initialising settings
    # It should be the first to execute
    sett = self.start_settings = start_settings

    self.init_world()
    self.world.gravity=b2Vec2(0, -1 * sett.g)

    # Ground
    self.world.CreateBody(
          shapes=shapes_from_points(sett.ground_settings.points)
        )

    # Hole
    target = self.world.CreateStaticBody(
          position=sett.target_position,
          shapes=[
              b2PolygonShape(vertices=sett.left_side_of_target),
              b2PolygonShape(vertices=sett.right_side_of_target),
            ]
        )
    self.target = target.GetWorldPoint(sett.target_point)

    # Body
    self.shapes = (
        b2PolygonShape(vertices=sett.geometry)
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
    self.mass_data = b2MassData()

    # Create output xml tree
    self.result_tree = ET.Element("data")
    self.trajectory = ET.SubElement(self.result_tree, "trajectory")
    self.min_distance = self.distance_to_target(self.target)
    self.save_iteration_in_xml_tree(self.min_distance)
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
    self.step_world(settings)
    self.iteration_number += 1
    distance = self.distance_to_target(self.target)
    if self.min_distance > distance:
      self.min_distance = distance
    if self.iteration_number % 4 == 0 and self.finalized == False:
      self.save_iteration_in_xml_tree(distance)
    self.is_finished()

  # Actions to do in the end
  def finalize(self):
    if self.finalized == False:
      distance = self.distance_to_target(self.target)
      self.save_iteration_in_xml_tree(distance)
      self.save_final_state(distance)
      indent(self.result_tree)
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
     
      if pos[0] < left[0] or pos[0] > right[0] or pos[1] < bottom[1]:
        print "Object is out of field"
        self.finalize()
      
      velocity = self.body.linearVelocity
      if velocity.lengthSquared < self.start_settings.epsilon_lin_velocity ** 2:
        print "Too slow"
        self.finalize()

  def distance_to_target(self, target):
    body_vertices = self.shapes.vertices
    temp = [self.body.GetWorldPoint(vertice) for vertice in body_vertices]
    minimum = distance(target, temp[-1], temp[0])
    for p0, p1 in zip(temp[:-1:1], temp[1::1]):
      dist = distance(target, p0, p1)
      if dist < minimum:
        minimum = dist
    return minimum


if __name__=="__main__":
  start_settings = StartSettings()
  world = Throwable(start_settings)
  world.run()
  world.finalize()
  painter.main(world.result_tree, world.start_settings)
