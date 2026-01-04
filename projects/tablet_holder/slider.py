from __future__ import annotations
from build123d import *

def build_slider(params: dict) -> Part:
    """Строит монолитный слайдер с усиленной Г-образной платформой."""
    wall, tt = params["wall"], params["tablet_t"]
    st, sw = params.get("slider_front_t", 6.0), params.get("slider_f_width", 140.0)
    
    # Планшет (18мм) начинается от Z=st (6.0)
    tablet_front_z = st + tt
    
    with BuildPart() as obj:
        # 1. Основной профиль: Блок в пазу + Мощный Г-зацеп
        with BuildSketch(Plane.YZ) as s1:
            with BuildLine():
                # Y - вертикаль, Z - глубина
                Polyline(
                    (0, 0),                   # 1. Верх-зад блока в пазу
                    (-60, 0),                 # 2. Низ-зад блока
                    (-60, st),                # 3. Низ-перед блока (у панели)
                    (-10, st),                # 4. Толщина платформы снизу (10мм)
                    (-10, tablet_front_z + 8),# 5. Вылет платформы (Z=32)
                    (20, tablet_front_z + 8), # 6. Зацеп ВВЕРХ (высота 20мм)
                    (20, tablet_front_z),     # 7. Загиб к экрану (толщина 8мм)
                    (0, tablet_front_z),      # 8. Внутренний угол платформы
                    close=True
                )
            make_face()
        extrude(amount=sw/2, both=True)

        # 2. Шейка (108мм)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ) as s2:
                 Rectangle(60, wall + 4, align=(Align.MAX, Align.CENTER))
            extrude(amount=108/2, both=True)

        # 3. Задняя плита (170мм)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ.offset(-wall)) as s3:
                with BuildLine():
                    Polyline((0, 0), (0, -6), (-65, -6), (-65, 0), close=True)
                make_face()
            extrude(amount=170/2, both=True)

        # 4. Отверстия под болты
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Plane.XY.offset(-wall/2) * Location((0, -30, 0))):
                for x_pos in [-50, 50]:
                    with Locations((x_pos, 0, 0)):
                        Cylinder(radius=5.5/2, height=40, align=Align.CENTER)

        RigidJoint("mount", obj.part, Location((0, 0, 0)))
    
    return obj.part
