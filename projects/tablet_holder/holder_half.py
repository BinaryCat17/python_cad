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
    
    # Высота: планшет + 60мм (было 48)
    th_total = th + 60.0 
    hw = (tw + wall * 2) / 2
    
    # Новые параметры для паза слайдера
    st = params.get("slider_front_t", 6.0)
    sw = params.get("slider_f_width", 110.0)
    panel_t = wall + st
    total_depth = tt + panel_t + vd
    
    with BuildPart() as obj:
        x_dir = -1 if is_left else 1
        align_x = Align.MAX if is_left else Align.MIN
        
        # 1. Задняя панель (утолщенная)
        Box(hw, th_total, panel_t, align=(align_x, Align.CENTER, Align.MIN))
        
        # 2. Боковая стенка (Ковш)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ.offset(x_dir * hw)) as s:
                with BuildLine():
                    y_top, y_bot = th_total/2, -th_total/2
                    p1, p2 = (y_bot, 0), (y_top, 0)
                    p3 = (y_top, total_depth)
                    p_bend = (y_top / 2, total_depth)
                    p4 = (y_bot, tt + panel_t)
                    Polyline(p1, p2, p3, p_bend, p4, close=True)
                make_face()
                # Скругляем внешний верхний угол ковша (p3)
                v_to_fillet = s.vertices().filter_by(Axis.Y, th_total/2 - 1, th_total/2 + 1).filter_by(Axis.Z, total_depth - 1, total_depth + 1)
                if v_to_fillet:
                    fillet(v_to_fillet, radius=20)
            extrude(amount=-x_dir * wall)

        # 3. Верхний козырек (Roof)
        roof_depth = total_depth - panel_t
        with BuildPart(mode=Mode.ADD):
            with Locations((0, th_total/2 - wall/2, panel_t + roof_depth/2)):
                Box(hw, wall, roof_depth, align=(align_x, Align.CENTER, Align.CENTER))
            
        # 4. Направляющие пазы
        tablet_bottom_y = th_total/2 - wall - th
        slot_top = tablet_bottom_y
        # Паз до самого низа панели
        slot_bottom = -th_total/2
        
        # Широкий паз под передний блок слайдера (sw = 140)
        with Locations((0, (slot_top + slot_bottom)/2, panel_t - st/2)):
            Box(sw/2 + 1, slot_top - slot_bottom, st + 0.5, align=(align_x, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Узкий сквозной паз под шейку (фиксировано 110мм для болтов)
        with Locations((0, (slot_top + slot_bottom)/2, panel_t/2)):
            Box(55, slot_top - slot_bottom, panel_t + 2, align=(align_x, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        
        # 5. Отверстия VESA и ниши под гайки
        xh = x_dir * 50.0
        for yh in [-50.0, 50.0]:
            with Locations((xh, yh, 0)):
                # Используем Align.MIN, чтобы цилиндр шел от 0 вверх на всю толщину
                Cylinder(radius=5.5/2, height=panel_t, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
                with BuildSketch(Plane.XY.offset(panel_t)) as s:
                    with Locations((xh, yh)):
                        RegularPolygon(radius=9.5/2, side_count=6)
                extrude(amount=-4.0, mode=Mode.SUBTRACT)

        # 6. ДЖОЙНТЫ
        # slider_start теперь на дне паза (Z = wall)
        RigidJoint("slider_start", obj.part, Location((0, tablet_bottom_y, wall)))
        RigidJoint("adapter_mount", obj.part, Location((0, 0, 3)))
    
    return obj.part
