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
        # Z=0 - это дно паза.
        with BuildSketch(Plane.YZ) as s1:
            with BuildLine():
                # p1-p2: Верхний торец лапы (над панелью)
                # p3-p4: Переход к поверхности блока (вровень с панелью)
                # p5-p6: Нижний торец блока (в глубине паза)
                p1 = (0, st + 14)        # Верх лапы (у джойнта)
                p2 = (-6, st + 14)       # Толщина лапы 6мм
                p3 = (-6, st)            # Поверхность панели
                p4 = (-40, st)           # Конец блока в пазу (длина 40)
                p5 = (-40, 0)            # Дно паза
                p6 = (0, 0)              # Возврат к джойнту по дну паза
                Polyline(p1, p2, p3, p4, p5, p6, close=True)
            make_face()
        extrude(amount=sw/2, both=True)

        # 2. Шейка (Neck) - Центральный силовой элемент
        # Должна быть внутри блока (Y от 0 до -40). Сделаем её 30мм.
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ.offset(-wall/2)) as s2:
                 # Align.MAX по Y прижмет прямоугольник к 0 и он пойдет вниз до -30
                 Rectangle(30, wall + 4, align=(Align.MAX, Align.CENTER))
            extrude(amount=58/2, both=True)

        # 3. Задняя плита (Back Plate)
        # Также идет вниз от 0 до -35
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ.offset(-wall)) as s3:
                with BuildLine():
                    p1 = (0, 0)
                    p2 = (0, -6)
                    p3 = (-35, -6)
                    p4 = (-35, 0)
                    Polyline(p1, p2, p3, p4, close=True)
                make_face()
            extrude(amount=120/2, both=True)

        # 4. Отверстия под болты-анкеры
        with BuildPart(mode=Mode.SUBTRACT):
            # Смещение на заднюю плиту (Z = -wall - 3)
            # Отверстия сместим чуть ниже (Y = -20), чтобы они были в центре плиты
            with Locations(Plane.XY.offset(-wall - 3) * Location((0, -20, 0))):
                for x_pos in [-50, 50]:
                    with Locations((x_pos, 0, 0)):
                        Cylinder(radius=5.5/2, height=20)

        RigidJoint("mount", obj.part, Location((0, 0, 0)))
    
    return obj.part        
    return obj.part