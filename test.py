from Box2D import *
import sys
sys.path.extend(['..', '.'])

import pypybox2d as b2
from pypybox2d.common import *

""" This is a simple example of building and running a simulation
    using Box2D. Here we create a large ground box and a small dynamic box
"""

# Presetting
y0 = 100;
x0 = 0;

friction = 0;
density = 1.0;

gravity_Y = -10.0;
gravity_X = 0;

# py version
world=b2World()
groundBody=world.CreateStaticBody(
    position=(0,-10),
    shapes=b2PolygonShape(box=(50,10)),
    )

body=world.CreateDynamicBody(position=(x0,y0))
box=body.CreatePolygonFixture(box=(1,1), density=density, friction=friction)

timeStep = 1.0 / 10.0
velocityIterations = 20;
positionIterations = 20;


# PYPY version
pypy_world = b2.World((gravity_X, gravity_Y), True)
pypy_ground = pypy_world.create_static_body(position=(0, -10))
pypy_ground.create_polygon_fixture(box=(50, 10))
pypy_box=b2.Fixture(
	shape=b2.Polygon(box=(1,1)),
    density=density,
    friction=friction)
pypy_body = pypy_world.create_dynamic_body(
    fixtures=pypy_box,
    position=(x0, y0))

print "py", "      pypy", "     differ", "  Theoretical"
print ("%8.4f" % (body.position.y)),( "%8.4f" % (pypy_body.position.y))

print dir(pypy_body)

# This is our little game loop.
for i in range(80):
   # Instruct the world to perform a single step of simulation. It is
   # generally best to keep the time step and iterations fixed.
   world.Step(timeStep, velocityIterations, positionIterations)
   world.ClearForces();

   pypy_world.step(timeStep, velocityIterations, positionIterations)
   pypy_world.clear_forces()

   y = body.position.y;
   pypy_y = pypy_body.position.y;
   differ = pypy_y - y;

   theoretical_y = (y0 + gravity_Y * (timeStep * (i + 1)) * (timeStep * (i + 1)) / 2);
   if theoretical_y < 1:
   	theoretical_y = 1;
   print ("%8.4f" % (y)), ("%8.4f" % (pypy_y)), ("%8.4f" % (differ)), ("%8.4f" % theoretical_y)
   print body.linearVelocity, pypy_body.linear_velocity