from __future__ import annotations
from build123d import *

def build_slider(params: dict) -> Part:
    """Строит монолитный слайдер с глубокой интеграцией узлов."""
    wall = params["wall"]
    tt = params["tablet_t"]
    st = params.get("slider_front_t", 6.0)
    sw = params.get("slider_f_width", 110.0)
    
    with BuildPart() as obj:
        # 1. Передний блок (L-профиль: блок в пазу + лапа)
        # Удлиняем направляющую часть до 60мм для стабильности
        with BuildSketch(Plane.YZ) as s1:
            with BuildLine():
                p1 = (0, st + 14)        # Верх лапы (у джойнта)
                p2 = (-6, st + 14)       # Толщина лапы 6мм
                p3 = (-6, st)            # Поверхность панели
                p4 = (-60, st)           # Конец блока в пазу (длина 60)
                p5 = (-60, 0)            # Дно паза
                p6 = (0, 0)              # Возврат к джойнту по дну паза
                Polyline(p1, p2, p3, p4, p5, p6, close=True)
            make_face()
        extrude(amount=sw/2, both=True)

        # 2. Шейка (Neck) - Центральный силовой элемент
        # Делаем её широкой (108мм), чтобы она почти заполняла паз 110мм
        # Длина шейки по Y теперь 60мм
        with BuildPart(mode=Mode.ADD):
            # Центр шейки в local Z = -wall/2
            with BuildSketch(Plane.YZ.offset(-wall/2)) as s2:
                 Rectangle(60, wall + 4, align=(Align.MAX, Align.CENTER))
            extrude(amount=108/2, both=True)

        # 3. Задняя плита (Back Plate)
        # Охватывает панель сзади. Ширина 130мм (шире паза 110мм)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ.offset(-wall)) as s3:
                with BuildLine():
                    p1 = (0, 0)          # Верх задней плиты
                    p2 = (0, -6)         # Толщина плиты 6мм
                    p3 = (-65, -6)       # Длина вниз (чуть длиннее блока)
                    p4 = (-65, 0)        # Плоскость прилегания к корпусу
                    Polyline(p1, p2, p3, p4, close=True)
                make_face()
            extrude(amount=130/2, both=True)

        # 4. Отверстия под болты-анкеры
        # Болты на x = +/- 50мм. В пазу шириной 110мм (x от -55 до +55) они проходят свободно.
        with BuildPart(mode=Mode.SUBTRACT):
            # Смещение на заднюю плиту (Z = -wall - 3)
            # Отверстия на Y = -30 (середина шейки)
            with Locations(Plane.XY.offset(-wall - 3) * Location((0, -30, 0))):
                for x_pos in [-50, 50]:
                    with Locations((x_pos, 0, 0)):
                        Cylinder(radius=5.5/2, height=30) # Сквозное отверстие сквозь слайдер

        RigidJoint("mount", obj.part, Location((0, 0, 0)))
    
    return obj.part        
    return obj.part