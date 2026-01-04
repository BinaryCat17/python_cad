import sys
import os
import vtk
from PySide6.QtWidgets import QApplication
from src.ui import CADMainWindow
from projects.tablet_holder import ProjectAssembly

# Настройки платформы
vtk.vtkObject.GlobalWarningDisplayOff()
os.environ["GALLIUM_DRIVER"] = "d3d12"
os.environ["QT_QPA_PLATFORM"] = "xcb"

def main():
    app = QApplication(sys.argv)
    
    # Инициализируем главное окно с классом сборки
    try:
        window = CADMainWindow(ProjectAssembly)
        window.show()
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
