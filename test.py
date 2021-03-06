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

xMiddleBlock = 12;
yMiddleBlock = 50;

blockWidth = 5;
blockHeight = 10;

# py version
world=b2World()
groundBody=world.CreateStaticBody(
    position=(0,-10),
    shapes=b2PolygonShape(box=(50,10)),
    )

groundBodyInTheMiddle=world.CreateStaticBody(
    position=(xMiddleBlock, yMiddleBlock),
    shapes=b2PolygonShape(box=(blockWidth, blockHeight)),
    )

body=world.CreateDynamicBody(position=(x0,y0))
box=body.CreatePolygonFixture(box=(8,8), density=density, friction=friction)

timeStep = 1.0 / 10.0
velocityIterations = 10;
positionIterations = 10;


# PYPY version
pypy_world = b2.World((gravity_X, gravity_Y), True)
pypy_ground = pypy_world.create_static_body(position=(0, -10))
pypy_ground.create_polygon_fixture(box=(50, 10))

pypy_middle_block = pypy_world.create_static_body(position=(xMiddleBlock, yMiddleBlock))
pypy_middle_block.create_polygon_fixture(box=(blockWidth, blockHeight))

pypy_box=b2.Fixture(
	shape=b2.Polygon(box=(8,8)),
    density=density,
    friction=friction)
pypy_body = pypy_world.create_dynamic_body(
    fixtures=pypy_box,
    position=(x0, y0))

print "   py", "      pypy", "     differ", "  Theoretical"

# print dir(pypy_body)

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

   x = body.position.x;
   pypy_x = pypy_body.position.x;
   differ_x = pypy_x - x;

   print ""
   print "Iteration numver:", i + 1, "time:", timeStep * (i + 1)
   print "X: ", ("%8.4f" % (x)), ("%8.4f" % (pypy_x)), ("%8.4f" % (differ_x))
   print "Y: ", ("%8.4f" % (y)), ("%8.4f" % (pypy_y)), ("%8.4f" % (differ))
   print "Velocity: "
   print "X: ", ("%8.4f" % (body.linearVelocity.x)), ("%8.4f" % (pypy_body.linear_velocity.x)) 
   print "Y: ", ("%8.4f" % (body.linearVelocity.y)), ("%8.4f" % (pypy_body.linear_velocity.y)) 