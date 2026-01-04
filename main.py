import sys
import os
import vtk
from PySide6.QtWidgets import QApplication
from src.ui import CADMainWindow
from projects.tablet_holder import ProjectAssembly

def setup_environment():
    """Настройка переменных окружения для стабильной работы 3D."""
    vtk.vtkObject.GlobalWarningDisplayOff()
    # Эти настройки специфичны для WSL/Linux с ускорением или без
    if "GALLIUM_DRIVER" not in os.environ:
        os.environ["GALLIUM_DRIVER"] = "d3d12"
    if "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "xcb"

def main():
    setup_environment()
    
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
