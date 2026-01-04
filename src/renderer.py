import pyvista as pv
import numpy as np
from build123d import Shape, Compound

class CADRenderer:
    """Класс, отвечающий исключительно за визуализацию геометрии в PyVista."""
    
    def __init__(self, plotter):
        self.plotter = plotter
        self.setup_scene()
        self.first_render = True
        self._mesh_cache = {} # Кэш для мешей, чтобы не пересчитывать их постоянно
        self._actor_count = 0

    def setup_scene(self):
        """Настройка освещения и фона."""
        self.plotter.set_background("#dcdcdc")
        self.plotter.remove_all_lights()
        
        # Равномерное освещение
        positions = [(100, 100, 150), (-100, 100, 150), (0, -100, -100)]
        for pos in positions:
            self.plotter.add_light(pv.Light(position=pos, intensity=1.1))
        
        self.plotter.enable_ssao(radius=15)
        self.plotter.enable_anti_aliasing("ssaa") # Включаем качественное сглаживание
        self.plotter.add_axes()

    def get_gpu_info(self):
        """Получает имя GPU из отчета VTK."""
        try:
            full_report = self.plotter.render_window.ReportCapabilities()
            for line in full_report.split("\n"):
                if "OpenGL renderer string" in line:
                    return line.split(":", 1)[1].strip()
            return "OpenGL Accelerator"
        except:
            return "D3D12 Adapter"

    def clear(self):
        """Очищает сцену."""
        for name in list(self.plotter.renderer.actors.keys()):
            if name != "axes":
                self.plotter.remove_actor(name)

    def _to_pyvista_mesh(self, shape: Shape, tolerance: float = 0.1):
        """Конвертирует форму build123d в PolyData с кэшированием."""
        # Используем hash геометрии как ключ
        shape_hash = hash(shape)
        if shape_hash in self._mesh_cache:
            return self._mesh_cache[shape_hash]

        verts, triangles = shape.tessellate(tolerance)
        points = np.array([[v.X, v.Y, v.Z] for v in verts])
        faces = []
        for tri in triangles:
            faces.append(3)
            faces.extend(tri)
        
        mesh = pv.PolyData(points, np.array(faces))
        self._mesh_cache[shape_hash] = mesh
        return mesh

    def render_shape(self, shape: Shape, name: str = None, color=None):
        """Рендерит одиночный Shape (Part) или рекурсивно обходит Compound."""
        self._actor_count += 1
        
        # 1. Получаем текущие свойства
        obj_label = getattr(shape, "label", name if name else f"Part_{self._actor_count}")
        obj_color = getattr(shape, "color", color)
        
        # 2. Если это Compound и у него НЕТ своего цвета - идем вглубь.
        # Если цвет есть - рендерим его как единое целое.
        is_compound = isinstance(shape, Compound)
        
        if is_compound and obj_color is None:
            try:
                # В build123d Compound итерируем
                for i, child in enumerate(shape):
                    child_name = f"{obj_label}_{i}"
                    self.render_shape(child, child_name, obj_color)
                return
            except:
                pass 

        # 3. Рендерим геометрию
        try:
            final_color = obj_color if obj_color else "#ffffff"
            mesh = self._to_pyvista_mesh(shape)
            
            if mesh.n_points == 0:
                return

            if hasattr(final_color, "to_tuple"):
                render_color = final_color.to_tuple()
            else:
                render_color = final_color
            
            actor_name = f"actor_{self._actor_count}"
            
            self.plotter.add_mesh(
                mesh, color=render_color, name=actor_name, 
                pbr=True, metallic=0.0, roughness=0.5,
                show_edges=False
            )
            
            edges = mesh.extract_feature_edges(feature_angle=20)
            if edges.n_cells > 0:
                self.plotter.add_mesh(edges, color="#111111", line_width=1.0, name=f"{actor_name}_e")
                
        except Exception as e:
            pass

    def update_scene(self, shapes):
        """Обновляет всю сцену на основе списка объектов или одного объекта."""
        self.clear()
        self._actor_count = 0
        
        if len(self._mesh_cache) > 500:
            self._mesh_cache.clear()
            
        if isinstance(shapes, (list, tuple)):
            for shape in shapes:
                self.render_shape(shape)
        elif shapes:
            self.render_shape(shapes)
            
        self.plotter.render()
        if hasattr(self.plotter, "update"):
            self.plotter.update()
        
        if self.first_render:
            self.plotter.view_isometric()
            self.first_render = False
