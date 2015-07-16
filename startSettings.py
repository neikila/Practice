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


class StartSettings():

  def __init__(self, filename='INPUT.dat'):
    self.getFromXML(filename)

  def getFromXML(self, filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    model = root.find('model')
    self.velocity_iterations = int(model.find('velocity_iterations').text)
    self.position_iterations = int(model.find('position_iterations').text)
    self.hz = float(model.find('hz').text)
    self.epsilon_lin_velocity = float(model.find('epsilon_lin_velocity').text)
    self.g = float(model.find('g').text)

    ground = root.find('ground')
    self.ground_settings = GroundSettings(ground)

    body = root.find('body')
    self.lin_velocity_amplitude = float(body.find('lin_velocity_amplitude').text)
    self.lin_velocity_angle = float(body.find('lin_velocity_angle').text)
    self.angular_velocity = float(body.find('angular_velocity').text)
    self.angle = float(body.find('angle').text)
    self.position = get_point_from_xml('position', body)
    self.geometry = get_points_from_xml('geometry', body)

    target = root.find('target')
    self.target_point = get_point_from_xml('target_point', target) 
    self.target_position = get_point_from_xml('target_position', target) 
    self.left_side_of_target = get_points_from_xml('left_side_of_target', target) 
    self.right_side_of_target = get_points_from_xml('right_side_of_target', target) 
