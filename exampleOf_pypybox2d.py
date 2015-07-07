import sys
sys.path.extend(['..', '.'])

import pypybox2d as b2
from pypybox2d.common import *
world = b2.World((0, -10), True)
ground = world.create_static_body(position=(0, -10))
ground.create_polygon_fixture(box=(50, 10))
box=b2.Fixture(
	shape=b2.Polygon(box=(1,1)),
    density=1,
    friction=0.1)
body = world.create_dynamic_body(
    fixtures=box,
    position=(0, 40))
for i in range(50):
    world.step(0.1, 10, 10)

    world.clear_forces()
    print "Position =",body.position.y