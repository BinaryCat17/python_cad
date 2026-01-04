from __future__ import annotations
from build123d import *

def build_holder_half(params: dict, is_left: bool = True) -> Part:
    """Строит половину корпуса в локальных координатах. Стык всегда в X=0."""
    
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
        # Направление роста: левая в -X, правая в +X
        x_dir = -1 if is_left else 1
        align_x = Align.MAX if is_left else Align.MIN
        
        # 1. Задняя панель
        Box(hw, th_total, wall, align=(align_x, Align.CENTER, Align.MIN))
        
        # 2. Боковая стенка и захват
        # Смещаемся к внешнему краю
        with Locations((x_dir * hw, 0, wall)):
            side_align = Align.MIN if is_left else Align.MAX
            Box(wall, th_total, tt, align=(side_align, Align.CENTER, Align.MIN))
            with Locations((0, 0, tt)):
                Box(wall + cg, th_total, wall, align=(side_align, Align.CENTER, Align.MIN))

        # 3. Направляющие (Rails)
        for y_pos in [-th_total/2, th_total/2 - wall]:
            with Locations((0, y_pos + wall/2, wall)):
                Box(hw, wall, tt, align=(align_x, Align.CENTER, Align.MIN))
                with Locations((0, 0, tt)):
                    Box(hw, wall, wall, align=(align_x, Align.CENTER, Align.MIN))

        # 4. Козырек (Hood)
        with Locations((0, th_total/2 - wall, wall + tt + wall)):
            with Locations(Rotation(va, 0, 0)):
                Box(hw, wall, vd, align=(align_x, Align.MIN, Align.MIN))
        
        # 5. Углубление под адаптер (Recess)
        # Возвращаем допуски +0.5 и +1.0 для легкой сборки после печати
        with Locations((0, 0, 0)):
            Box(aw/2 + 0.5, aw + 1.0, 3.0, align=(align_x, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 6. Отверстия VESA
        x_dir = -1 if is_left else 1
        xh = x_dir * hd/2
        for yh in [-hd/2, hd/2]:
            with Locations((xh, yh, 0)):
                Cylinder(radius=5.5/2, height=wall, mode=Mode.SUBTRACT)
                with Locations((0, 0, wall)):
                    Cylinder(radius=10.0/2, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

        # 7. Скругления (Fillets)
        ext_edges = obj.edges().filter_by(Axis.Z).sort_by(Axis.X)
        target_edge = ext_edges[0] if is_left else ext_edges[-1]
        fillet(target_edge, radius=wall/2)

        # 8. Вырез для зарядки
        if not is_left:
            # Возвращаем оригинальный глубокий вырез
            with Locations((hw - wall/2, 0, wall + tt/2)):
                Box(wall * 3, 50, tt * 0.8, mode=Mode.SUBTRACT)

        # 9. ДЖОЙНТЫ
        # Находится на дне углубления (Z=3)
        RigidJoint("adapter_mount", obj.part, Location((0, 0, 3)))
    
    return obj.part