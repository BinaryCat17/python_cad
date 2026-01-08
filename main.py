import sys
import os
import vtk
import warnings
from PySide6.QtWidgets import QApplication
from src.ui import CADMainWindow
from projects.tablet_holder import ProjectAssembly

def setup_environment():
    """Настройка переменных окружения для стабильной работы 3D."""
    vtk.vtkObject.GlobalWarningDisplayOff()
    # Игнорируем предупреждения о депрекации в консоли
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Настройки для 4K и корректного масштабирования
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    
    # Эти настройки специфичны для WSL/Linux с ускорением или без
    if "GALLIUM_DRIVER" not in os.environ:
        os.environ["GALLIUM_DRIVER"] = "d3d12"
    if "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "xcb"

def main():
    setup_environment()
    
    # Включаем поддержку High DPI до создания QApplication
    from PySide6.QtCore import Qt
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    
    try:
        # Теперь CADMainWindow сам позаботится о загрузке параметров для ProjectAssembly
        window = CADMainWindow(ProjectAssembly)
        window.show()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
