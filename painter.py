#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide.QtGui import *
from PySide.QtCore import *
import xml.etree.ElementTree as ET
from startSettings import StartSettings
from datetime import datetime

def get_qt_point_from_xml_point(point, scale):
  return QPoint(
      float(point.find('x').text) * scale.x(),
      -1 * float(point.find('y').text) * scale.y()
      )


def get_qt_point_from_tuple(point, scale):
  return QPoint(
      point[0] * scale.x(),
      -1 * point[1] * scale.y()
      )


def draw_lines_from_points(qp, points, scale, zero, transform, cicle=False):
  qt_points = []
  for p in points:
    qt_points.append(transform(p, scale))
  for start, finish in zip(qt_points[:-1], qt_points[1:]): 
    qp.drawLine(zero + start, zero + finish)
  if cicle == True:
    qp.drawLine(zero + qt_points[0], zero + qt_points[-1])


class Trajectory(QWidget):

  def get_model_size(self):
    sett = self.start_settings
    ground_set = sett.ground_settings

    qt_body_vectors = []
    mass_center = QVector2D(0, 0)
    for p in sett.geometry:
      qt_vector = QVector2D(p[0], p[1])
      qt_body_vectors.append(qt_vector)
      mass_center += qt_vector
    mass_center /= len(qt_body_vectors)
    self.max_distance = max(qt_body_vectors, key=lambda vec: (mass_center - vec).lengthSquared()).length()
    model_width = ground_set.get_right()[0] - ground_set.get_left()[0] + 2 * self.max_distance

    # 20 - max speed in Box2D world
    model_height = 1.2 * (sett.position[1] + float(20 ** 2) / (2 *
          sett.g) - ground_set.get_bottom()[1])
    return QVector2D(model_width, model_height)

  
  def init(self):
    self.width = 800.0
    self.height = 800.0
    self.offset = QPoint(20, 20)
    # Create two are: one for text and another for trajectory. 
    self.text_area = QRect(
        self.offset.x() + 0, self.offset.y() + 0, 
        800, 40)
    # Setting trajectory area depended from text area
    self.trajectory_area = QRect(
        self.text_area.left() + 0, self.text_area.bottom() + 10, 
        800, 800
        )
    self.directory_to_save = "out/"
    
    model_size = self.get_model_size()
    ground_set = self.start_settings.ground_settings

    self.scale = QVector2D(
          self.trajectory_area.width() / model_size.x(), 
          self.trajectory_area.height() / model_size.y()
          )
    if self.scale.x() > self.scale.y():
      self.scale.setX(self.scale.y())
      self.trajectory_area.setWidth(model_size.x() * self.scale.x())
    else:
      self.scale.setY(self.scale.x())
      self.trajectory_area.setHeight(model_size.y() * self.scale.y())

    self.local_zero_point = QPoint(
        -self.scale.x() * (ground_set.get_left()[0] - self.max_distance),
        -self.scale.y() * ground_set.get_bottom()[1] 
        )  
    self.target = QPoint(
        self.scale.x() * (self.start_settings.target_point[0] + 
          self.start_settings.target_position[0]),
        -self.scale.y() * (self.start_settings.target_point[1] + 
          self.start_settings.target_position[1])
        )

    # Getting resulting size of image
    self.total_area = QVector2D(
        max(self.text_area.right(), self.trajectory_area.right()) + self.offset.x(), 
        self.trajectory_area.bottom() + self.offset.y()
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
    self.init()
    self.init_ui()
    
  def init_ui(self):    
    self.setGeometry(50, 50, self.total_area.x(), self.total_area.y())
    self.setWindowTitle('Result')
    self.show()

  def paintEvent(self, event):
    qp = QPainter()
    qp.begin(self)

    self.draw_image()
    qp.drawImage(0, 0, self.image)    

    qp.end()

  def draw_image(self):
    self.image = QImage(self.total_area.x(), self.total_area.y(), QImage.Format_ARGB32)
    self.image.fill(qRgb(255, 255, 255))
    qp = QPainter()
    qp.begin(self.image)
    
    self.draw_trajectory(qp)
    self.draw_ground(qp)
    self.draw_target(qp)
    self.draw_body(qp)
    self.draw_text(qp)

    qp.end()

  def save_image(self):
    temp = datetime.now()
    filename = temp.strftime("%y_%m_%d__%H_%M_%S_") + "{:0>6}".format(temp.microsecond) + ".png"
    self.image.save(self.directory_to_save + filename)

  def get_trajectory_zero_point(self):
    return QPoint(
      self.trajectory_area.left() + self.local_zero_point.x(),
      self.trajectory_area.bottom() - self.local_zero_point.y()
      )

  def draw_trajectory(self, qp):
    scale = self.scale
    zero = self.get_trajectory_zero_point()

    trajectory = self.root.find("trajectory")
    iterations = trajectory.findall('iteration')
    draw_lines_from_points(qp, iterations, scale, zero, get_qt_point_from_xml_point)
        
  def draw_ground(self, qp):
    scale = self.scale
    zero = self.get_trajectory_zero_point()

    draw_lines_from_points(
        qp, self.start_settings.ground_settings.points, 
        scale, zero, get_qt_point_from_tuple
        )

  def draw_target(self, qp):
    scale = self.scale
    sett = self.start_settings
    zero = self.get_trajectory_zero_point()

    target_position = get_qt_point_from_tuple(sett.target_position, scale)
    
    draw_lines_from_points(
        qp, sett.right_side_of_target, scale, 
        zero + target_position, get_qt_point_from_tuple, cicle=True
        )
    draw_lines_from_points(
        qp, sett.left_side_of_target, scale, 
        zero + target_position, get_qt_point_from_tuple, cicle=True
        )
    qp.drawEllipse(zero + self.target, 2, 2)      # rx = 2, ry = 2

  def draw_body(self, qp):
    scale = self.scale
    zero = self.get_trajectory_zero_point()
    
    body = self.root.find("result").find("body")
    vertices = body.findall('vertice')
    draw_lines_from_points(qp, vertices, scale, zero, get_qt_point_from_xml_point, cicle=True)
    
  def draw_text(self, qp):
    rect = QRectF(self.text_area)
    text = unicode(' Simulation\n Distance: {}'.format(self.root.find("result").find("distance").text))
    qp.fillRect(rect, QColor(255, 255, 255))
    qp.setPen(QColor(168, 34, 3))
    qp.setFont(QFont('Decorative', 10))
    qp.drawText(rect, Qt.AlignLeft, text)        
    

def main(root, settings, show_image=False):
  app = QApplication([])
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
  main(namespace.trajectory_file, namespace.settings_file, namespace.show_image)
