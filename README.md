
The **Throw Optimization** project demonstrates modeling and optimizing a throw of body, determined by user.

<!--Two models are implemented: the first uses a simple external solver (included in the project), the second uses a SolidWorks geometry model and ANSYS to perform a finite-element analysis.-->
<!--The project optimizes both models and compares results.-->

**Note:** all workflows require python2.7, pybox2d (version '2.3b0') and PySide (version '1.2.1') installed.

Throwable body's (onward body), ground's, target's and some modell's parameters are set in xml document INPUT.dat in the relevant section <body>, <ground>, <target> and <model>

Body geometry is polygon which is described by local vertices (more than 3) in the section (<geometry>)
Body start velocity amplitude is set by field <lin_velocity_amplitude>
Body start velocity angle is set by field <lin_velocity_angle>
Body start angular velocity is set by field <angular_velocity>
Body start global position is decribed in section <position>

Ground is a number of connected edges
Edge ends' coordinates are set in section <vertices>
Two nearby vertices describe one edge
Vertices are global

Target object global position is set by field <position>
Point distance to which will be calculated in pSevev is set in section <target>
Target geometry is set by to section: <left_side_of_target> and <right_side_of_target>
Both are described by a number of local vertices (more than 3)

Modelling settings:
There are two conditions (sign) to stop modelling:
First is Body is stopped and second is Body's center of mass is out of modelling field
Body is consider to be stopped when it's linear velocity is below <epsilon_lin_velocity>
Modelling field is all space between leftmost point and rightmost point and above the
bottom of ground
Also it possible to change gravity constant be setting field <g>

Other settings (<velocity_iterations>, <position_iterations>, <hz>) are settings of box2d modelling engine.
It's higly recommended **not** to change them

Modelling is performed by python script model.py

Result of modelling is xml file OUTPUT.dat which contains points of trajectory in
section <field> and additional information in section <result>
Additional information, which is mentioned there are:
final distance between target and body at the last step - <distance>.
Distance between body and target is distance between target point and the closet body point
Minimal distance between body and target which was achivied while body was moving -
<min_distance>.
Body mass - <mass>.
Body inertia - <inertia>.
Body state which is describe by all vertices of body - <body>

Additional output is png image of throw trajectory with result distance printed in it.
This image is located in directory out (relativle from the location of python script)
<!--TODO Finished here-->

Disk geometry is described by 6 radii (_r1_ to _r6_) and 3 thickness (_t1_, _t3_, _t5_) parameters.
The disk is subjected to inertial load and additional load from blades mounted on the disk.
The parameters _r5_, _r6_, and _t5_ define the contact zone of rim and blades and cannot be varied.
Other parameters are design variables.
Considered performance characteristics are the disk mass, maximum radial displacement and maximum stress.

![](./doc/img/disk.png)

Additional parameters are: total mass of blades and disk rotation rate (required to calculate the inertial load), and disk material properties.

In general, the design problem is to choose such geometric parameters of the disk that provide the best values of objectives subject to constraints.
There are two objectives to be minimized: the disk mass and its radial displacement.
In order to prevent the contact between rotating and static components, the radial displacement is restricted to 0.3 mm.
To meet the strength requirements, equivalent maximum stress cannot exceed 600 MPa.
Additional parameters and 3 fixed geometry values mentioned above are not varied during optimization, but can be modified before solving (these parameters are added to workflow configuration).

The example considers two different computational models.
The first model is a system of ordinary differential equations defining the stress-strain behavior of the disk.
The [RotatingDisk](./RotatingDisk.p7wf) workflow uses an external solver included into the project to solve this system of differential equations by Runge-Kutta method.
The second model, implemented in the [RotatingDiskFEModel](./RotatingDiskFEModel.p7wf) workflow, utilizes a finite-element method to solve the same stress-strain problem.
It uses a SolidWorks geometry model (included into project) which is discretized in ANSYS to perform a finite-element analysis.

Both the [RotatingDisk](./RotatingDisk.p7wf) and [RotatingDiskFEModel](./RotatingDiskFEModel.p7wf) workflows can be run independently, model inputs are specified on the _Inputs_ pane in _Run_.
Note that [RotatingDiskFEModel](./RotatingDiskFEModel.p7wf) requires SolidWorks and ANSYS installed; before running this workflow, specify the path to the ANSYS executable on the _Configuration_ tab in _Run_.

The [OptimizationRotatingDisk](./OptimizationRotatingDisk.p7wf) workflow optimizes the model implemented in [RotatingDisk](./RotatingDisk.p7wf).
Results of this workflow are shown in the [OptimizationResults](./OptimizationResults.p7rep) report.

The [OptimizationRotatingDiskFEModel](./OptimizationRotatingDiskFEModel.p7wf) workflow optimizes the finite-element model implemented in [RotatingDiskFEModel](./RotatingDiskFEModel.p7wf).
This workflow also requires SolidWorks and ANSYS installed, and the path to the ANSYS executable should be specified before running it.
Results of this workflow are shown in the [OptimizationResultsFEModel](./OptimizationResultsFEModel.p7rep) report.

Finally, the [OptimizationResultsComparison](./OptimizationResultsComparison.p7rep) report compares the results obtained from [OptimizationRotatingDisk](./OptimizationRotatingDisk.p7wf) and [OptimizationRotatingDiskFEModel](./OptimizationRotatingDiskFEModel.p7wf).

**Note:** all reports in this project are initially empty. They are configured to update automatically when data appears in the project: run workflows, then refresh the reports to see results.
