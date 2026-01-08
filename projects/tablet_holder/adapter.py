from __future__ import annotations
from build123d import *

def build_adapter(params: dict) -> Part:
    """Строит стальную пластину-адаптер, стягивающую половины корпуса."""
    w = params.get("adapter_w", 310.0) 
    hdx = params.get("adapter_hole_dist_x", 100.0)
    hdy = params.get("adapter_hole_dist_y", 100.0)
    hds = params.get("adapter_hole_step_x", 50.0)
    
    h_total = hdy + 40.0 # Отступ 20мм от отверстий сверху и снизу
    t = params.get("adapter_t", 2.0)
    bd = params.get("bolt_d", 4.9)
    
    with BuildPart() as obj:
        # Пластина-основание, теперь центрирована по Y относительно отверстий
        Box(w, h_total, t, align=(Align.CENTER, Align.CENTER, Align.MIN))
        
        # 1. Отверстия (все 12 штук)
        # Центр отверстий совпадает с сеткой в holder_half (Y = +/- hdy/2)
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Plane.XY.offset(t/2)):
                x_coords = [-(hdx/2 + hds * 2), -(hdx/2 + hds), -hdx/2, hdx/2, hdx/2 + hds, hdx/2 + hds * 2]
                with Locations(*[(x, y) for x in x_coords for y in [-hdy/2, hdy/2]]):
                     Cylinder(radius=bd/2, height=t+5)
        
        # Mount Joint: на ПЕРЕДНЕЙ грани пластины в мировом нуле держателя (Y=0)
        RigidJoint("mount", obj.part, Location((0, 0, t)))
    
    return obj.part
