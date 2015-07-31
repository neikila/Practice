from Box2D import *
import sys
sys.path.extend(['..', '.'])

import pypybox2d as b2
from pypybox2d.common import *
import time

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

if len(sys.argv) > 1:
  amountOfBlocks = int(sys.argv[1])
else:
  amountOfBlocks = 0
print "Amount Of blocks:", amountOfBlocks

# py version
world=b2World()
groundBody=world.CreateStaticBody(
    position=(0,-10),
    shapes=b2PolygonShape(box=(50,10)),
    )
if amountOfBlocks > 0:
  groundBodyInTheMiddle=world.CreateStaticBody(
    position=(xMiddleBlock, yMiddleBlock),
    shapes=b2PolygonShape(box=(blockWidth, blockHeight)),
    )
if amountOfBlocks > 1:
  groundBodyInTheMiddle=world.CreateStaticBody(
    position=(-xMiddleBlock, yMiddleBlock + blockHeight),
    shapes=b2PolygonShape(box=(blockWidth, blockHeight)),
    )

body=world.CreateDynamicBody(position=(x0,y0))
box=body.CreatePolygonFixture(box=(8,8), density=density, friction=friction)

# PYPY version
pypy_world = b2.World((gravity_X, gravity_Y), True)
pypy_ground = pypy_world.create_static_body(position=(0, -10))
pypy_ground.create_polygon_fixture(box=(50, 10))

if amountOfBlocks > 0:
  pypy_middle_block = pypy_world.create_static_body(position=(xMiddleBlock, yMiddleBlock))
  pypy_middle_block.create_polygon_fixture(box=(blockWidth, blockHeight))
if amountOfBlocks > 1:
  pypy_middle_block = pypy_world.create_static_body(position=(-xMiddleBlock, yMiddleBlock + blockHeight))
  pypy_middle_block.create_polygon_fixture(box=(blockWidth, blockHeight))


pypy_box=b2.Fixture(
	shape=b2.Polygon(box=(8,8)),
    density=density,
    friction=friction)
pypy_body = pypy_world.create_dynamic_body(
    fixtures=pypy_box,
    position=(x0, y0))

iterationNumber = 80;

pypy_start = time.time()
for i in range(iterationNumber):
   pypy_world.step(timeStep, velocityIterations, positionIterations)
   pypy_world.clear_forces()
pypy_finish = time.time()
print "Result:", (pypy_finish - pypy_start) * 1000

start = time.time()
for i in range(iterationNumber):
   world.Step(timeStep, velocityIterations, positionIterations)
   world.ClearForces();
finish = time.time()
print "Result:", (finish - start) * 1000

print "Ratio pypy / py:", (pypy_finish - pypy_start) / (finish - start)
