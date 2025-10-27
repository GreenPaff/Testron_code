import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget,
    QFormLayout, QLabel, QLineEdit, QPushButton, QTextEdit,
    QSpinBox, QComboBox,
    QDialog, QDialogButtonBox,
    QMainWindow, QStatusBar,
    QDockWidget, QListWidget, QListWidgetItem,
    QInputDialog, QMenu, QMessageBox,
    QToolButton, QHBoxLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction
#导入核心模块
from core.manual_generator import generate_data
# -----------------------------------------------------------------
# --- 登录对话框 Class (无变化) ---
# -----------------------------------------------------------------
class LoginDialog(QDialog):
    # (此部分代码与上一版完全相同，折叠)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Testron - 登录")
        self.setModal(True)
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.username_input.setText("user")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setText("12345")
        form_layout.addRow(QLabel("用户名:"), self.username_input)
        form_layout.addRow(QLabel("密码:"), self.password_input)
        link_layout = QHBoxLayout()
        self.forgot_password_button = QToolButton()
        self.forgot_password_button.setText("忘记密码?")
        self.forgot_password_button.setObjectName("LinkButton")
        self.forgot_password_button.clicked.connect(self.on_forgot_password)
        self.register_button = QToolButton()
        self.register_button.setText("注册账号")
        self.register_button.setObjectName("LinkButton")
        self.register_button.clicked.connect(self.on_register)
        link_layout.addWidget(self.forgot_password_button)
        link_layout.addStretch()
        link_layout.addWidget(self.register_button)
        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("登录")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        button_box.accepted.connect(self.check_login)
        button_box.rejected.connect(self.reject)
        layout.addLayout(form_layout)
        layout.addLayout(link_layout)
        layout.addWidget(self.error_label)
        layout.addWidget(button_box)
        self.username = ""

    def check_login(self):
        user = self.username_input.text()
        password = self.password_input.text()
        if user == "user" and password == "12345":
            self.username = user
            self.accept()
        else:
            self.error_label.setText("用户名或密码错误！")

    def get_username(self):
        return self.username

    def on_forgot_password(self):
        self.error_label.setText(" '忘记密码' 功能尚未实现。")
        print("Forgot Password clicked")

    def on_register(self):
        self.error_label.setText(" '注册账号' 功能尚未实现。")
        print("Register clicked")


# -----------------------------------------------------------------
# --- 设置对话框 Class (无变化) ---
# -----------------------------------------------------------------
class SettingsDialog(QDialog):
    # (此部分代码与上一版完全相同，折叠)
    def __init__(self, parent, current_theme, current_font_size, current_language):
        super().__init__(parent)
        self.setWindowTitle("应用设置")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(current_theme)
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(10, 20)
        self.font_size_spinbox.setValue(current_font_size)
        self.font_size_spinbox.setSuffix(" px")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文 (Chinese)", "English"])
        self.language_combo.setCurrentText(current_language)
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("颜色主题:"), self.theme_combo)
        form_layout.addRow(QLabel("字体大小:"), self.font_size_spinbox)
        form_layout.addRow(QLabel("语言 (Language):"), self.language_combo)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def get_settings(self):
        return {
            "theme": self.theme_combo.currentText(),
            "font_size": self.font_size_spinbox.value(),
            "language": self.language_combo.currentText()
        }
