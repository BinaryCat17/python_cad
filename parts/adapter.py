from __future__ import annotations
from build123d import *

def build_adapter(w: float = 120.0, h: float = 120.0, t: float = 5.0, hole_dist: float = 100.0, hole_d: float = 5.0) -> Part:
    """Строит адаптер крепления VESA с RigidJoint на задней грани."""
    with BuildPart() as obj:
        Box(w, h, t)
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(obj.faces().sort_by(Axis.Z)[-1]):
                with Locations(*[(x, y) for x in [-hole_dist/2, hole_dist/2] for y in [-hole_dist/2, hole_dist/2]]):
                    Cylinder(radius=hole_d/2, height=t*2)
        # RigidJoint на передней стенке (для крепления к холдеру)
        # Он должен смотреть 'навстречу' холдеру
        RigidJoint("mount", obj.part, Location(obj.faces().sort_by(Axis.Z)[-1].center(), (0, 0, 0)))
    
    return obj.part
