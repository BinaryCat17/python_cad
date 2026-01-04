from __future__ import annotations
from build123d import *

def build_slider(params: dict) -> Part:
    """Строит монолитный слайдер с глубокой интеграцией узлов."""
    wall = params["wall"]
    tt = params["tablet_t"]
    st = params.get("slider_front_t", 6.0)
    sw = params.get("slider_f_width", 140.0) # 140мм
    
    with BuildPart() as obj:
        # 1. Передний блок (Лапа + блок в пазу)
        # Все эскизы на Plane.YZ (X=0) для строгой симметрии
        with BuildSketch(Plane.YZ) as s1:
            with BuildLine():
                p1 = (0, st + 14)        # Верх лапы
                p2 = (-6, st + 14)       # Толщина лапы
                p3 = (-6, st)            # Поверхность панели
                p4 = (-60, st)           # Конец блока в пазу
                p5 = (-60, 0)            # Дно паза
                p6 = (0, 0)              # Возврат
                Polyline(p1, p2, p3, p4, p5, p6, close=True)
            make_face()
        extrude(amount=sw/2, both=True)

        # 2. Шейка (Neck) - входит в паз 110мм
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ) as s2:
                 with BuildLine():
                     # По оси X эскиза (Y мир): от 0 до -60
                     # По оси Y эскиза (Z мир): от -wall-2 до 2 (охват панели wall)
                     p1 = (0, 2)
                     p2 = (-60, 2)
                     p3 = (-60, -wall-2)
                     p4 = (0, -wall-2)
                     Polyline(p1, p2, p3, p4, close=True)
                 make_face()
            extrude(amount=108/2, both=True)

        # 3. Задняя плита (Back Plate) - ширина 160мм
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ) as s3:
                with BuildLine():
                    # Прилегает к задней стенке (Z = -wall) и уходит вглубь до -wall-6
                    p1 = (0, -wall)
                    p2 = (0, -wall-6)
                    p3 = (-65, -wall-6)
                    p4 = (-65, -wall)
                    Polyline(p1, p2, p3, p4, close=True)
                make_face()
            extrude(amount=160/2, both=True)

        # 4. Отверстия под болты-анкеры
        # Болты на x = +/- 50мм.
        with BuildPart(mode=Mode.SUBTRACT):
            # Отверстия на Y = -30 (середина шейки)
            # Центр отверстий по Z (мировой) = -wall/2
            with Locations(Plane.XY.offset(-wall/2) * Location((0, -30, 0))):
                for x_pos in [-50, 50]:
                    with Locations((x_pos, 0, 0)):
                        Cylinder(radius=5.5/2, height=40, align=Align.CENTER)

        RigidJoint("mount", obj.part, Location((0, 0, 0)))
    
    return obj.part