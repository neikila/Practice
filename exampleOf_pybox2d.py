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
worldAABB=b2AABB()
worldAABB.lowerBound.Set(-100.0, -100.0);
worldAABB.upperBound.Set(100.0, 100.0);

gravity = b2Vec2(0.0, -10.0);

doSleep = True

world = b2World(worldAABB, gravity, doSleep)

groundBodyDef = b2BodyDef();
groundBodyDef.position.Set(gravity_X, gravity_Y);

groundBody = world.CreateBody(groundBodyDef);

groundShapeDef = b2PolygonDef()

groundShapeDef.SetAsBox(50.0, 10.0);

groundBody.CreateShape(groundShapeDef);

bodyDef = b2BodyDef()
bodyDef.position.Set(x0, y0);
body = world.CreateBody(bodyDef);

shapeDef = b2PolygonDef()
shapeDef.SetAsBox(1.0, 1.0);

shapeDef.density = density;

shapeDef.friction = friction;

body.CreateShape(shapeDef);

body.SetMassFromShapes();

timeStep = 1.0 / 10.0
velocityIterations = 10;
positionIterations = 10;


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
print ("%8.4f" % (body.GetPosition().y)),( "%8.4f" % (pypy_body.position.y))

print dir(world)

# This is our little game loop.
for i in range(50):
   # Instruct the world to perform a single step of simulation. It is
   # generally best to keep the time step and iterations fixed.
   world.Step(timeStep, velocityIterations, positionIterations)
   world.ClearForces();

   pypy_world.step(timeStep, velocityIterations, positionIterations)
   pypy_world.clear_forces()

   y = body.GetPosition().y;
   pypy_y = pypy_body.position.y;
   differ = pypy_y - y;

   theoretical_y = (y0 + gravity_Y * (timeStep * (i + 1)) * (timeStep * (i + 1)) / 2);
   if theoretical_y < 1:
   	theoretical_y = 1;
   print ("%8.4f" % (y)), ("%8.4f" % (pypy_y)), ("%8.4f" % (differ)), ("%8.4f" % theoretical_y)