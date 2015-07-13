import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument(
        '-v', '--visualised', 
        action='store_true', default=False, 
        help = 'visually modelling'
        )

namespace = parser.parse_args()
sys.argv = sys.argv[:1]

if namespace.visualised:
  from framework import *
  class Simulation(Framework):
    name = "Throwable" # Name of the class to display
    description = "First example" 

    def init_world(self):
      super(Simulation, self).__init__()

    def step_world(self, settings):
      Framework.Step(self, settings)

else:
  from Box2D import *
  class Simulation(object):
    
    def init_world(self):
      self.world = b2World(gravity=(0,-10), doSleep=True)

    def step_world(self, settings):
      timeStep = 1.0 / settings.hz
      self.world.Step(
          timeStep, 
          settings.velocity_iterations, 
          settings.position_iterations
          )

    def run(self):
      while not self.finalized:
        self.Step(self.start_settings)
