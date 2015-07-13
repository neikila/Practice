#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide import QtGui, QtCore
import xml.etree.ElementTree as ET
from startSettings import StartSettings
from datetime import datetime

def get_qt_point_from_xml_point(point, scale):
  return QtCore.QPointF(
      float(point.find('x').text) * scale.x(),
      -1 * float(point.find('y').text) * scale.y()
      )


def get_qt_point_from_tuple(point, scale):
  return QtCore.QPointF(
      point[0] * scale.x(),
      -1 * point[1] * scale.y()
      )

def draw_lines_from_points_from_xml(qp, points, scale, zero, transform):
  qt_points = []
  for p in points:
    qt_points.append(transform(p, scale))
  for start, finish in zip(qt_points[:-1], qt_points[1:]): 
    qp.drawLine(zero + start, zero + finish)


class Trajectory(QtGui.QWidget):
  
  def set_settings(self):
    self.width = 800.0
    self.height = 800.0
    self.directory_to_save = "out/"
    
    sett = self.start_settings
    ground_set = sett.ground_settings

    #TODO take into account distance till the far point of body
    model_width = ground_set.get_right()[0] - ground_set.get_left()[0] 
    # 20 - max speed in Box2D world
    model_height = 1.2 * (sett.position[1] + float(20 ** 2) / (2 *
          sett.g) - ground_set.get_bottom()[1])

    self.zero_point = QtCore.QPointF(20, 20)
    self.scale = QtGui.QVector2D(
          (self.width - 2 * self.zero_point.x()) / model_width, 
          (self.height - 2 * self.zero_point.y()) / model_height
          )
    self.local_zero_point = QtCore.QPointF(
        -self.scale.x() * ground_set.get_left()[0],
        -self.scale.y() * ground_set.get_bottom()[1] 
        )  
    self.target = QtCore.QPointF(
        self.scale.x() * (self.start_settings.hole_target[0] + 
          self.start_settings.hole_position[0]),
        -self.scale.y() * (self.start_settings.hole_target[1] + 
          self.start_settings.hole_position[1])
        )


  def __init__(self, root, settings):
    super(Trajectory, self).__init__()
    if type(root) == str:
      tree = ET.parse(root)
      root = tree.getroot()

    if type(settings) == str:
      self.start_settings = StartSettings(settings)
    else:
      self.start_settings = settings

    self.root = root
    self.set_settings()
    self.init_ui()
    
  def init_ui(self):    
    self.setGeometry(200, 200, self.width, self.height)
    self.setWindowTitle('Result')
    self.show()

  def paintEvent(self, event):
    qp = QtGui.QPainter()
    qp.begin(self)

    self.draw_image()
    qp.drawImage(0, 0, self.image)    

    qp.end()

  def draw_image(self):
    self.image = QtGui.QImage(self.width, self.height, QtGui.QImage.Format_ARGB32)
    self.image.fill(QtGui.qRgb(255, 255, 255))
    qp = QtGui.QPainter()
    qp.begin(self.image)
    
    self.draw_trajectory(qp)
    self.draw_ground(qp)
    self.draw_target(qp)
    self.draw_body(qp)

    qp.end()

  def save_image(self):
    temp = datetime.now()
    filename = temp.strftime("%y_%m_%d__%H_%M_") + "{:0>6}".format(temp.microsecond) + ".png"
    self.image.save(self.directory_to_save + filename)

  def draw_trajectory(self, qp):
    scale = self.scale
    zero = self.zero_point + self.local_zero_point
    zero.setY(self.height - zero.y())

    iterations_element = self.root.find("iterations")
    iterations = iterations_element.findall('iteration')
    draw_lines_from_points_from_xml(qp, iterations, scale, zero, get_qt_point_from_xml_point)
        
  def draw_ground(self, qp):
    scale = self.scale
    zero = self.zero_point + self.local_zero_point
    zero.setY(self.height - zero.y())

    draw_lines_from_points_from_xml(
        qp, self.start_settings.ground_settings.points, 
        scale, zero, get_qt_point_from_tuple
        )

  def draw_target(self, qp):
    zero = self.zero_point + self.local_zero_point
    zero.setY(self.height - zero.y())
    qp.drawEllipse(zero + self.target, 2, 2)

  def draw_body(self, qp):
    scale = self.scale
    zero = self.zero_point + self.local_zero_point
    zero.setY(self.height - zero.y())
    
    body = self.root.find("body")
    vertices = body.findall('vertice')
    draw_lines_from_points_from_xml(qp, vertices, scale, zero, get_qt_point_from_xml_point)
    start = get_qt_point_from_xml_point(vertices[0], scale)
    finish = get_qt_point_from_xml_point(vertices[-1], scale)
    qp.drawLine(zero + start, zero + finish)
    
    
def main(root, settings, show_image=False):
  app = QtGui.QApplication([])
  ex = Trajectory(root, settings)
  ex.draw_image()
  result = ex.save_image()
  if show_image == True:
    result = app.exec_()
  sys.exit(result)


if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument(
      '-sh', '--show_image', 
      action='store_true', default=False, 
      help='show png image'
      )
  parser.add_argument (
      '--trajectory_file', '-trf', 
      nargs='?', default='OUTPUT.dat',
      help='file containing all points of trajectory'
      )
  parser.add_argument (
      '--settings_file', '-sf', 
      nargs='?', default='INPUT.dat',
      help='file containig all settings')
  namespace = parser.parse_args()
  print namespace
  main(namespace.trajectory_file, namespace.settings_file, namespace.show_image)
