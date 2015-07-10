from parserForBox2DFramework import ParserForBox2dFramework

parser = ParserForBox2dFramework()
namespace = parser.parse_args()

if namespace.visualised:
  from framework import *
  class Decorator(Framework):
    name = "Throwable" # Name of the class to display
    description = "First example" 

    def get_the_world_set(self):
      super(Decorator, self).__init__()

    def make_world_step(self, settings):
      Framework.Step(self, settings)

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



