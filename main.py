import sys
import os
import vtk
from PySide6.QtWidgets import QApplication
from src.ui import CADMainWindow
from assemblies.tablet_holder_asm import TabletHolderAssembly

# Настройки платформы (важно для Linux/WSL)
vtk.vtkObject.GlobalWarningDisplayOff()
os.environ["GALLIUM_DRIVER"] = "d3d12"
os.environ["QT_QPA_PLATFORM"] = "xcb"

def main():
    app = QApplication(sys.argv)
    
    # Конфигурация
    assembly = TabletHolderAssembly()
    
    # Запуск
    window = CADMainWindow(assembly)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
