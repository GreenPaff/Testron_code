import sys
from PyQt6.QtWidgets import QApplication
from UI.main_window import LoginDialog, TestronApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    login_dialog = LoginDialog()
    if login_dialog.exec():
        username = login_dialog.get_username()
        main_window = TestronApp(username=username)
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)
