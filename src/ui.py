from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QLabel, QSlider, QDoubleSpinBox, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor
from src.renderer import CADRenderer

class CADMainWindow(QMainWindow):
    """Главное окно приложения. Управляет интерфейсом."""
    
    def __init__(self, assembly):
        super().__init__()
        self.setWindowTitle("Python CAD - Modular Architecture")
        self.resize(1280, 800)
        
        self.assembly = assembly
        
        # Центральный виджет и основной лейаут
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Сайдбар (UI)
        self.sidebar_layout = QVBoxLayout()
        sidebar_container = QWidget()
        sidebar_container.setLayout(self.sidebar_layout)
        sidebar_container.setFixedWidth(300)
        
        main_layout.addWidget(sidebar_container, 0)
        
        # Область рендеринга
        self.interactor = QtInteractor(self)
        main_layout.addWidget(self.interactor.interactor, 1)
        
        # Инициализируем рендерер
        self.renderer = CADRenderer(self.interactor)
        
        # Обновляем заголовок информацией о GPU
        gpu_info = self.renderer.get_gpu_info()
        self.setWindowTitle(f"Python CAD - [{gpu_info}]")
        
        # Настройка параметров
        self._setup_parameter_controls()
        
        # Первичная отрисовка
        self.refresh_view()

    def _setup_parameter_controls(self):
        """Создает контролы на основе параметров сборки."""
        group = QGroupBox("Parameters")
        form = QFormLayout(group)
        
        params_info = self.assembly.get_parameters()
        
        for key, (min_v, max_v, label) in params_info.items():
            current_val = self.assembly.params.get(key, min_v)
            
            spin = QDoubleSpinBox()
            spin.setRange(min_v, max_v)
            spin.setValue(current_val)
            spin.setSingleStep(1.0)
            
            # Связываем изменение значения с обновлением модели
            spin.valueChanged.connect(lambda v, k=key: self._on_param_changed(k, v))
            
            form.addRow(label, spin)
            
        self.sidebar_layout.addWidget(group)
        self.sidebar_layout.addStretch()

    def _on_param_changed(self, key, value):
        """Хендлер изменения параметра."""
        self.assembly.params[key] = value
        self.refresh_view()

    def refresh_view(self):
        """Обновляет геометрию через рендерер."""
        try:
            self.renderer.render_assembly(self.assembly)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Build Error: {e}")

    def closeEvent(self, event):
        """Чистая остановка интеркатора при закрытии окна."""
        self.interactor.close()
        super().closeEvent(event)
