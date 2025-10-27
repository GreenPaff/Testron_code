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


# -----------------------------------------------------------------
# --- 主窗口 Class (有改动) ---
# -----------------------------------------------------------------
class TestronApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.current_theme = "Dark"
        self.current_font_size = 14
        self.current_language = "中文 (Chinese)"
        self.username = username
        self.history_file_path = f"{self.username}_history.json"
        self.history_data = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Testron (用户: {self.username})")
        self.setGeometry(300, 300, 1000, 700)

        self.create_menu_bar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.create_history_dock()

        central_widget = QWidget()
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.manual_tab = self.create_manual_tab()
        self.ai_tab = self.create_ai_tab()
        self.tabs.addTab(self.manual_tab, "手动精确定制")
        self.tabs.addTab(self.ai_tab, "AI 智能解析")
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(QLabel("生成结果:"))
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setText("尚未生成...")
        main_layout.addWidget(self.result_output)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.load_history_from_file()

        # synchronize view menu and dock
        self.view_history_action.toggled.connect(self.history_dock.setVisible)
        self.history_dock.visibilityChanged.connect(self.view_history_action.setChecked)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("文件")
        clear_action = QAction("清空全部历史...", self)
        clear_action.triggered.connect(self.clear_all_history)
        file_menu.addAction(clear_action)
        file_menu.addSeparator()
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("编辑")
        settings_action = QAction("设置...", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        edit_menu.addAction(settings_action)

        view_menu = menu_bar.addMenu("视图")
        self.view_history_action = QAction("历史面板", self)
        self.view_history_action.setCheckable(True)
        self.view_history_action.setChecked(True)
        view_menu.addAction(self.view_history_action)

        help_menu = menu_bar.addMenu("帮助")
        about_action = QAction("关于...", self)
        help_menu.addAction(about_action)

    def create_history_dock(self):
        self.history_dock = QDockWidget("生成历史", self)
        self.history_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.history_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.history_list_widget = QListWidget()
        self.history_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list_widget.customContextMenuRequested.connect(self.show_history_context_menu)
        self.history_dock.setWidget(self.history_list_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.history_dock)
        self.history_list_widget.itemClicked.connect(self.on_history_item_clicked)

    def show_history_context_menu(self, position):
        item = self.history_list_widget.itemAt(position)
        if item:
            context_menu = QMenu(self)
            delete_action = QAction("删除", self)
            delete_action.triggered.connect(lambda: self.delete_history_item(item))
            context_menu.addAction(delete_action)
            context_menu.exec(self.history_list_widget.viewport().mapToGlobal(position))

    def delete_history_item(self, item: QListWidgetItem):
        row = self.history_list_widget.row(item)
        if row == -1:
            return
        self.history_list_widget.takeItem(row)
        try:
            del self.history_data[row]
        except IndexError:
            self.status_bar.showMessage("错误: 历史数据与UI不同步！", 5000)
            return
        self.save_history_to_file()
        self.status_bar.showMessage(f"已删除: {item.text()}", 3000)

    def load_history_from_file(self):
        try:
            with open(self.history_file_path, 'r', encoding='utf-8') as f:
                self.history_data = json.load(f)
            self.history_list_widget.clear()
            for entry in self.history_data:
                item = QListWidgetItem(entry.get("name", "未命名"))
                item.setData(Qt.ItemDataRole.UserRole, entry.get("generated_data", ""))
                self.history_list_widget.addItem(item)
            if self.history_data:
                self.history_list_widget.setCurrentRow(self.history_list_widget.count() - 1)
                self.on_history_item_clicked(self.history_list_widget.currentItem())
                self.status_bar.showMessage(f"已为用户 '{self.username}' 加载 {len(self.history_data)} 条历史记录")
            else:
                self.status_bar.showMessage(f"欢迎, {self.username}! 历史记录为空。")
        except FileNotFoundError:
            self.status_bar.showMessage(f"欢迎, {self.username}! 未找到历史文件。")
            self.history_data = []
        except json.JSONDecodeError:
            self.status_bar.showMessage("错误: 历史文件已损坏。")
            self.history_data = []

    def on_history_item_clicked(self, item: QListWidgetItem):
        generated_data = item.data(Qt.ItemDataRole.UserRole)
        if generated_data:
            self.result_output.setText(generated_data)
            self.status_bar.showMessage(f"已加载: {item.text()}", 3000)

    def add_history_item(self, constraints: dict, generated_data: str, custom_name: str):
        item = QListWidgetItem(custom_name)
        item.setData(Qt.ItemDataRole.UserRole, generated_data)
        self.history_list_widget.insertItem(0, item)
        self.history_list_widget.setCurrentRow(0)
        history_entry = {
            "name": custom_name,
            "timestamp": datetime.now().isoformat(),
            "constraints": constraints,
            "generated_data": generated_data
        }
        self.history_data.insert(0, history_entry)
        self.save_history_to_file()

    def save_history_to_file(self):
        try:
            with open(self.history_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.history_data[::-1], f, ensure_ascii=False, indent=4)
        except IOError as e:
            self.status_bar.showMessage(f"错误: 无法保存历史文件！ {e}", 5000)

    def clear_all_history(self):
        reply = QMessageBox.question(self, "确认操作",
                                     "你确定要 *永久删除* 所有的历史记录吗？\n此操作不可撤销。",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.history_list_widget.clear()
            self.history_data = []
            self.save_history_to_file()
            self.result_output.setText("历史记录已清空。")
            self.status_bar.showMessage("历史记录已清空", 3000)
        else:
            self.status_bar.showMessage("已取消清空操作", 3000)

    def create_manual_tab(self) -> QWidget:
        tab = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # 数据结构类型（仅保留数组、矩阵、字符串）
        self.manual_data_type = QComboBox()
        self.manual_data_type.addItems(["数组", "字符串"])

        # 规模输入：n (长度/行数/长度) 和 m (列数/备用)
        self.manual_n_value = QLineEdit()
        self.manual_n_value.setPlaceholderText("例如: 10 或 1-100（字符串/数组长度或矩阵行数）")
        self.manual_m_value = QLineEdit()
        self.manual_m_value.setPlaceholderText("例如: 10 或 1-100（矩阵列数，数组/字符串可留空）")

        # 元素类型选择：数字 / 字母 / 符号 / 混合
        self.manual_element_type = QComboBox()
        self.manual_element_type.addItems(["混合", "数字", "字母", "符号"])
        # 元素类型选择
        self.manual_element_type = QComboBox()
        self.manual_element_type.addItems(["混合", "数字", "字母", "符号", "自定义"])

        # 自定义字符输入框
        self.manual_custom_chars = QLineEdit()
        self.manual_custom_chars.setPlaceholderText("当选择'自定义'时，请输入可用元素，如: abc123@#")
        self.manual_custom_chars.setEnabled(False)

        # 当选择变化时启用输入框
        self.manual_element_type.currentTextChanged.connect(
            lambda t: self.manual_custom_chars.setEnabled(t == "自定义")
        )   

        form_layout.addRow(QLabel("元素类型:"), self.manual_element_type)
        form_layout.addRow(QLabel("自定义字符:"), self.manual_custom_chars)

        # 生成组数
        self.manual_groups = QSpinBox()
        self.manual_groups.setValue(1)
        self.manual_groups.setMinimum(1)

        form_layout.addRow(QLabel("数据结构:"), self.manual_data_type)
        form_layout.addRow(QLabel("规模 N:"), self.manual_n_value)
        # form_layout.addRow(QLabel("规模 M (矩阵列数):"), self.manual_m_value)
        form_layout.addRow(QLabel("元素类型:"), self.manual_element_type)
        form_layout.addRow(QLabel("数据组数:"), self.manual_groups)

        self.manual_generate_button = QPushButton("生成 (手动模式)")
        form_layout.addRow(self.manual_generate_button)
        tab.setLayout(form_layout)
        self.manual_generate_button.clicked.connect(self.run_manual_generation)
        return tab

    def create_ai_tab(self) -> QWidget:
        tab = QWidget()
        ai_layout = QVBoxLayout()
        ai_layout.setSpacing(10)
        self.ai_input = QTextEdit()
        self.ai_input.setPlaceholderText("请在此处粘贴你的算法题目自然语言描述...")
        self.ai_generate_button = QPushButton("AI 解析并直接生成")
        ai_layout.addWidget(QLabel("题目描述:"))
        ai_layout.addWidget(self.ai_input)
        ai_layout.addWidget(self.ai_generate_button)
        ai_layout.addStretch(1)
        tab.setLayout(ai_layout)
        self.ai_generate_button.clicked.connect(self.run_ai_generation)
        return tab

    def run_generation_flow(self, constraints_map: dict, generated_data: str):
        default_name = f"{constraints_map.get('type', 'Data')} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        text, ok = QInputDialog.getText(self, "保存历史记录", "为该条记录命名:",
                                        QLineEdit.EchoMode.Normal, default_name)
        if ok and text:
            self.result_output.setText(generated_data)
            self.status_bar.showMessage("生成成功！", 3000)
            self.add_history_item(constraints_map, generated_data, custom_name=text)
        elif ok and not text:
            self.status_bar.showMessage("已取消保存，因为未提供名称。", 3000)
            self.result_output.setText(generated_data)
        else:
            self.status_bar.showMessage("已取消保存到历史记录。", 3000)
            self.result_output.setText(generated_data)

    def run_manual_generation(self):
        data_type = self.manual_data_type.currentText()
        n_value = self.manual_n_value.text()
        m_value = self.manual_m_value.text()
        element_type = self.manual_element_type.currentText()
        groups = self.manual_groups.value()
        custom_chars = self.manual_custom_chars.text()
        constraints_map = {
            "type": data_type,
            "n": n_value,
            "m": m_value,
            "groups": groups,
            "element_type": element_type,
            "custom_chars": custom_chars
        }

        try:
            generated_data = self.call_core_engine(constraints_map)
            self.run_generation_flow(constraints_map, generated_data)
        except Exception as e:
            self.result_output.setText(f"--- 手动模式生成失败 ---\n{str(e)}")
            self.status_bar.showMessage("生成失败！", 3000)

    def run_ai_generation(self):
        problem_text = self.ai_input.toPlainText()
        if not problem_text.strip():
            self.result_output.setText("AI 解析错误: 题目描述不能为空。")
            self.status_bar.showMessage("AI 解析错误", 3000)
            return
        try:
            # AI 模块尚未实现：模拟一个基础约束（可后续替换）
            simulated_constraints = {"type": "数组", "n": "10", "m": "10", "groups": 1, "element_type": "混合"}
            generated_data = self.call_core_engine(simulated_constraints)
            self.run_generation_flow(simulated_constraints, generated_data)
        except Exception as e:
            self.result_output.setText(f"--- AI 模式生成失败 ---\n{str(e)}")
            self.status_bar.showMessage("生成失败！", 3000)

    def call_core_engine(self, constraints: dict) -> str:
        if not constraints:
            raise ValueError("约束不能为空！")
        # 直接调用 core.manual_generator.generate_data
        return generate_data(constraints)

    def open_settings_dialog(self):
        dialog = SettingsDialog(self,
                                self.current_theme,
                                self.current_font_size,
                                self.current_language)
        if dialog.exec():
            settings = dialog.get_settings()
            self.current_theme = settings["theme"]
            self.current_font_size = settings["font_size"]
            self.current_language = settings["language"]
            self.apply_settings(self.current_theme,
                                self.current_font_size,
                                self.current_language)

    def apply_settings(self, theme, font_size, language):
        stylesheet = self.get_stylesheet(theme, font_size)
        QApplication.instance().setStyleSheet(stylesheet)
        self.apply_language(language)

    def apply_language(self, lang):
        self.status_bar.showMessage(f"语言已切换为: {lang} (部分UI可能需要重启后更新)", 3000)

    # -----------------------------------------------------------------
    # --- QSS 样式表 (无变化) ---
    # -----------------------------------------------------------------
    def get_stylesheet(self, theme, font_size):
        # (此函数内容与上一版完全相同，折叠)
        if theme == "Dark":
            palette = {
                "bg": "#2b2b2b", "bg_darker": "#212121", "bg_lighter": "#3c3c3c",
                "text": "#f0f0f0", "text_dim": "#aaa", "border": "#555",
                "primary": "#007bff", "primary_hover": "#0056b3", "primary_pressed": "#004085",
                "danger": "#ff5555"
            }
        else:  # Light Theme
            palette = {
                "bg": "#ffffff", "bg_darker": "#f0f0f0", "bg_lighter": "#e0e0e0",
                "text": "#212121", "text_dim": "#555", "border": "#c0c0c0",
                "primary": "#007bff", "primary_hover": "#0056b3", "primary_pressed": "#004085",
                "danger": "#cc0000"
            }
        return f"""
        QMainWindow, QDialog {{ background-color: {palette["bg"]}; }}
        QWidget {{
            font-size: {font_size}px;
            color: {palette["text"]};
            background-color: {palette["bg"]};
        }}
        QLabel#ErrorLabel {{ color: {palette["danger"]}; font-weight: bold; }}
        QToolButton#LinkButton {{
            color: {palette["primary"]};
            background-color: transparent;
            border: none;
            text-decoration: underline;
        }}
        QToolButton#LinkButton:hover {{ color: {palette["primary_hover"]}; }}
        QDockWidget {{ color: {palette["text_dim"]}; }}
        QDockWidget::title {{
            background-color: {palette["bg_lighter"]};
            color: {palette["text_dim"]};
            padding: 8px;
            border-top: 1px solid {palette["border"]};
        }}
        QListWidget {{
            background-color: {palette["bg_darker"]};
            color: {palette["text_dim"]};
            border: 1px solid {palette["border"]};
        }}
        QListWidget::item {{ padding: 8px; }}
        QListWidget::item:hover {{
            background-color: {palette["bg_lighter"]};
            color: {palette["text"]};
        }}
        QListWidget::item:selected {{
            background-color: {palette["primary"]};
            color: white;
        }}
        QMenuBar {{
            background-color: {palette["bg_lighter"]};
            color: {palette["text"]};
            border-bottom: 1px solid {palette["border"]};
        }}
        QMenuBar::item:selected {{ background-color: {palette["primary"]}; color: white; }}
        QMenu {{
            background-color: {palette["bg_lighter"]};
            color: {palette["text"]};
            border: 1px solid {palette["border"]};
        }}
        QMenu::item:selected {{ background-color: {palette["primary"]}; color: white; }}
        QStatusBar {{
            background-color: {palette["bg_lighter"]};
            color: {palette["text_dim"]};
            border-top: 1px solid {palette["border"]};
        }}
        QTabWidget::pane {{
            background-color: {palette["bg"]}; 
            border: 1px solid {palette["border"]};
            border-top: none;
            border-radius: 0px;
            padding: 10px;
        }}
        QTabBar::tab {{
            background-color: {palette["bg_lighter"]};
            color: {palette["text_dim"]};
            padding: 10px 20px;
            border: 1px solid {palette["border"]};
            border-bottom: none;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: {palette["bg"]};
            color: {palette["text"]};
            border-bottom: 1px solid {palette["bg"]};
        }}
        QTabBar::tab:!selected:hover {{
            background-color: {palette["bg_lighter"]};
            color: {palette["text"]};
        }}
        QLabel {{ color: {palette["text"]}; background-color: transparent; }}
        QPushButton {{
            background-color: {palette["primary"]};
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 10px;
        }}
        QPushButton:hover {{ background-color: {palette["primary_hover"]}; }}
        QPushButton:pressed {{ background-color: {palette["primary_pressed"]}; }}
        QLineEdit, QComboBox, QSpinBox {{
            background-color: {palette["bg_lighter"]};
            border: 1px solid {palette["border"]};
            padding: 8px;
            border-radius: 4px;
            color: {palette["text"]};
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 1px solid {palette["primary"]};
        }}
        QComboBox QAbstractItemView {{
            background-color: {palette["bg_lighter"]};
            selection-background-color: {palette["primary"]};
            color: {palette["text"]};
        }}
        QTextEdit {{
            background-color: {palette["bg_darker"]};
            border: 1px solid {palette["border"]};
            padding: 8px;
            border-radius: 4px;
            color: {palette["text"]};
            font-family: 'Courier New', monospace;
        }}
        QTextEdit:focus {{ border: 1px solid {palette["primary"]}; }}
        """


# -----------------------------------------------------------------
# --- 启动应用程序 (无变化) ---
# -----------------------------------------------------------------
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     login_dialog = LoginDialog()

#     # --- 临时的样式加载方案 (无变化) ---
#     temp_window_for_style = TestronApp("temp")
#     default_style = temp_window_for_style.get_stylesheet("Dark", 14)
#     temp_window_for_style.close()
#     app.setStyleSheet(default_style)

#     if login_dialog.exec():
#         username = login_dialog.get_username()
#         main_window = TestronApp(username=username)
#         main_window.apply_settings(
#             main_window.current_theme,
#             main_window.current_font_size,
#             main_window.current_language
#         )
#         main_window.show()
#         sys.exit(app.exec())
#     else:
#         sys.exit(0)