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


timeStep = 1.0 / 10.0
velocityIterations = 10;
positionIterations = 10;

world = b2.World((gravity_X, gravity_Y), True)
ground = world.create_static_body(position=(0, -10))
ground.create_polygon_fixture(box=(50, 10))

middle_block = world.create_static_body(position=(xMiddleBlock, yMiddleBlock))
middle_block.create_polygon_fixture(box=(blockWidth, blockHeight))

box=b2.Fixture(
	shape=b2.Polygon(box=(8,8)),
    density=density,
    friction=friction)
body = world.create_dynamic_body(
    fixtures=box,
    position=(x0, y0))

print "   py", "      pypy", "     differ", "  Theoretical"

# print dir(pypy_body)

# This is our little game loop.
for i in range(80):
   world.step(timeStep, velocityIterations, positionIterations)
   world.clear_forces()

   y = body.position.y;

   x = body.position.x;

   print ""
   print "Iteration numver:", i + 1, "time:", timeStep * (i + 1)
   print "X: ", ("%8.4f" % (x))
   print "Y: ", ("%8.4f" % (y))
   print "Velocity: "
   print "X: ", ("%8.4f" % (body.linear_velocity.x)) 
   print "Y: ", ("%8.4f" % (body.linear_velocity.y)) 