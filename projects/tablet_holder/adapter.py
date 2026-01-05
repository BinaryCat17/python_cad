from __future__ import annotations
from build123d import *

def build_adapter(params: dict) -> Part:
    """Строит стальную пластину-адаптер, стягивающую половины корпуса."""
    w = params.get("adapter_w", 310.0) # Увеличили до 310 мм
    # Высота 160 мм дает отступ 20 мм от центров отверстий (которые на +/- 60)
    h_total = 160.0 
    t = params.get("adapter_t", 2.0)
    
    with BuildPart() as obj:
        # Пластина-основание
        Box(w, h_total, t, align=(Align.CENTER, Align.CENTER, Align.MIN))
        
        # 1. Вырез под слайдер (маленькая выемка по нижнему краю)
        # Ширина 180 мм, глубина 10 мм. 
        with BuildPart(mode=Mode.SUBTRACT):
            # Позиционируем вырез ровно по нижнему краю (Y = -h_total/2)
            with Locations((0, -h_total/2, t/2)):
                Box(180, 10, t + 5, align=(Align.CENTER, Align.MIN, Align.CENTER))

        # 2. Отверстия (все 12 штук)
        # Центр отверстий должен совпадать с центром пластины (Y=0)
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Plane.XY.offset(t/2)):
                x_coords = [-140.0, -90.0, -40.0, 40.0, 90.0, 140.0]
                with Locations(*[(x, y) for x in x_coords for y in [-60.0, 60.0]]):
                     Cylinder(radius=5.5/2, height=t+5)
        
        # Mount Joint: на ПЕРЕДНЕЙ грани пластины (Z=t) в её центре (Y=0)
        RigidJoint("mount", obj.part, Location((0, 0, t)))
    
    return obj.part
