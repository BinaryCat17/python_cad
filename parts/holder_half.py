from __future__ import annotations
from build123d import *
import math

def build_holder_half(
    tablet_w: float,
    tablet_h: float,
    tablet_t: float,
    wall: float,
    slot_t: float,
    visor_d: float,
    visor_angle: float = 20.0,
    claw_grip: float = 15.0,
    is_left: bool = True,
    adapter_size: float = 120.0,
    hole_dist: float = 100.0
) -> Part:
    """
    Строит половину корпуса держателя с углублением под VESA адаптер.
    """
    
    total_w = tablet_w + wall * 2
    half_w = total_w / 2
    total_h = tablet_h + wall * 2
    
    # Геометрия строится относительно стыка (X=0)
    x_min = -half_w if is_left else 0
    x_max = 0 if is_left else half_w
    center_x = (x_min + x_max) / 2
    side_x = -half_w if is_left else half_w - wall

    with BuildPart() as obj:
        # 1. Backplate
        with Locations((center_x, 0, wall/2)):
            Box(half_w, total_h, wall)
        
        # 2. Side Wall and Claw
        with Locations((side_x + wall/2, 0, wall + tablet_t/2)):
            Box(wall, total_h, tablet_t)
        
        # Claw
        claw_width = wall + claw_grip
        claw_center_x = side_x + claw_width/2 if is_left else side_x + wall - claw_width/2
        with Locations((claw_center_x, 0, wall + tablet_t + wall/2)):
            Box(claw_width, total_h, wall)

        # 3. Top and Bottom Rails
        for y_pos in [-total_h/2 + wall/2, total_h/2 - wall/2]:
            with Locations((center_x, y_pos, wall + tablet_t/2)):
                Box(half_w, wall, tablet_t)
            with Locations((center_x, y_pos, wall + tablet_t + wall/2)):
                Box(half_w, wall, wall)

        # 4. The Hood
        with Locations((center_x, total_h/2 - wall/2, wall + tablet_t + wall)):
            with Locations(Rotation(visor_angle, 0, 0)):
                Box(half_w, wall, visor_d, align=(Align.CENTER, Align.CENTER, Align.MIN))
        
        # 5. УГЛУБЛЕНИЕ ПОД АДАПТЕР (Recess)
        # Вырезаем в основной детали
        recess_align_x = Align.MAX if is_left else Align.MIN
        with Locations((0, 0, 0)):
            Box(adapter_size/2 + 0.5, adapter_size + 1.0, 3.0, 
                align=(recess_align_x, Align.CENTER, Align.MIN), 
                mode=Mode.SUBTRACT)

        # 6. ОТВЕРСТИЯ ПОД ПОТАЙНЫЕ БОЛТЫ (VESA 100)
        x_hole = hole_dist / 2
        hole_y_coords = [-hole_dist/2, hole_dist/2]
        for y_h in hole_y_coords:
            h_x = -x_hole if is_left else x_hole
            with Locations((h_x, y_h, 0)):
                # Сквозное отверстие M5
                Cylinder(radius=5.5/2, height=wall*2, mode=Mode.SUBTRACT)
                # Зенковка со стороны планшета (изнутри)
                # Потай должен быть снаружи или внутри? 
                # Обычно болты вкручиваются снаружи в кронштейн, 
                # но тут болт должен держать холдер. Значит потай внутри (под планшетом).
                with Locations((0, 0, wall)):
                    Cylinder(radius=10.0/2, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

        # 7. Вырез для зарядки
        if not is_left:
            with Locations((side_x + wall/2, 0, wall + tablet_t/2)):
                Box(wall * 3, 50, tablet_t * 0.8, mode=Mode.SUBTRACT)

        # 8. ДЖОИНТЫ
        # Находим грань точно на X=0
        join_face = obj.faces().filter_by(Axis.X, 0).sort_by(Axis.Z)[0]
        RigidJoint("center_joint", obj.part, join_face.location)
        
        # Джоинт адаптера на дне кармана (Z=3)
        # Направляем его "от детали" (в сторону отрицательного Z)
        RigidJoint("adapter_mount", obj.part, Location((0, 0, 3), (0, 0, 0)))
    
    return obj.part
