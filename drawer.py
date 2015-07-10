#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide import QtGui, QtCore
import xml.etree.ElementTree as ET
from startSettings import StartSettings

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
    
    ground_set = self.start_settings.ground_settings

    self.scale = QtGui.QVector2D(self.width / 200, self.height / 200)
    self.zero_point = QtCore.QPointF(40, 40)
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
      tree = ET.parse('OUTPUT.dat')
      root = tree.getroot()

    if type(settings) == str:
      self.start_settings = StartSettings(settings)
    else:
      self.start_settings = settings

    self.root = root
    self.set_settings()
    self.init_ui()
    
  def init_ui(self):    
    self.setGeometry(300, 300, self.width, self.height)
    self.setWindowTitle('Result')
    self.show()

  def paintEvent(self, event):
    qp = QtGui.QPainter()
    qp.begin(self)
    self.draw_trajectory(qp)
    self.drawGround(qp)
    self.drawTarget(qp)
    self.drawBody(qp)
    qp.end()

  def draw_trajectory(self, qp):
    scale = self.scale
    zero = self.zero_point + self.local_zero_point
    zero.setY(self.height - zero.y())

    iterations_element = self.root.find("iterations")
    iterations = iterations_element.findall('iteration')
    draw_lines_from_points_from_xml(qp, iterations, scale, zero, get_qt_point_from_xml_point)
        
  def drawGround(self, qp):
    scale = self.scale
    zero = self.zero_point + self.local_zero_point
    zero.setY(self.height - zero.y())

    draw_lines_from_points_from_xml(
        qp, self.start_settings.ground_settings.points, 
        scale, zero, get_qt_point_from_tuple
        )

  def drawTarget(self, qp):
    zero = self.zero_point + self.local_zero_point
    zero.setY(self.height - zero.y())
    qp.drawEllipse(zero + self.target, 2, 2)

  def drawBody(self, qp):
    scale = self.scale
    zero = self.zero_point + self.local_zero_point
    zero.setY(self.height - zero.y())
    
    body = self.root.find("body")
    vertices = body.findall('vertice')
    draw_lines_from_points_from_xml(qp, vertices, scale, zero, get_qt_point_from_xml_point)
    start = get_qt_point_from_xml_point(vertices[0], scale)
    finish = get_qt_point_from_xml_point(vertices[-1], scale)
    qp.drawLine(zero + start, zero + finish)
    
    
def main(root, settings):
  app = QtGui.QApplication([])
  ex = Trajectory(root, settings)
  sys.exit(app.exec_())


if __name__ == '__main__':
  main('OUTPUT.dat', 'INPUT.dat')
