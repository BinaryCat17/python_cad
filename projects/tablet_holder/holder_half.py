from __future__ import annotations
from build123d import *
import math

def build_holder_half(params: dict, is_left: bool = True) -> Part:
    """Строит половину корпуса с прямой фиксирующей планкой."""
    
    tw, th, tt = params["tablet_w"], params["tablet_h"], params["tablet_t"]
    wall = params["wall"]
    aw = params["adapter_w"]
    hd = params["adapter_hole_dist"]
    vd = params["visor_d"]
    
    th_total = th + 60.0 
    hw = (tw + wall * 2) / 2
    
    st = params.get("slider_front_t", 6.0)
    sw = params.get("slider_f_width", 140.0)
    panel_t = wall + st
    total_depth = tt + panel_t + vd
    
    with BuildPart() as obj:
        x_dir = -1 if is_left else 1
        align_x = Align.MAX if is_left else Align.MIN
        
        # 1. Задняя панель
        Box(hw, th_total, panel_t, align=(align_x, Align.CENTER, Align.MIN))
        
        # 2. Боковая стенка (Ковш)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ.offset(x_dir * hw)) as s:
                with BuildLine():
                    p1, p2 = (-th_total/2, 0), (th_total/2, 0)
                    p3 = (th_total/2, total_depth)
                    p_bend = (th_total/4, total_depth)
                    p4 = (-th_total/2, panel_t + tt)
                    Polyline(p1, p2, p3, p_bend, p4, close=True)
                make_face()
            extrude(amount=-x_dir * wall)

        # 3. Верхний козырек (Roof)
        roof_depth = total_depth - panel_t
        with BuildPart(mode=Mode.ADD):
            with Locations((0, th_total/2 - wall/2, panel_t + roof_depth/2)):
                Box(hw, wall, roof_depth, align=(align_x, Align.CENTER, Align.CENTER))
            
            # 3.2 ФИКСИРУЮЩАЯ ПЛАНКА (Прямая, во всю ширину)
            bar_h, bar_t = 12.0, 8.0
            # Размещаем планку на краю планшета (Z = panel_t + tt)
            with Locations((0, th_total/2 - wall - bar_h/2, panel_t + tt + bar_t/2)):
                Box(hw, bar_h, bar_t, align=(align_x, Align.CENTER, Align.CENTER))

        # 4. Направляющие пазы
        tablet_bottom_y = th_total/2 - wall - th
        slot_top, slot_bottom = tablet_bottom_y, -th_total/2
        
        with Locations((0, (slot_top + slot_bottom)/2, panel_t - st/2)):
            Box(sw/2 + 1, slot_top - slot_bottom, st + 0.5, align=(align_x, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        with Locations((0, (slot_top + slot_bottom)/2, panel_t/2)):
            Box(55, slot_top - slot_bottom, panel_t + 2, align=(align_x, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        
        # 5. Отверстия VESA
        xh = x_dir * 50.0
        for yh in [-50.0, 50.0]:
            with Locations((xh, yh, 0)):
                Cylinder(radius=5.5/2, height=panel_t, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
                with BuildSketch(Plane.XY.offset(panel_t)) as s:
                    with Locations((xh, yh)): RegularPolygon(radius=9.5/2, side_count=6)
                extrude(amount=-4.0, mode=Mode.SUBTRACT)

        RigidJoint("slider_start", obj.part, Location((0, tablet_bottom_y, wall)))
        RigidJoint("adapter_mount", obj.part, Location((0, 0, 3)))
    
    return obj.part