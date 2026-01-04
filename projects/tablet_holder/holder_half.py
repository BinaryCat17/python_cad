from __future__ import annotations
from build123d import *

def build_holder_half(params: dict, is_left: bool = True) -> Part:
    """Строит половину корпуса, используя абсолютные координаты через Locations."""
    
    tw, th, tt = params["tablet_w"], params["tablet_h"], params["tablet_t"]
    wall = params["wall"]
    cg = params["claw_grip"]
    aw = params["adapter_w"]
    hd = params["adapter_hole_dist"]
    vd = params["visor_d"]
    va = params["visor_angle"]
    
    hw = (tw + wall * 2) / 2
    th_total = th + wall * 2
    
    with BuildPart() as obj:
        # 1. Задняя панель
        with Locations(((-hw if is_left else 0), -th_total/2, 0)):
            Box(hw, th_total, wall, align=(Align.MIN, Align.MIN, Align.MIN))
        
        # 2. Боковая стенка
        with Locations(((-hw if is_left else hw - wall), -th_total/2, wall)):
            Box(wall, th_total, tt, align=(Align.MIN, Align.MIN, Align.MIN))
            # Захват
            with Locations((0, 0, tt)):
                Box(wall + cg, th_total, wall, align=(Align.MIN if is_left else Align.MAX, Align.MIN, Align.MIN))

        # 3. Направляющие (Rails)
        for y_edge in [-th_total/2, th_total/2 - wall]:
            with Locations(((-hw if is_left else 0), y_edge, wall)):
                Box(hw, wall, tt, align=(Align.MIN, Align.MIN, Align.MIN))
                with Locations((0, 0, tt)):
                    Box(hw, wall, wall, align=(Align.MIN, Align.MIN, Align.MIN))

        # 4. Козырек (Hood)
        with Locations((0, th_total/2 - wall, wall + tt + wall)):
            with Locations(Rotation(va, 0, 0)):
                # Козырек должен расти от стыка
                Box(hw, wall, vd, align=(Align.MAX if is_left else Align.MIN, Align.MIN, Align.MIN))
        
        # 5. Углубление под адаптер (Recess)
        with Locations((0, 0, 0)):
            # Делаем вырез симметричным относительно 0 по Y
            Box(aw/2, aw, 3.0, align=(Align.MAX if is_left else Align.MIN, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 6. Отверстия VESA
        xh = -hd/2 if is_left else hd/2
        for yh in [-hd/2, hd/2]:
            with Locations((xh, yh, 0)):
                Cylinder(radius=5.5/2, height=wall, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
                with Locations((0, 0, wall)):
                    Cylinder(radius=10.0/2, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

        # 7. Вырез для зарядки
        if not is_left:
            with Locations((hw - wall, 0, wall + tt/2)):
                Box(wall * 3, 50, 10, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # 8. ДЖОЙНТЫ
        RigidJoint("seam", obj.part, Location((0, 0, 0)))
        RigidJoint("adapter_mount", obj.part, Location((0, 0, 3)))
    
    return obj.part
