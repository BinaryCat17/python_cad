from __future__ import annotations
from build123d import *
import math

def build_holder_half(params: dict, is_left: bool = True) -> Part:
    """Строит половину корпуса. Анкеры перенесены на заднюю сторону."""
    
    tw, th, tt = params["tablet_w"], params["tablet_h"], params["tablet_t"]
    wall = params["wall"]
    aw = params["adapter_w"]
    hd = params["adapter_hole_dist"]
    vd = params["visor_d"]
    
    hw = (tw + wall * 2) / 2
    th_total = th + wall * 2
    total_depth = tt + wall + vd
    
    with BuildPart() as obj:
        x_dir = -1 if is_left else 1
        align_x = Align.MAX if is_left else Align.MIN
        
        # 1. Задняя панель (Z от 0 до wall)
        Box(hw, th_total, wall, align=(align_x, Align.CENTER, Align.MIN))
        
        # 2. Боковая стенка (Трапеция)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ.offset(x_dir * hw)) as s:
                with BuildLine():
                    y_top, y_bot = th_total/2, -th_total/2
                    p1, p2 = (y_bot, 0), (y_top, 0)
                    p3 = (y_top, total_depth)
                    p_bend = (y_top / 3, total_depth)
                    p4 = (y_bot, tt + wall)
                    Polyline(p1, p2, p3, p_bend, p4, close=True)
                make_face()
            extrude(amount=-x_dir * wall)

        # 3. Верхний козырек (Roof)
        roof_depth = total_depth - wall
        with Locations((0, th_total/2 - wall/2, wall + roof_depth/2)):
            Box(hw, wall, roof_depth, align=(align_x, Align.CENTER, Align.CENTER))
            
        # 4. Центральный паз (Slider Track) - сквозной
        with Locations((0, -th_total/4, wall/2)):
            Box(30, th_total/2 + 20, wall + 2, align=(align_x, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        
        # 5. Анкеры для пружин на ТЫЛЬНОЙ стороне (Z < 0)
        with Locations((x_dir * 40, 0, 0)):
            Cylinder(radius=4, height=12, align=(Align.CENTER, Align.CENTER, Align.MAX))
            # Шляпка, чтобы пружина не слетела
            with Locations((0, 0, -12)):
                Cylinder(radius=6, height=2, align=(Align.CENTER, Align.CENTER, Align.MAX))

        # 6. Углубление под адаптер (Recess)
        with Locations((0, 0, 0)):
            Box(aw/2 + 0.5, aw + 1.0, 3.0, align=(align_x, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 7. Отверстия VESA
        xh = x_dir * hd/2
        for yh in [-hd/2, hd/2]:
            with Locations((xh, yh, 0)):
                Cylinder(radius=5.5/2, height=wall, mode=Mode.SUBTRACT)

        # 8. ДЖОЙНТЫ
        RigidJoint("slider_axis", obj.part, Location((0, -th_total/2, wall)))
        RigidJoint("adapter_mount", obj.part, Location((0, 0, 3)))
    
    return obj.part