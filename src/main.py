from app import App
import ctypes
import platform

if platform.system() == "Windows":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception as e:
        # Option de secours pour les versions plus anciennes de Windows
        ctypes.windll.user32.SetProcessDPIAware()
        

if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
