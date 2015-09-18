"""
BSpline definition in FreeCAD
Every points is part of a list of FreeCAD.Vector class.
The example uses a hypotrochoid
https://en.wikipedia.org/wiki/Hypotrochoid
"""
import FreeCAD as FC
from FreeCAD import Base
import Draft
import Mesh
import MeshPart
import numpy as np
import os
from numpy import sin, cos, pi


def param_curve(t, R, r, d):
    """Coordinates of a hypotrochoid for parameters t, R, r and d"""
    x = (R - r)*cos(t) + d*cos((R - r)/r*t)
    y = (R - r)*sin(t) - d*sin((R - r)/r*t)
    z = 3*sin(t)
    return x, y, z


#%%
doc = App.newDocument("Mana_item")
gui_doc = Gui.getDocument("Mana_item")

## Hypotrochoid
npts = 200
R = 5.
r = 3.
d = 5.
t = np.linspace(0, 6*pi, npts)
x_vec, y_vec, z_vec = param_curve(t, R, r, d)
pts = [FC.Vector(x_vec[k], y_vec[k], z_vec[k]) for k in range(npts)]
path = Draft.makeBSpline(pts, closed=True, support=None)

## Circle perpendicular to the parametric curve
rad = 0.5
vec = pts[1] - pts[0]
ang = vec.getAngle(FC.Vector(vec.x, vec.y, 0))*np.sign(vec.z)
ang = ang + pi/2
axis = vec.cross(FC.Vector(vec.x, vec.y, 0))
place = FC.Placement()
# Quaternion in FreeCAD
# q1 = sin(angle/2)*axis_1
# q2 = sin(angle/2)*axis_2
# q3 = sin(angle/2)*axis_3
# q4 = cos(angle/2)
place.Rotation = (sin(ang/2)*axis[0],
                  sin(ang/2)*axis[1],
                  sin(ang/2)*axis[2],
                  cos(ang/2))
place.Base = pts[0]
circle = Draft.makeCircle(radius=rad, placement=place)

## Sweep
tube = doc.addObject('Part::Sweep','Sweep')
tube.Sections = circle
tube.Spine = path
tube.Solid = True
tube.Frenet = False

## Boolean operation
sphere = doc.addObject("Part::Sphere","Sphere")
cut = doc.addObject("Part::Cut","Cut")
cut.Base = sphere
cut.Tool = tube
doc.recompute()

## Aesthetic changes
Gui.SendMsgToActiveView("ViewFit")
gui_doc.activeView().viewAxometric()
# Cut sphere
gui_doc.getObject("Cut").Transparency = 30
gui_doc.getObject("Cut").ShapeColor = (0.00,0.33,0.50)
gui_doc.getObject("Cut").DisplayMode = "Shaded"
# Tube
gui_doc.getObject("Sweep").ShapeColor = (0.00,0.33,0.00)
gui_doc.getObject("Sweep").DisplayMode = "Shaded"
gui_doc.getObject("Sweep").Visibility = True
# Sketches
gui_doc.getObject("Circle").Visibility = False
gui_doc.getObject("BSpline").Visibility = False


## Save file
fname = "/mana_item"
file_path = os.path.dirname(__file__) + fname + ".FCStd"
stl_path = os.path.dirname(__file__) + fname + ".STL"
stl_path2 = os.path.dirname(__file__) + fname + "_fine" + ".STL"
doc.saveAs(file_path)
Mesh.export([tube, cut], stl_path)
print("Successfully generate the mana item!")


## Manually handle meshes
cut_mesh = doc.addObject("Mesh::Feature","Cut mesh")
tube_mesh = doc.addObject("Mesh::Feature","Sweep mesh")
cut_mesh.Mesh = MeshPart.meshFromShape(Shape=cut.Shape, Fineness=2,
                    SecondOrder=0, Optimize=1, AllowQuad=0)
tube_mesh.Mesh = MeshPart.meshFromShape(Shape=tube.Shape, Fineness=2,
                    SecondOrder=0, Optimize=1, AllowQuad=0)
Mesh.export([tube_mesh, cut_mesh], stl_path2)
doc.cut_mesh.Visibility = False
doc.tube_mesh.Visibility = False