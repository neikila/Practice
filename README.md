The **Throw Optimization** project demonstrates modeling and optimizing a throw of body, determined by user.

**Note:** all workflows require python2.7, pybox2d (version '2.3b0') and PySide (version '1.2.1') installed.

*Settings*
Throwable body's (onward body), ground's, target's and some modell's parameters are set in xml document INPUT.dat in the relevant section <body>, <ground>, <target> and <model>

All sizes should be set accordingly with SI

Body settings:
1) geometry is polygon which is described by local vertices (more than 3) in the section <geometry>,   
2) start velocity amplitude is set by field <lin\_velocity\_amplitude>,   
3) start velocity angle is set by field <lin\_velocity\_angle>,   
4) start angular velocity is set by field <angular\_velocity>,   
5) start global position is decribed in section <position>.   

Ground settings:
Ground is a number of connected edges   
Edge ends' coordinates are set in section <vertices>   
Two nearby vertices describe one edge   
Vertices are global   

Target settings:
1) target object global position is set by field <position>,   
2) point distance to which will be calculated in pSevev is set in section <target>,   
3) target geometry is set by to section: <left\_side\_of\_target> and <right\_side\_of\_target>   
   (both are described by a number of local vertices (more than 3)).   

Modelling settings:   
1) there are two conditions (sign) to stop modelling:   
   1.1) first is Body is stopped
        (body is consider to be stopped when it's linear velocity is below <epsilon\_lin\_velocity>)
   1.2) second is Body's center of mass is out of modelling field      
        (modelling field is all space between leftmost point and rightmost point and above the bottom of ground)   
2) also it possible to change gravity constant be setting field <g>,   
3) other settings (<velocity\_iterations>, <position\_iterations>, <hz>) are settings of box2d modelling engine   
   (It's higly recommended **not** to change them).   

*Simulation*
Modelling is performed by python script model.py which use framework pybox2d for simulation world.   

Result of modelling is xml file OUTPUT.dat which contains points of trajectory in section <field> and additional information in section <result>   
Additional information, which is mentioned there is:   
1) final distance between target and body at the last step - <distance>   
   (distance between body and target is distance between target point and the closet body point),   
2) minimal distance between body and target which was achivied while body was moving - <min\_distance>,   
3) body mass - <mass>.   
4) body inertia - <inertia>.   
5) body state which is describe by all vertices of body - <body>.   

Additional output is png image of throw trajectory with result distance printed in it.   
This image is located in directory out (relativle from the location of python script)   
![](./doc/img/img0.png)

*Problem description*
In general, the design problem is to choose such start parameters of throw that provide the best values of objectives subject to constraints.   
Objective to be minimized: start kinetic energy.   
Hitting the target means that body stopped at the target point, so that distance should be less than 0.001 meter.   
Since the function of distance is complex and not analitic it is important to enable global optimisation be setting GlobalPhaseIntensity - parameter of block "Optimizer0".   
Only threee parameters among all mentioned above could be varied during optimization: <lin\_velocity\_amplitude>, <lin\_velocity\_angle>, <angular\_velocity>.   

Example contains three workflows:   
The [OneParameterVaried](./OneParameterVaries.p7wf) workflow use one parameter (linear velocity) to optimize model.   
Be carefull while changing angle in input file. There could be no solution in a range of value (For instance, in example angle = -pi/2 won't have solution)   
The [TwoParametersVaried](./TwoParametersVaries.p7wf) workflow use two parameters (linear velocity and angle) to optimize model.   
The [ThreeParametersVaried](./ThreeParametersVaries.p7wf) workflow use three parameters (linear velocity, angle and angular velocity) to optimize model.   

