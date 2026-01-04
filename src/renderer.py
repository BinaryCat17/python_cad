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

    def render_assembly(self, assembly):
        """Отрисовывает сборку."""
        root = assembly.build()
        self.clear()
        
        # Очищаем кэш если он слишком большой
        if len(self._mesh_cache) > 100:
            self._mesh_cache.clear()
        
        all_nodes = [root] + list(root.descendants)
        
        for i, node in enumerate(all_nodes):
            if not isinstance(node, Shape):
                continue
            
            # Если это Compound и у него есть дети, которые тоже являются Shape,
            # то мы пропускаем этот узел, так как его геометрия будет отрисована
            # через его детей (чтобы сохранить индивидуальные цвета и метки).
            # Исключение: если мы хотим видеть Compound целиком как одну деталь.
            has_shape_children = any(isinstance(c, Shape) for c in node.children)
            if has_shape_children:
                continue
                
            label = getattr(node, "label", "")
            name = label if label else f"part_{i}"
            raw_color = getattr(node, "color", "#ffffff")
            color = raw_color.to_tuple() if hasattr(raw_color, "to_tuple") else raw_color
            
            mesh = self._to_pyvista_mesh(node)
            
            self.plotter.add_mesh(
                mesh, color=color, name=name, 
                pbr=True, metallic=0.0, roughness=0.5,
                show_edges=False
            )
            
            edges = mesh.extract_feature_edges(feature_angle=20)
            if edges.n_cells > 0:
                self.plotter.add_mesh(edges, color="#111111", line_width=3.0, name=f"{name}_e")
            
        if self.first_render:
            self.plotter.view_isometric()
            self.first_render = False
            
        self.plotter.render()
