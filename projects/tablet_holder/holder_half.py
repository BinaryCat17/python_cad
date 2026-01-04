from __future__ import annotations
from build123d import *
import math

def build_holder_half(params: dict, is_left: bool = True) -> Part:
    """Строит половину корпуса с открытым снизу пазом для слайдера."""
    
    tw, th, tt = params["tablet_w"], params["tablet_h"], params["tablet_t"]
    wall = params["wall"]
    aw = params["adapter_w"]
    hd = params["adapter_hole_dist"]
    vd = params["visor_d"]
    
    # Высота: планшет + 48мм
    th_total = th + 48.0 
    hw = (tw + wall * 2) / 2
    total_depth = tt + wall + vd
    
    with BuildPart() as obj:
        x_dir = -1 if is_left else 1
        align_x = Align.MAX if is_left else Align.MIN
        
        # 1. Задняя панель
        Box(hw, th_total, wall, align=(align_x, Align.CENTER, Align.MIN))
        
        # 2. Боковая стенка (Ковш)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ.offset(x_dir * hw)) as s:
                with BuildLine():
                    y_top, y_bot = th_total/2, -th_total/2
                    p1, p2 = (y_bot, 0), (y_top, 0)
                    p3 = (y_top, total_depth)
                    p_bend = (y_top / 2, total_depth)
                    p4 = (y_bot, tt + wall)
                    Polyline(p1, p2, p3, p_bend, p4, close=True)
                make_face()
            extrude(amount=-x_dir * wall)

        # 3. Верхний козырек (Roof)
        roof_depth = total_depth - wall
        with Locations((0, th_total/2 - wall/2, wall + roof_depth/2)):
            Box(hw, wall, roof_depth, align=(align_x, Align.CENTER, Align.CENTER))
            
        # 4. Направляющий паз (U-образный, открытый снизу)
        tablet_bottom_y = th_total/2 - wall - th
        slot_top = tablet_bottom_y
        slot_bottom = -th_total/2
        with Locations((0, (slot_top + slot_bottom)/2, wall/2)):
            # Ширина паза 60мм (30 на половину)
            Box(30, slot_top - slot_bottom, wall + 2, align=(align_x, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        
        # 5. Отверстия VESA и ниши под гайки
        xh = x_dir * 50.0
        for yh in [-50.0, 50.0]:
            with Locations((xh, yh, 0)):
                Cylinder(radius=5.5/2, height=wall, mode=Mode.SUBTRACT)
                with BuildSketch(Plane.XY.offset(wall)) as s:
                    with Locations((xh, yh)):
                        RegularPolygon(radius=9.5/2, side_count=6)
                extrude(amount=-4.0, mode=Mode.SUBTRACT)

        # 6. ДЖОЙНТЫ
        RigidJoint("slider_start", obj.part, Location((0, tablet_bottom_y, wall/2)))
        RigidJoint("adapter_mount", obj.part, Location((0, 0, 3)))
    
    return obj.part
