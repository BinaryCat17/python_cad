from __future__ import annotations
from build123d import *

def build_slider(params: dict) -> Part:
    """Строит охватывающий пружинный зажим (Slider) с тыльной фиксацией."""
    wall = params["wall"]
    tt = params["tablet_t"]
    
    with BuildPart() as obj:
        # 1. Шейка (Neck) - часть, которая находится внутри паза
        # Ширина 58 (паз 60), толщина wall
        Box(58, 30, wall, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        
        # 2. Задняя фиксирующая пластина (Back Plate)
        # Находится с ТЫЛЬНОЙ стороны корпуса (Z < -wall/2)
        with Locations((0, 0, -wall/2)):
            # Ширина 80, чтобы не проваливалась в паз 60
            Box(80, 45, 5, align=(Align.CENTER, Align.CENTER, Align.MAX))
            # Анкеры для пружин на задней пластине
            for x_pos in [-40, 40]:
                with Locations((x_pos, 0, -5)):
                    Cylinder(radius=4, height=10, align=(Align.CENTER, Align.CENTER, Align.MAX))
                    # Шляпка
                    with Locations((0, 0, -10)):
                        Cylinder(radius=6, height=2, align=(Align.CENTER, Align.CENTER, Align.MAX))
        
        # 3. Лицевая прижимная часть (Front Claw)
        # Находится с ЛИЦЕВОЙ стороны корпуса (Z > wall/2)
        with Locations((0, 0, wall/2)):
            # Площадка-основание на лицевой стороне
            Box(110, 40, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Г-образный захват планшета (нижняя челюсть)
            with Locations((0, -20, 5)):
                # "Губа", которая заходит под планшет
                Box(110, 15, 8, align=(Align.CENTER, Align.MAX, Align.MIN))
                # Вертикальный бортик
                with Locations((0, -7.5, 8)):
                    Box(110, wall, tt + 5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 4. ДЖОЙНТЫ
        # Центрируем слайдер по его шейке
        RigidJoint("mount", obj.part, Location((0, 0, 0)))
        
    return obj.part