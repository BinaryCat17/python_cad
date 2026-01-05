from __future__ import annotations
from build123d import *

def build_slider(params: dict) -> Part:
    """Строит монолитный слайдер с усиленной Г-образной платформой."""
    wall, tt = params["wall"], params["tablet_t"]
    st, sw = params.get("slider_front_t", 6.0), params.get("slider_f_width", 140.0)
    
    # Планшет (18мм) начинается от Z=st (6.0)
    tablet_front_z = st + tt
    
    with BuildPart() as obj:
        # 1. Передняя панель + Зацеп (в передней выемке st)
        # Z: 0...st (в координатах джойнта, что соответствует 8...14 в корпусе)
        with BuildSketch(Plane.YZ) as s1:
            with BuildLine():
                # Y - вертикаль, Z - глубина
                # tablet_front_z (24.0) - поверхность экрана
                Polyline(
                    (0, 0),                   # Низ-зад передней панели
                    (-60, 0),                 # Верх-зад передней панели
                    (-60, st),                # Верх-перед панели (грань корпуса)
                    (-10, st),                # Переход к зацепу
                    (-10, tablet_front_z + 8),# Внешняя грань зацепа (верх)
                    (20, tablet_front_z + 12),# Кончик зацепа (отогнут на 4мм от экрана)
                    (20, tablet_front_z + 4), # Кончик зацепа (толщина, тоже с отступом)
                    (0, tablet_front_z),      # Внутренний угол (у основания экрана)
                    close=True
                )
            make_face()
        extrude(amount=sw/2, both=True)

        # 2. Шейка (Neck) - должна быть в толщине основной стенки (wall)
        # Z: -wall...0 (соответствует 0...8 в корпусе)
        with BuildPart(mode=Mode.ADD):
            with Locations((0, -30, -wall/2)):
                Box(108, 60, wall)

        # 3. Задняя плита (Back Plate) - должна быть ЗА корпусом
        # Z: -(wall+6)...-wall (соответствует -6...0 в мировых координатах)
        with BuildPart(mode=Mode.ADD):
            with Locations((0, -32.5, -wall - 3)):
                Box(170, 65, 6)

        # 4. Отверстия под болты
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Plane.XY.offset(-wall/2) * Location((0, -30, 0))):
                for x_pos in [-50, 50]:
                    with Locations((x_pos, 0, 0)):
                        Cylinder(radius=5.5/2, height=40, align=Align.CENTER)

        RigidJoint("mount", obj.part, Location((0, 0, 0)))
    
    return obj.part
