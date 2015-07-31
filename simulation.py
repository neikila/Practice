import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument(
        '-v', '--visualised', 
        action='store_true', default=False, 
        help = 'visually modelling'
        )

namespace = parser.parse_args()

if namespace.visualised:
  # This is for testing
  # It requiers pybox2d testing scripts (https://github.com/pybox2d/pybox2d/tree/master/examples):
  #  - pygame_framework.py
  #  - framework.py
  #  - settings.py

  # Clearing arguments because pybox2d will raise an error if it get any of arguments mentioned above
  # We are also aren't going to use any of pybox2d arguments
  sys.argv = sys.argv[:1]
  from framework import *
  class Simulation(Framework):
    name = "Throwable" # Name of the class to display
    description = "First example" 
    namespace = namespace

    def init_world(self):
      super(Simulation, self).__init__()

    def step_world(self, settings):
      Framework.Step(self, settings)

else:
  from Box2D import *
  class Simulation(object):
    namespace = namespace
    
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
