from __future__ import annotations
from build123d import *

def build_slider(params: dict) -> Part:
    """Строит монолитный слайдер с глубокой интеграцией узлов."""
    wall = params["wall"]
    tt = params["tablet_t"]
    st = params.get("slider_front_t", 6.0)
    sw = params.get("slider_f_width", 110.0)
    
    with BuildPart() as obj:
        # 1. Передний блок (L-профиль: платформа + хват)
        # Z=0 - это дно паза. Блок идет от 0 до st.
        with BuildSketch(Plane.YZ) as s1:
            with BuildLine():
                # Профиль в плоскости YZ (Y-высота, Z-толщина)
                p1 = (45, 0)             # Верхняя внутренняя
                p2 = (45, st)            # Верхняя внешняя (вровень с панелью)
                p3 = (0, st)             # Нижняя внешняя (начало губы) - ТЕПЕРЬ НА Y=0
                p4 = (0, st + 14)        # Край губы вперед
                p5 = (-6, st + 14)       # Толщина губы
                p6 = (-6, 0)             # Возврат к дну паза
                Polyline(p1, p2, p3, p4, p5, p6, close=True)
            make_face()
        extrude(amount=sw/2, both=True)

        # 2. Шейка (Neck) - Центральный силовой элемент
        # Проходит сквозь панель толщиной wall.
        # Идем от -wall-2 до +2 для надежного перекрытия.
        with BuildPart(mode=Mode.ADD):
            # Смещаем эскиз шейки так, чтобы она была внутри панели
            # Центр шейки в local Z = -wall/2
            with BuildSketch(Plane.YZ.offset(-wall/2)) as s2:
                 Rectangle(30, wall + 4, align=(Align.CENTER, Align.CENTER))
            extrude(amount=58/2, both=True)

        # 3. Задняя плита (Back Plate)
        # Начинается от -wall и идет вглубь (назад)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ.offset(-wall)) as s3:
                with BuildLine():
                    p1 = (25, 0)
                    p2 = (25, -6)
                    p3 = (-25, -6)
                    p4 = (-25, 0)
                    Polyline(p1, p2, p3, p4, close=True)
                make_face()
            extrude(amount=120/2, both=True)

        # 4. Отверстия под болты-анкеры
        with BuildPart(mode=Mode.SUBTRACT):
            # Смещение на заднюю плиту (Z = -wall - 3)
            with Locations(Plane.XY.offset(-wall - 3)):
                for x_pos in [-50, 50]:
                    with Locations((x_pos, 0, 0)):
                        Cylinder(radius=5.5/2, height=20)

        RigidJoint("mount", obj.part, Location((0, 0, 0)))
        
    return obj.part