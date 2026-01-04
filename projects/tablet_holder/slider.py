from __future__ import annotations
from build123d import *

def build_slider(params: dict) -> Part:
    """Строит монолитный слайдер с глубокой интеграцией узлов."""
    wall = params["wall"]
    tt = params["tablet_t"]
    w2 = wall / 2
    
    with BuildPart() as obj:
        # 1. Передний блок (L-профиль: платформа + хват)
        # Экструдируем на 110мм
        with BuildSketch(Plane.YZ) as s1:
            with BuildLine():
                # Профиль в плоскости YZ (Y-высота, Z-толщина)
                # Передняя панель начинается от w2 и идет вперед
                p1 = (25, w2)           # Верхняя внутренняя
                p2 = (25, w2 + 6)       # Верхняя внешняя
                p3 = (-50, w2 + 6)      # Нижняя внешняя (начало губы)
                p4 = (-50, w2 + 20)     # Край губы вперед
                p5 = (-56, w2 + 20)     # Толщина губы
                p6 = (-56, w2)          # Возврат к стенке корпуса
                Polyline(p1, p2, p3, p4, p5, p6, close=True)
            make_face()
        extrude(amount=110/2, both=True)

        # 2. Шейка (Neck) - Центральный силовой элемент
        # Создаем перекрытие (overlap) по 2мм с каждой стороны для прочности
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ) as s2:
                # Шейка должна быть выше и толще, чтобы "прошить" обе пластины
                # Высота 30, толщина wall + 4 (заходит по 2мм в каждую сторону)
                Rectangle(30, wall + 4, align=(Align.CENTER, Align.CENTER))
            extrude(amount=58/2, both=True)

        # 3. Задняя плита (Back Plate)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ) as s3:
                # Плоская плита сзади
                with BuildLine():
                    p1 = (25, -w2)
                    p2 = (25, -w2 - 6)
                    p3 = (-25, -w2 - 6)
                    p4 = (-25, -w2)
                    Polyline(p1, p2, p3, p4, close=True)
                make_face()
            extrude(amount=120/2, both=True)

        # 4. Отверстия под болты-анкеры
        with BuildPart(mode=Mode.SUBTRACT):
            # Смещение на заднюю плиту
            with Locations(Plane.XY.offset(-w2 - 3)):
                for x_pos in [-50, 50]:
                    with Locations((x_pos, 0, 0)):
                        Cylinder(radius=5.5/2, height=20)

        RigidJoint("mount", obj.part, Location((0, 0, 0)))
        
    return obj.part