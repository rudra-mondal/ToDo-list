import sys
import os # Required for resource_path
import json
from pathlib import Path
import pygame
from PySide6.QtCore import Qt, QSize, Signal, QObject, QPoint
from PySide6.QtGui import QIcon, QAction, QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QMenu, QLabel, QSizePolicy, QScrollArea,
                               QFrame, QDialog, QSpacerItem)


# --- Resource Path (Essential for PyInstaller) ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# --- Configuration ---
ICON_PATH = Path(resource_path("Assets")) # Use resource_path for Assets
DEFAULT_TASKS_FILE = "tasks.json" # Keep this relative to CWD or make absolute if needed elsewhere
PRIMARY_COLOR = "#C6534E"
WINDOW_BG_COLOR = "#F5F5F5"
MINI_WINDOW_BG_COLOR = "#F5F5F5"
DIALOG_BG_COLOR = "#FFFFFF"

# --- Asset Directory Check ---
if not ICON_PATH.exists():
    try:
        ICON_PATH.mkdir(exist_ok=True)
        print(f"Checked/Created Assets directory at: {ICON_PATH}")
    except OSError as e:
        print(f"Error checking/creating Assets directory: {e}")


# --- Data ---
class Task:
    # --- Task: __init__ ---
    def __init__(self, description, completed=False, prioritized=False):
        self.description = description
        self.completed = completed
        self.prioritized = prioritized

    # --- Task: __eq__ ---
    def __eq__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return (self.description == other.description and
                self.completed == other.completed and
                self.prioritized == other.prioritized)

class TaskModel(QObject):
    data_changed = Signal()

    # --- TaskModel: __init__ ---
    def __init__(self, filename=DEFAULT_TASKS_FILE):
        super().__init__()
        self.tasks = []
        # Determine if filename should be relative to CWD or bundled assets
        # If bundled, use: self.filename = Path(resource_path(filename))
        self.filename = Path(filename) # Relative to CWD by default
        self.load_tasks()
        self._init_sound()

    # --- TaskModel: _init_sound ---
    def _init_sound(self):
        try:
            pygame.mixer.init()
            sound_file = ICON_PATH / "complete.mp3"
            if sound_file.is_file():
                self.complete_sound = pygame.mixer.Sound(str(sound_file))
            else:
                self.complete_sound = None
        except Exception as e:
             print(f"Warning: Sound system initialization failed: {e}")
             self.complete_sound = None

    # --- TaskModel: _find_task_index ---
    def _find_task_index(self, task_instance):
        try:
            return self.tasks.index(task_instance)
        except ValueError:
             for i, task in enumerate(self.tasks):
                  if task == task_instance: return i
             return -1

    # --- TaskModel: add_task ---
    def add_task(self, description):
        if description:
            self.tasks.append(Task(description))
            self.save_tasks()
            self.data_changed.emit()

    # --- TaskModel: delete_task ---
    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save_tasks()
            self.data_changed.emit()

    # --- TaskModel: toggle_complete ---
    def toggle_complete(self, index):
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            task.completed = not task.completed
            self.save_tasks()
            self.data_changed.emit()
            if task.completed and self.complete_sound:
                try: self.complete_sound.play()
                except Exception: pass # Ignore sound errors silently

    # --- TaskModel: toggle_priority ---
    def toggle_priority(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index].prioritized = not self.tasks[index].prioritized
            self.save_tasks()
            self.data_changed.emit()

    # --- TaskModel: edit_task ---
    def edit_task(self, index, new_description):
        if 0 <= index < len(self.tasks) and new_description:
            self.tasks[index].description = new_description
            self.save_tasks()
            self.data_changed.emit()

    # --- TaskModel: save_tasks ---
    def save_tasks(self):
        data = [{"description": t.description, "completed": t.completed, "prioritized": t.prioritized}
               for t in self.tasks]
        try:
            with open(self.filename, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
             print(f"Error saving tasks to {self.filename}: {e}")

    # --- TaskModel: load_tasks ---
    def load_tasks(self):
        if not self.filename.is_file():
             self.tasks = []
             return
        try:
            with open(self.filename, "r", encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.tasks = []
                    for t_data in data:
                        if isinstance(t_data, dict) and "description" in t_data and "completed" in t_data:
                            self.tasks.append(Task(t_data["description"], t_data["completed"], t_data.get("prioritized", False)))
                else:
                    self.tasks = []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading tasks from {self.filename}: {e}")
            self.tasks = []


# --- UI Widgets ---
class TaskItemWidget(QFrame):
    # --- TaskItemWidget: __init__ ---
    def __init__(self, task, model, is_mini=False):
        super().__init__()
        self.model = model
        self.task = task
        self.is_mini = is_mini

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumHeight(60)
        self.setObjectName("TaskItemFrame")
        self.setStyleSheet(f"#TaskItemFrame{{background:white;border-radius:8px;border:1px solid #E0E0E0;margin:4px 2px;}}")

        layout = QHBoxLayout(self); layout.setContentsMargins(15,10,15,10); layout.setSpacing(15)

        self.status_btn = QPushButton(); self.status_btn.setFixedSize(24,24); self.status_btn.setCheckable(True)
        self.status_btn.setChecked(task.completed); self.status_btn.clicked.connect(self._on_status_toggled)
        self.status_btn.setFocusPolicy(Qt.NoFocus); self.update_status_icon()

        self.text_label = QLabel(task.description); self.text_label.setWordWrap(True)
        self.text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred); self.update_text_style()

        self.priority_btn = QPushButton(); self.priority_btn.setFixedSize(24,24); self.priority_btn.setCheckable(True)
        self.priority_btn.setChecked(task.prioritized); self.priority_btn.clicked.connect(self._on_priority_toggled)
        self.priority_btn.setFocusPolicy(Qt.NoFocus); self.update_priority_icon()

        layout.addWidget(self.status_btn); layout.addWidget(self.text_label, 1); layout.addWidget(self.priority_btn)

        self.setContextMenuPolicy(Qt.CustomContextMenu); self.customContextMenuRequested.connect(self.show_context_menu)

    # --- TaskItemWidget: _on_status_toggled ---
    def _on_status_toggled(self):
        current_index = self.model._find_task_index(self.task)
        if current_index != -1: self.model.toggle_complete(current_index)

    # --- TaskItemWidget: _on_priority_toggled ---
    def _on_priority_toggled(self):
        current_index = self.model._find_task_index(self.task)
        if current_index != -1: self.model.toggle_priority(current_index)

    # --- TaskItemWidget: _get_icon ---
    def _get_icon(self, filename):
        icon_path = ICON_PATH / filename
        if icon_path.is_file(): return QIcon(str(icon_path))
        return None

    # --- TaskItemWidget: update_status_icon ---
    def update_status_icon(self):
        icon_name = "check.svg" if self.task.completed else "radio.svg"
        icon = self._get_icon(icon_name)
        if icon:
            self.status_btn.setIcon(icon); self.status_btn.setIconSize(QSize(24, 24))
            self.status_btn.setText(""); self.status_btn.setStyleSheet("border: none;")
        else: self.status_btn.setText("✓" if self.task.completed else "O")

    # --- TaskItemWidget: update_priority_icon ---
    def update_priority_icon(self):
        icon_name = "star_filled.svg" if self.task.prioritized else "star.svg"
        icon = self._get_icon(icon_name)
        color = PRIMARY_COLOR if self.task.prioritized else "#CCCCCC"
        if icon:
             self.priority_btn.setIcon(icon); self.priority_btn.setIconSize(QSize(20, 20)); self.priority_btn.setText("")
        else: self.priority_btn.setText("★" if self.task.prioritized else "☆")
        self.priority_btn.setStyleSheet(f"border: none; color: {color};")

    # --- TaskItemWidget: update_text_style ---
    def update_text_style(self):
        style = "font-size: 14px;"
        style += "color:#888888;text-decoration:line-through;" if self.task.completed else "color:#333333;text-decoration:none;"
        self.text_label.setStyleSheet(style)

    # --- TaskItemWidget: show_context_menu ---
    def show_context_menu(self, pos):
        if not self.is_mini:
            current_index = self.model._find_task_index(self.task)
            if current_index == -1: return
            menu = QMenu(); edit_icon = self._get_icon("edit.svg"); delete_icon = self._get_icon("delete.svg")
            edit_action = QAction("Edit", self); delete_action = QAction("Delete", self)
            if edit_icon: edit_action.setIcon(edit_icon)
            if delete_icon: delete_action.setIcon(delete_icon)
            edit_action.triggered.connect(lambda: self.edit_task(current_index))
            delete_action.triggered.connect(lambda: self.model.delete_task(current_index))
            menu.addAction(edit_action); menu.addAction(delete_action); menu.exec(self.mapToGlobal(pos))

    # --- TaskItemWidget: edit_task ---
    def edit_task(self, index_to_edit):
        dialog = QDialog(self); dialog.setWindowTitle("Edit Task"); dialog.setMinimumWidth(300)
        dialog.setStyleSheet(f"QDialog{{background-color:{DIALOG_BG_COLOR};}}")
        layout = QVBoxLayout(); edit_input = QLineEdit(self.task.description); edit_input.selectAll()
        edit_input.setStyleSheet("QLineEdit{padding:8px;border:1px solid #CCCCCC;border-radius:4px;}QLineEdit:focus{border:1px solid #AAAAAA;}")
        button_layout = QHBoxLayout(); save_btn = QPushButton("Save"); save_btn.setDefault(True)
        save_btn.setStyleSheet(f"padding:5px 15px;background-color:{PRIMARY_COLOR};color:white;border:none;border-radius:4px;")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("padding:5px 15px;border:1px solid #CCCCCC;border-radius:4px;")
        button_layout.addStretch(); button_layout.addWidget(cancel_btn); button_layout.addWidget(save_btn)
        save_btn.clicked.connect(lambda: self.save_edit(edit_input.text(), dialog, index_to_edit))
        cancel_btn.clicked.connect(dialog.reject); edit_input.returnPressed.connect(save_btn.click)
        layout.addWidget(edit_input); layout.addLayout(button_layout); dialog.setLayout(layout); dialog.exec()

    # --- TaskItemWidget: save_edit ---
    def save_edit(self, text, dialog, index_to_edit):
        new_description = text.strip()
        if new_description: self.model.edit_task(index_to_edit, new_description); dialog.accept()
        else:
            edit_input = dialog.findChild(QLineEdit)
            if edit_input: edit_input.setStyleSheet(edit_input.styleSheet() + "border: 1px solid red;")


# --- Main Window ---
class MainWindow(QMainWindow):
    # --- MainWindow: __init__ ---
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.mini_window = None
        self._init_window_properties()
        self.init_ui()
        self.model.data_changed.connect(self.update_ui)

    # --- MainWindow: _init_window_properties ---
    def _init_window_properties(self):
        self.setWindowTitle("ToDo List")
        icon_path = ICON_PATH / "window.ico"
        if icon_path.is_file(): self.setWindowIcon(QIcon(str(icon_path)))
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet(f"background-color: {WINDOW_BG_COLOR};")

    # --- MainWindow: init_ui ---
    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget); layout.setContentsMargins(15,15,15,15); layout.setSpacing(15)
        header = self._create_header()
        self.scroll, self.task_container, self.task_layout = self._create_scroll_area()
        self.completed_header, self.completed_items, self.completed_layout = self._create_completed_section()
        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.add_btn, self.task_input = self._create_input_area()
        self.task_layout.addWidget(self.completed_header); self.task_layout.addWidget(self.completed_items)
        self.task_layout.addItem(self.vertical_spacer); self.scroll.setWidget(self.task_container)
        layout.addWidget(header); layout.addWidget(self.scroll, 1); layout.addWidget(self.task_input)
        layout.addWidget(self.add_btn); self.setCentralWidget(main_widget)
        self.update_ui()

    # --- MainWindow: _create_header ---
    def _create_header(self):
        header = QWidget(); header_layout = QHBoxLayout(header); header_layout.setContentsMargins(0,0,0,0); header_layout.setSpacing(10)
        icon_label = QLabel(); house_icon_path = ICON_PATH / "house.svg"
        if house_icon_path.is_file(): icon_label.setPixmap(QIcon(str(house_icon_path)).pixmap(24, 24))
        else: icon_label.setText("T")
        title_label = QLabel("Tasks"); title_label.setStyleSheet(f"font-size:20px;color:{PRIMARY_COLOR};font-weight:bold;")
        self.mini_btn = QPushButton(); min_icon_path = ICON_PATH / "minimize.svg"
        if min_icon_path.is_file(): self.mini_btn.setIcon(QIcon(str(min_icon_path)))
        else: self.mini_btn.setText("_")
        self.mini_btn.setFixedSize(32,32); self.mini_btn.setToolTip("Switch to Mini Mode")
        self.mini_btn.clicked.connect(self.show_mini_window)
        self.mini_btn.setStyleSheet(f"QPushButton{{border:none;background:{PRIMARY_COLOR};border-radius:16px;}} QPushButton:hover{{background:#D6655E;}}")
        header_layout.addWidget(icon_label); header_layout.addWidget(title_label); header_layout.addStretch(); header_layout.addWidget(self.mini_btn)
        return header

    # --- MainWindow: _create_scroll_area ---
    def _create_scroll_area(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{border:none;background:transparent;}} QScrollBar:vertical{{background:#E0E0E0;width:8px;margin:0px;border-radius:4px;}} QScrollBar::handle:vertical{{background:{PRIMARY_COLOR};min-height:25px;border-radius:4px;}} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0px;background:none;}} QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{{background:none;}}")
        task_container = QWidget(); task_container.setStyleSheet("background:transparent;")
        task_layout = QVBoxLayout(task_container); task_layout.setContentsMargins(0,0,0,0); task_layout.setSpacing(0)
        return scroll, task_container, task_layout

    # --- MainWindow: _create_completed_section ---
    def _create_completed_section(self):
        completed_header = QPushButton("Completed 0  ⌄"); completed_header.setCheckable(True); completed_header.setChecked(True)
        completed_header.setStyleSheet(f"QPushButton{{text-align:left;padding:8px 5px;margin-top:10px;font-size:14px;font-weight:bold;color:{PRIMARY_COLOR};border:none;border-radius:4px;}} QPushButton:hover{{background-color:#EEEEEE;}}")
        completed_header.clicked.connect(self.toggle_completed_visibility)
        completed_items = QWidget(); completed_items.setVisible(True)
        completed_layout = QVBoxLayout(completed_items); completed_layout.setContentsMargins(0,5,0,0); completed_layout.setSpacing(0); completed_layout.setAlignment(Qt.AlignTop)
        return completed_header, completed_items, completed_layout

    # --- MainWindow: _create_input_area ---
    def _create_input_area(self):
        add_btn = QPushButton("+ Add a task")
        add_btn.setStyleSheet(f"QPushButton{{background:{PRIMARY_COLOR};color:white;border:none;padding:12px;border-radius:8px;font-size:14px;font-weight:bold;}} QPushButton:hover{{background:#D6655E;}} QPushButton:pressed{{background:#B6453E;}}")
        add_btn.clicked.connect(self.show_add_task_input)
        task_input = QLineEdit(); task_input.setPlaceholderText("Type a new task and press Enter...")
        task_input.setStyleSheet("QLineEdit{padding:12px;border:1px solid #CCCCCC;border-radius:8px;font-size:14px;background-color:white;} QLineEdit:focus{border:1px solid #AAAAAA;}")
        task_input.returnPressed.connect(self.add_task); task_input.hide()
        return add_btn, task_input

    # --- MainWindow: show_add_task_input ---
    def show_add_task_input(self):
        self.add_btn.hide(); self.task_input.show(); self.task_input.setFocus()

    # --- MainWindow: add_task ---
    def add_task(self):
        text = self.task_input.text().strip()
        self.model.add_task(text)
        self.task_input.clear(); self.task_input.hide(); self.add_btn.show()

    # --- MainWindow: toggle_completed_visibility ---
    def toggle_completed_visibility(self):
        is_checked = self.completed_header.isChecked()
        self.completed_items.setVisible(is_checked)
        symbol = "⌄" if is_checked else "⌃"
        completed_count = sum(t.completed for t in self.model.tasks)
        self.completed_header.setText(f"Completed {completed_count}  {symbol}")

    # --- MainWindow: update_ui ---
    def update_ui(self):
        active_widgets_to_remove = []
        for i in range(self.task_layout.count()):
            item = self.task_layout.itemAt(i); widget = item.widget()
            if widget and isinstance(widget, TaskItemWidget): active_widgets_to_remove.append(item)
        for item in active_widgets_to_remove:
             widget = item.widget(); self.task_layout.removeItem(item); widget.deleteLater()
        while self.completed_layout.count():
            item = self.completed_layout.takeAt(0); widget = item.widget(); widget.deleteLater()

        tasks = self.model.tasks; active_tasks = [t for t in tasks if not t.completed]; completed_tasks = [t for t in tasks if t.completed]
        active_tasks.sort(key=lambda t: not t.prioritized)
        insertion_index = self.task_layout.indexOf(self.completed_header); insertion_index = insertion_index if insertion_index != -1 else 0
        for i, task in enumerate(active_tasks):
             widget = TaskItemWidget(task, self.model); self.task_layout.insertWidget(insertion_index + i, widget)
        for task in completed_tasks:
             widget = TaskItemWidget(task, self.model); self.completed_layout.addWidget(widget)
        symbol = "⌄" if self.completed_header.isChecked() else "⌃"; self.completed_header.setText(f"Completed {len(completed_tasks)}  {symbol}")
        self.task_layout.removeItem(self.vertical_spacer); self.task_layout.addItem(self.vertical_spacer)
        if not self.task_input.isHidden(): self.add_btn.hide()
        else: self.add_btn.show()

    # --- MainWindow: show_mini_window ---
    def show_mini_window(self):
        if not self.mini_window or not self.mini_window.isVisible():
            self.mini_window = MiniWindow(self.model, self); self.mini_window.show(); self.hide()

    # --- MainWindow: closeEvent ---
    def closeEvent(self, event):
        if self.mini_window: self.mini_window.close()
        pygame.mixer.quit(); event.accept()


# --- Mini Window ---
class MiniWindow(QMainWindow):
    # --- MiniWindow: __init__ ---
    def __init__(self, model, main_window_ref):
        super().__init__()
        self.model = model; self.main_window_ref = main_window_ref
        self._init_window_properties(); self.init_ui()
        self.model.data_changed.connect(self.update_ui); self._drag_pos = None

    # --- MiniWindow: _init_window_properties ---
    def _init_window_properties(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground); self.setWindowTitle("ToDo-Mini")
        icon_path = ICON_PATH / "window.ico"
        if icon_path.is_file(): self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(270, 320); self._position_window()

    # --- MiniWindow: _position_window ---
    def _position_window(self):
        try:
            screen = QApplication.primaryScreen()
            if screen:
                 screen_geometry = screen.availableGeometry(); margin = 20
                 x = screen_geometry.x() + screen_geometry.width() - self.width() - margin
                 y = screen_geometry.y() + margin; self.move(x, y)
            else: self.move(50, 50)
        except Exception as e: print(f"Warning: Could not get screen geometry: {e}"); self.move(50, 50)

    # --- MiniWindow: init_ui ---
    def init_ui(self):
        container_frame = QFrame(); container_frame.setObjectName("MiniContainer")
        container_frame.setStyleSheet(f"#MiniContainer{{background-color:{MINI_WINDOW_BG_COLOR};border-radius:10px;border:1px solid #D0D0D0;}}")
        layout = QVBoxLayout(container_frame); layout.setContentsMargins(12,8,12,12); layout.setSpacing(8)
        header = self._create_header()
        self.scroll, self.task_container, self.task_layout = self._create_scroll_area()
        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.task_layout.addItem(self.vertical_spacer); self.scroll.setWidget(self.task_container)
        layout.addWidget(header); layout.addWidget(self.scroll, 1); self.setCentralWidget(container_frame)
        self.update_ui()

    # --- MiniWindow: _create_header ---
    def _create_header(self):
        header = QWidget(); header_layout = QHBoxLayout(header); header_layout.setContentsMargins(0,0,0,0); header_layout.setSpacing(8)
        back_btn = QPushButton(); back_icon_path = ICON_PATH / "back.svg"
        if back_icon_path.is_file(): back_btn.setIcon(QIcon(str(back_icon_path)))
        else: back_btn.setText("<")
        back_btn.setFixedSize(28, 28); back_btn.setToolTip("Back to Full Mode")
        back_btn.clicked.connect(self.show_main_window)
        back_btn.setStyleSheet(f"QPushButton{{border:none;background:{PRIMARY_COLOR};border-radius:14px;}} QPushButton:hover{{background:#D6655E;}}")
        title = QLabel("Active Tasks"); title.setStyleSheet(f"font-size:16px;color:{PRIMARY_COLOR};font-weight:bold;")
        header_layout.addWidget(back_btn); header_layout.addWidget(title); header_layout.addStretch()
        return header

    # --- MiniWindow: _create_scroll_area ---
    def _create_scroll_area(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{border:none;background:transparent;}} QScrollBar:vertical{{background:#E8E8E8;width:6px;margin:0px;border-radius:3px;}} QScrollBar::handle:vertical{{background:{PRIMARY_COLOR};min-height:20px;border-radius:3px;}} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0px;background:none;}} QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{{background:none;}}")
        task_container = QWidget(); task_container.setStyleSheet("background:transparent;")
        task_layout = QVBoxLayout(task_container); task_layout.setContentsMargins(0,0,0,0); task_layout.setSpacing(0)
        return scroll, task_container, task_layout

    # --- MiniWindow: update_ui ---
    def update_ui(self):
        widgets_to_remove = []
        for i in range(self.task_layout.count()):
            item = self.task_layout.itemAt(i); widget = item.widget()
            if widget and isinstance(widget, TaskItemWidget): widgets_to_remove.append(item)
        for item in widgets_to_remove: widget = item.widget(); self.task_layout.removeItem(item); widget.deleteLater()

        active_tasks = [t for t in self.model.tasks if not t.completed]; active_tasks.sort(key=lambda t: not t.prioritized)
        insertion_index = self.task_layout.indexOf(self.vertical_spacer); insertion_index = insertion_index if insertion_index != -1 else 0
        for i, task in enumerate(active_tasks):
            widget = TaskItemWidget(task, self.model, is_mini=True); self.task_layout.insertWidget(insertion_index + i, widget)

        current_spacer_item = self.task_layout.itemAt(self.task_layout.count() - 1)
        if not current_spacer_item or current_spacer_item.spacerItem() != self.vertical_spacer:
             self.task_layout.removeItem(self.vertical_spacer); self.task_layout.addItem(self.vertical_spacer)

    # --- MiniWindow: show_main_window ---
    def show_main_window(self):
        self.close(); self.main_window_ref.show(); self.main_window_ref.activateWindow()

    # --- MiniWindow: mousePressEvent ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self._drag_pos = event.globalPosition().toPoint(); event.accept()
        else: super().mousePressEvent(event)

    # --- MiniWindow: mouseMoveEvent ---
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            new_global_pos = event.globalPosition().toPoint(); diff = new_global_pos - self._drag_pos
            self.move(self.pos() + diff); self._drag_pos = new_global_pos; event.accept()
        else: super().mouseMoveEvent(event)

    # --- MiniWindow: mouseReleaseEvent ---
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._drag_pos: self._drag_pos = None; event.accept()
        else: super().mouseReleaseEvent(event)


# --- Main Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = TaskModel()
    main_window = MainWindow(model)
    main_window.show()
    sys.exit(app.exec())