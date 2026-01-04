from __future__ import annotations
from build123d import *

def build_adapter(params: dict) -> Part:
    """Строит адаптер крепления VESA."""
    # Получаем параметры без дефолтных значений (вызовет ошибку если ключа нет, что и нужно)
    w = params["adapter_w"]
    h = params["adapter_h"]
    t = params["adapter_t"]
    hole_dist = params["adapter_hole_dist"]
    
    with BuildPart() as obj:
        Box(w, h, t)
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(obj.faces().sort_by(Axis.Z)[-1]):
                with Locations(*[(x, y) for x in [-hole_dist/2, hole_dist/2] for y in [-hole_dist/2, hole_dist/2]]):
                     Cylinder(radius=5.0/2, height=t*2)
        
        # Mount Joint: смотрит вперед (Positive Z)
        RigidJoint("mount", obj.part, Location(obj.faces().sort_by(Axis.Z)[-1].center(), (0, 0, 0)))
    
    return obj.part
