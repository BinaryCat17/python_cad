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
    
    th_min = 205.0 # Минимальная высота планшета для прижатия (было 195)
    th_total = th + 68.0 # Увеличиваем корпус (было th + 38)
    hw = (tw + wall * 2) / 2
    
    st = params.get("slider_front_t", 6.0)
    sw = params.get("slider_f_width", 140.0)
    bd = params.get("bolt_d", 4.9)
    nw = params.get("nut_w", 8.0)
    nut_r = nw / math.sqrt(3) # Радиус описанной окружности для шестигранника "под ключ" nw
    
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
                with BuildLine() as bl:
                    p1 = (-th_total/2, 0)
                    p2 = (th_total/2, 0)
                    p3 = (th_total/2, total_depth)
                    pb = (th_total/4, total_depth)
                    p4 = (-th_total/2, panel_t + tt)
                    Polyline(p1, p2, p3, pb, p4, close=True)
                    
                    # Правильный выбор вершин в 2D эскизе
                    def get_closest(pts, target):
                        return sorted(pts, key=lambda p: (p.X - target[0])**2 + (p.Y - target[1])**2)[0]
                    
                    v_middle = get_closest(bl.vertices(), pb)
                    v_bottom = get_closest(bl.vertices(), p4)
                    
                    fillet(v_middle, radius=50.0)
                    fillet(v_bottom, radius=15.0)
                make_face()
            extrude(amount=-x_dir * wall)

        # 3. Верхний козырек (Roof)
        roof_depth = total_depth - panel_t
        with BuildPart(mode=Mode.ADD):
            # Увеличиваем толщину козырька до panel_t (было wall)
            with Locations((0, th_total/2 - panel_t/2, panel_t + roof_depth/2)):
                Box(hw, panel_t, roof_depth, align=(align_x, Align.CENTER, Align.CENTER))
            
            # 3.1 ОТВЕРСТИЯ В КОЗЫРЬКЕ (3 штуки для стяжки пластиной)
            # Теперь центрируем по новой толщине panel_t
            for x_off in [40.0, 90.0, 140.0]:
                xh = x_dir * x_off
                with Locations((xh, th_total/2 - panel_t/2, panel_t + tt + 30.0)):
                    # Поворачиваем цилиндр вдоль оси Y (90 градусов по X)
                    Cylinder(radius=bd/2, height=panel_t * 2, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

            # 3.2 ФИКСИРУЮЩАЯ ПЛАНКА (Прямая, во всю ширину)
            bar_h, bar_t = 12.0, 18.0
            # Размещаем планку вплотную к утолщенному козырьку
            with BuildPart(mode=Mode.ADD) as bar_obj:
                with Locations((0, th_total/2 - panel_t - bar_h/2, panel_t + tt + bar_t/2)):
                    Box(hw, bar_h, bar_t, align=(align_x, Align.CENTER, Align.CENTER))
                # Скругляем внутреннее ребро
                inner_edge = bar_obj.edges().filter_by(Axis.X).sort_by(Axis.Y)[0:2].sort_by(Axis.Z)[0]
                fillet(inner_edge, radius=5.0)

        # 4. Направляющие пазы
        tablet_bottom_y = th_total/2 - wall - th
        # Верх паза для прижатия 205мм
        slot_top = th_total/2 - wall - th_min
        slot_bottom = -th_total/2 # Паз идет до самого низа (который теперь ниже на 30мм)
        
        with Locations((0, (slot_top + slot_bottom)/2, panel_t - st/2)):
            Box(sw/2 + 1, slot_top - slot_bottom, st + 0.5, align=(align_x, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        with Locations((0, (slot_top + slot_bottom)/2, panel_t/2)):
            Box(55, slot_top - slot_bottom, panel_t + 2, align=(align_x, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        
        # 5. Отверстия под адаптер (теперь 6 на каждую половину, итого 12)
        # 5.1 Отверстия: 3 колонки (40, 90, 140) в 2 ряда (-60, 60)
        for x_off in [40.0, 90.0, 140.0]:
            xh = x_dir * x_off
            for yh in [-60.0, 60.0]:
                with Locations((xh, yh, 0)):
                    # Сквозное отверстие
                    Cylinder(radius=bd/2, height=panel_t, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
                    # Гнездо под гайку на лицевой стороне
                    with BuildSketch(Plane.XY.offset(panel_t)) as s:
                        with Locations((xh, yh)): RegularPolygon(radius=nut_r, side_count=6)
                    extrude(amount=-4.0, mode=Mode.SUBTRACT)

        RigidJoint("slider_start", obj.part, Location((0, tablet_bottom_y, wall)))
        # Джойнт на задней поверхности (Z=0) в центре панели (Y=0)
        RigidJoint("adapter_mount", obj.part, Location((0, 0, 0)))
    
    return obj.part