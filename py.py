from Box2D import *
import sys
sys.path.extend(['..', '.'])

import pypybox2d as b2
from pypybox2d.common import *
import time
from datetime import datetime
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


print "   py", "      pypy", "     differ", "  Theoretical"

# print dir(pypy_body)

# This is our little game loop.
a = datetime.now()
for i in range(80):
   # Instruct the world to perform a single step of simulation. It is
   # generally best to keep the time step and iterations fixed.
   world.Step(timeStep, velocityIterations, positionIterations)
   world.ClearForces();
b = datetime.now()
print "Result:", b.microsecond - a.microsecond