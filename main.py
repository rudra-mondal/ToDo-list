# -*- coding: utf-8 -*-
"""
Simple ToDo List Application using PySide6
Manages tasks with completion and priority status, persists data in JSON.
Includes a main window and a mini always-on-top mode.
Uses resource_path for PyInstaller compatibility with external assets.
"""

import sys
import json
import os # Import os for path joining and checking
import pygame
from PySide6.QtCore import Qt, QSize, Signal, QObject, QPoint
from PySide6.QtGui import QIcon, QAction, QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QMenu, QLabel, QSizePolicy, QScrollArea,
                               QFrame, QDialog, QSpacerItem)

# --- Configuration ---
# Note: ICON_PATH definition is removed, using resource_path directly
PRIMARY_COLOR = "#C6534E"
WINDOW_BG_COLOR = "#F5F5F5" # Main window background
MINI_WINDOW_BG_COLOR = "#F5F5F5" # Mini window background
DIALOG_BG_COLOR = "#FFFFFF" # Edit dialog background

# --- Resource Path Function (For PyInstaller --onedir compatibility) ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller --onedir """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)


# --- Data ---
class Task:
    """Represents a single task item."""
    def __init__(self, description, completed=False, prioritized=False):
        self.description = description
        self.completed = completed
        self.prioritized = prioritized

    def __eq__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return (self.description == other.description and
                self.completed == other.completed and
                self.prioritized == other.prioritized)

class TaskModel(QObject):
    """Manages the list of tasks and persistence."""
    data_changed = Signal()

    def __init__(self, filename="tasks.json"):
        super().__init__()
        self.tasks = []
        self.filename = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else '.', filename)
        self.load_tasks()
        self._init_sound()

    def _init_sound(self):
        """Initializes the sound system."""
        try:
            pygame.mixer.init()
            sound_file_path = resource_path("Assets/complete.mp3") # Use resource_path
            if os.path.isfile(sound_file_path): # Use os.path.isfile
                self.complete_sound = pygame.mixer.Sound(sound_file_path) # Path is already a string
            else:
                self.complete_sound = None
        except pygame.error as e:
            print(f"Warning: Pygame mixer init or sound load failed: {e}")
            self.complete_sound = None
        except Exception as e:
             print(f"Warning: Sound system initialization failed: {e}")
             self.complete_sound = None

    def _find_task_index(self, task_instance):
        """Safely find the index of a task instance."""
        try:
            return self.tasks.index(task_instance)
        except ValueError:
             for i, task in enumerate(self.tasks):
                  if task == task_instance:
                      return i
             return -1

    def add_task(self, description):
        """Adds a new task."""
        if description:
            self.tasks.append(Task(description))
            self.save_tasks()
            self.data_changed.emit()

    def delete_task(self, index):
        """Deletes a task by index."""
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save_tasks()
            self.data_changed.emit()
        else:
            print(f"Warning: Attempted to delete invalid index {index}")

    def toggle_complete(self, index):
        """Toggles the completion status of a task."""
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            task.completed = not task.completed
            self.save_tasks()
            self.data_changed.emit()
            if task.completed and self.complete_sound:
                try:
                    self.complete_sound.play()
                except pygame.error as e:
                    print(f"Warning: Failed to play sound: {e}")
        else:
             print(f"Warning: Attempted to toggle complete for invalid index {index}")

    def toggle_priority(self, index):
        """Toggles the priority status of a task."""
        if 0 <= index < len(self.tasks):
            self.tasks[index].prioritized = not self.tasks[index].prioritized
            self.save_tasks()
            self.data_changed.emit()
        else:
             print(f"Warning: Attempted to toggle priority for invalid index {index}")

    def edit_task(self, index, new_description):
        """Edits the description of a task."""
        if 0 <= index < len(self.tasks) and new_description:
            self.tasks[index].description = new_description
            self.save_tasks()
            self.data_changed.emit()
        elif not new_description:
             print("Warning: Attempted to edit task with empty description.")
        else:
             print(f"Warning: Attempted to edit invalid index {index}")

    def save_tasks(self):
        """Saves the current tasks to the JSON file."""
        data = [{"description": t.description, "completed": t.completed, "prioritized": t.prioritized}
               for t in self.tasks]
        try:
            with open(self.filename, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
             print(f"Error saving tasks to {self.filename}: {e}")

    def load_tasks(self):
        """Loads tasks from the JSON file."""
        if not os.path.isfile(self.filename): # Check if file exists
             self.tasks = []
             print(f"Info: No tasks file found at {self.filename}. Starting fresh.")
             return

        try:
            with open(self.filename, "r", encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.tasks = []
                    for t_data in data:
                        if isinstance(t_data, dict) and "description" in t_data and "completed" in t_data:
                            self.tasks.append(Task(
                                t_data["description"],
                                t_data["completed"],
                                t_data.get("prioritized", False) # Handle older files missing priority
                            ))
                        else:
                             print(f"Warning: Skipping invalid task data: {t_data}")
                else:
                    print(f"Warning: Invalid format in {self.filename}, expected a list.")
                    self.tasks = []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading tasks from {self.filename}: {e}")
            self.tasks = [] # Load failed, start fresh


# --- UI Widgets ---
class TaskItemWidget(QFrame):
    """Widget displaying a single task item."""
    def __init__(self, task, model, is_mini=False):
        super().__init__()
        self.model = model
        self.task = task
        self.is_mini = is_mini

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(60)
        self.setObjectName("TaskItemFrame")
        self.setStyleSheet(f"""
            #TaskItemFrame {{
                background: white;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
                margin: 4px 2px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # Status Button
        self.status_btn = QPushButton()
        self.status_btn.setFixedSize(24, 24)
        self.status_btn.setCheckable(True)
        self.status_btn.setChecked(task.completed)
        self.status_btn.clicked.connect(self._on_status_toggled)
        self.status_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.update_status_icon()

        # Text Label
        self.text_label = QLabel(task.description)
        self.text_label.setWordWrap(True)
        self.text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.update_text_style()

        # Priority Button
        self.priority_btn = QPushButton()
        self.priority_btn.setFixedSize(24, 24)
        self.priority_btn.setCheckable(True)
        self.priority_btn.setChecked(task.prioritized)
        self.priority_btn.clicked.connect(self._on_priority_toggled)
        self.priority_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.update_priority_icon()

        layout.addWidget(self.status_btn)
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.priority_btn)

        # Enable context menu only for main window items
        if not self.is_mini:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self.show_context_menu)

    def _on_status_toggled(self):
        current_index = self.model._find_task_index(self.task)
        if current_index != -1:
            self.model.toggle_complete(current_index)
        else:
            print("Warning: Task no longer exists in model for status toggle.")

    def _on_priority_toggled(self):
        current_index = self.model._find_task_index(self.task)
        if current_index != -1:
            self.model.toggle_priority(current_index)
        else:
             print("Warning: Task no longer exists in model for priority toggle.")

    def _get_icon(self, filename):
        """Safely gets a QIcon using resource_path, falling back to None."""
        icon_full_path = resource_path(os.path.join("Assets", filename)) # Use resource_path
        if os.path.isfile(icon_full_path):
            return QIcon(icon_full_path)
        print(f"Warning: Icon not found: {icon_full_path}")
        return None

    def update_status_icon(self):
        icon_name = "check.svg" if self.task.completed else "radio.svg"
        icon = self._get_icon(icon_name)
        if icon:
            self.status_btn.setIcon(icon)
            self.status_btn.setIconSize(QSize(24, 24))
            self.status_btn.setText("")
            self.status_btn.setStyleSheet("border: none;")
        else:
            self.status_btn.setText("✓" if self.task.completed else "O")

    def update_priority_icon(self):
        icon_name = "star_filled.svg" if self.task.prioritized else "star.svg"
        icon = self._get_icon(icon_name)
        color = PRIMARY_COLOR if self.task.prioritized else "#CCCCCC"
        if icon:
             self.priority_btn.setIcon(icon)
             self.priority_btn.setIconSize(QSize(20, 20))
             self.priority_btn.setText("")
        else:
             self.priority_btn.setText("★" if self.task.prioritized else "☆")
        self.priority_btn.setStyleSheet(f"border: none; color: {color};")

    def update_text_style(self):
        style = "font-size: 14px;"
        if self.task.completed:
            style += "color: #888888; text-decoration: line-through;"
        else:
            style += "color: #333333; text-decoration: none;"
        self.text_label.setStyleSheet(style)

    def show_context_menu(self, pos):
        current_index = self.model._find_task_index(self.task)
        if current_index == -1: return

        menu = QMenu()
        edit_icon = self._get_icon("edit.svg")
        delete_icon = self._get_icon("delete.svg")

        edit_action = QAction("Edit", self)
        if edit_icon: edit_action.setIcon(edit_icon)
        edit_action.triggered.connect(lambda: self.edit_task(current_index))

        delete_action = QAction("Delete", self)
        if delete_icon: delete_action.setIcon(delete_icon)
        delete_action.triggered.connect(lambda: self.model.delete_task(current_index))

        menu.addAction(edit_action)
        menu.addAction(delete_action)
        menu.exec(self.mapToGlobal(pos))

    def edit_task(self, index_to_edit):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Task")
        dialog.setMinimumWidth(300)
        dialog.setStyleSheet(f"QDialog {{ background-color: {DIALOG_BG_COLOR}; }}")

        layout = QVBoxLayout()
        edit_input = QLineEdit(self.task.description)
        edit_input.selectAll()
        edit_input.setStyleSheet("""
                    QLineEdit { padding: 8px; border: 1px solid #CCCCCC; border-radius: 4px; }
                    QLineEdit:focus { border: 1px solid #AAAAAA; }""")

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.setStyleSheet(f"padding: 5px 15px; background-color: {PRIMARY_COLOR}; color: white; border: none; border-radius: 4px;")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("padding: 5px 15px; border: 1px solid #CCCCCC; border-radius: 4px;")

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        save_btn.clicked.connect(lambda: self.save_edit(edit_input.text(), dialog, index_to_edit))
        cancel_btn.clicked.connect(dialog.reject)
        edit_input.returnPressed.connect(save_btn.click)

        layout.addWidget(edit_input)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def save_edit(self, text, dialog, index_to_edit):
        new_description = text.strip()
        if new_description:
            self.model.edit_task(index_to_edit, new_description)
            dialog.accept()
        else:
            print("Task description cannot be empty.")
            edit_input = dialog.findChild(QLineEdit)
            if edit_input:
                 edit_input.setStyleSheet(edit_input.styleSheet() + "border: 1px solid red;")


# --- Main Window ---
class MainWindow(QMainWindow):
    """The main application window."""
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.mini_window = None
        self._init_window_properties()
        self.init_ui()
        self.model.data_changed.connect(self.update_ui)

    def _init_window_properties(self):
        self.setWindowTitle("ToDo List")
        icon_full_path = resource_path(os.path.join("Assets", "icon.ico")) # Use resource_path
        if os.path.isfile(icon_full_path): self.setWindowIcon(QIcon(icon_full_path))
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet(f"background-color: {WINDOW_BG_COLOR};")

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        header = self._create_header()
        self.scroll, self.task_container, self.task_layout = self._create_scroll_area()
        self.completed_header, self.completed_items, self.completed_layout = self._create_completed_section()
        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.add_btn, self.task_input = self._create_input_area()

        # Assemble Task Layout Structure
        self.task_layout.addWidget(self.completed_header)
        self.task_layout.addWidget(self.completed_items)
        self.task_layout.addItem(self.vertical_spacer)
        self.scroll.setWidget(self.task_container)

        # Add Widgets to Main Layout
        layout.addWidget(header)
        layout.addWidget(self.scroll, 1)
        layout.addWidget(self.task_input)
        layout.addWidget(self.add_btn)
        self.setCentralWidget(main_widget)

        self.update_ui()

    def _create_header(self):
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0); header_layout.setSpacing(10)
        icon_label = QLabel(); house_icon_full_path = resource_path(os.path.join("Assets", "house.svg")) # Use resource_path
        if os.path.isfile(house_icon_full_path): icon_label.setPixmap(QIcon(house_icon_full_path).pixmap(24, 24))
        else: icon_label.setText("T")
        title_label = QLabel("Tasks")
        title_label.setStyleSheet(f"font-size: 20px; color: {PRIMARY_COLOR}; font-weight: bold;")
        self.mini_btn = QPushButton(); min_icon_full_path = resource_path(os.path.join("Assets", "minimize.svg")) # Use resource_path
        if os.path.isfile(min_icon_full_path): self.mini_btn.setIcon(QIcon(min_icon_full_path))
        else: self.mini_btn.setText("_")
        self.mini_btn.setFixedSize(32, 32); self.mini_btn.setToolTip("Switch to Mini Mode")
        self.mini_btn.clicked.connect(self.show_mini_window)
        self.mini_btn.setStyleSheet(f"QPushButton{{border:none;background:{PRIMARY_COLOR};border-radius:16px;}} QPushButton:hover{{background:#D6655E;}}")
        header_layout.addWidget(icon_label); header_layout.addWidget(title_label)
        header_layout.addStretch(); header_layout.addWidget(self.mini_btn)
        return header

    def _create_scroll_area(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""QScrollArea{{border:none;background:transparent;}} QScrollBar:vertical{{background:#E0E0E0;width:8px;margin:0px;border-radius:4px;}} QScrollBar::handle:vertical{{background:{PRIMARY_COLOR};min-height:25px;border-radius:4px;}} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0px;background:none;}} QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{{background:none;}}""")
        task_container = QWidget(); task_container.setStyleSheet("background:transparent;")
        task_layout = QVBoxLayout(task_container); task_layout.setContentsMargins(0,0,0,0); task_layout.setSpacing(0); task_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Align items top
        return scroll, task_container, task_layout

    def _create_completed_section(self):
        completed_header = QPushButton("Completed 0  ⌄"); completed_header.setCheckable(True); completed_header.setChecked(True)
        completed_header.setStyleSheet(f"QPushButton{{text-align:left;padding:8px 5px;margin-top:10px;font-size:14px;font-weight:bold;color:{PRIMARY_COLOR};border:none;border-radius:4px;}} QPushButton:hover{{background-color:#EEEEEE;}}")
        completed_header.clicked.connect(self.toggle_completed_visibility)
        completed_items = QWidget(); completed_items.setVisible(True)
        completed_layout = QVBoxLayout(completed_items); completed_layout.setContentsMargins(0,5,0,0); completed_layout.setSpacing(0); completed_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        return completed_header, completed_items, completed_layout

    def _create_input_area(self):
        add_btn = QPushButton("+ Add a task")
        add_btn.setStyleSheet(f"QPushButton{{background:{PRIMARY_COLOR};color:white;border:none;padding:12px;border-radius:8px;font-size:14px;font-weight:bold;}} QPushButton:hover{{background:#D6655E;}} QPushButton:pressed{{background:#B6453E;}}")
        add_btn.clicked.connect(self.show_add_task_input)
        task_input = QLineEdit(); task_input.setPlaceholderText("Type a new task and press Enter...")
        task_input.setStyleSheet("QLineEdit{padding:12px;border:1px solid #CCCCCC;border-radius:8px;font-size:14px;background-color:white;} QLineEdit:focus{border:1px solid #AAAAAA;}")
        task_input.returnPressed.connect(self.add_task); task_input.hide()
        return add_btn, task_input

    def show_add_task_input(self):
        self.add_btn.hide(); self.task_input.show(); self.task_input.setFocus()

    def add_task(self):
        text = self.task_input.text().strip()
        self.model.add_task(text)
        self.task_input.clear(); self.task_input.hide(); self.add_btn.show()

    def toggle_completed_visibility(self):
        is_checked = self.completed_header.isChecked()
        self.completed_items.setVisible(is_checked)
        symbol = "⌄" if is_checked else "⌃"
        completed_count = sum(t.completed for t in self.model.tasks)
        self.completed_header.setText(f"Completed {completed_count}  {symbol}")

    def update_ui(self):
        # --- Clear Layouts (Keep non-TaskItemWidgets) ---
        active_widgets_to_remove = []
        for i in range(self.task_layout.count()):
            item = self.task_layout.itemAt(i)
            widget = item.widget()
            # Only mark TaskItemWidget instances for removal
            if widget and isinstance(widget, TaskItemWidget):
                 active_widgets_to_remove.append(widget) # Store widget directly

        # Remove marked TaskItemWidgets
        for widget in active_widgets_to_remove:
            widget.setParent(None) # Remove from parent layout
            widget.deleteLater()

        # Clear completed layout completely
        while self.completed_layout.count():
            item = self.completed_layout.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()

        # --- Separate and Sort Tasks ---
        tasks = self.model.tasks
        active_tasks = [t for t in tasks if not t.completed]
        completed_tasks = [t for t in tasks if t.completed]
        active_tasks.sort(key=lambda t: not t.prioritized) # Prioritized first

        # --- Rebuild Layout ---
        # Find the index where completed section starts (header or spacer if empty)
        insertion_point = self.task_layout.indexOf(self.completed_header)
        if insertion_point == -1: # Failsafe if header somehow got removed
             insertion_point = self.task_layout.indexOf(self.vertical_spacer)
        if insertion_point == -1: insertion_point = 0 # Ultimate fallback

        # Insert active tasks before the insertion point
        for task in reversed(active_tasks): # Insert in reverse to maintain order at top
             widget = TaskItemWidget(task, self.model)
             self.task_layout.insertWidget(insertion_point, widget)

        # Add completed tasks to their dedicated layout
        for task in completed_tasks:
             widget = TaskItemWidget(task, self.model)
             self.completed_layout.addWidget(widget)

        # Update completed header text
        symbol = "⌄" if self.completed_header.isChecked() else "⌃"
        self.completed_header.setText(f"Completed {len(completed_tasks)}  {symbol}")

        # Ensure spacer is still at the very end of the main task layout
        current_spacer_item = self.task_layout.itemAt(self.task_layout.count() - 1)
        if not current_spacer_item or current_spacer_item.spacerItem() != self.vertical_spacer:
             self.task_layout.removeItem(self.vertical_spacer)
             self.task_layout.addItem(self.vertical_spacer)

        # Handle add button/input visibility
        if not self.task_input.isHidden(): self.add_btn.hide()
        else: self.add_btn.show()


    def show_mini_window(self):
        if not self.mini_window or not self.mini_window.isVisible():
            self.mini_window = MiniWindow(self.model, self)
            self.mini_window.show()
            self.hide()

    def closeEvent(self, event):
        if self.mini_window: self.mini_window.close()
        pygame.mixer.quit()
        event.accept()


# --- Mini Window ---
class MiniWindow(QMainWindow):
    """A compact, always-on-top version of the task list."""
    def __init__(self, model, main_window_ref):
        super().__init__()
        self.model = model
        self.main_window_ref = main_window_ref
        self._init_window_properties()
        self.init_ui()
        self.model.data_changed.connect(self.update_ui)
        self._drag_pos = None

    def _init_window_properties(self):
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("ToDo-Mini")
        icon_full_path = resource_path(os.path.join("Assets", "icon.ico")) # Use resource_path
        if os.path.isfile(icon_full_path): self.setWindowIcon(QIcon(icon_full_path))
        self.resize(270, 320)
        self._position_window()

    def _position_window(self):
        try:
            screen = QApplication.primaryScreen()
            if screen:
                 screen_geometry = screen.availableGeometry()
                 margin = 20
                 x = screen_geometry.x() + screen_geometry.width() - self.width() - margin
                 y = screen_geometry.y() + margin
                 self.move(x, y)
            else: self.move(50, 50)
        except Exception as e: print(f"Warning: Could not get screen geometry: {e}"); self.move(50, 50)

    def init_ui(self):
        container_frame = QFrame()
        container_frame.setObjectName("MiniContainer")
        container_frame.setStyleSheet(f"#MiniContainer{{background-color:{MINI_WINDOW_BG_COLOR};border-radius:10px;border:1px solid #D0D0D0;}}")

        layout = QVBoxLayout(container_frame)
        layout.setContentsMargins(12, 8, 12, 12); layout.setSpacing(8)

        header = self._create_header()
        self.scroll, self.task_container, self.task_layout = self._create_scroll_area()
        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # Assemble Layout
        self.task_layout.addItem(self.vertical_spacer) # Add spacer first in mini mode
        self.scroll.setWidget(self.task_container)
        layout.addWidget(header)
        layout.addWidget(self.scroll, 1)
        self.setCentralWidget(container_frame)

        self.update_ui()

    def _create_header(self):
        header = QWidget()
        header_layout = QHBoxLayout(header); header_layout.setContentsMargins(0,0,0,0); header_layout.setSpacing(8)
        back_btn = QPushButton(); back_icon_full_path = resource_path(os.path.join("Assets", "back.svg")) # Use resource_path
        if os.path.isfile(back_icon_full_path): back_btn.setIcon(QIcon(back_icon_full_path))
        else: back_btn.setText("<")
        back_btn.setFixedSize(28, 28); back_btn.setToolTip("Back to Full Mode")
        back_btn.clicked.connect(self.show_main_window)
        back_btn.setStyleSheet(f"QPushButton{{border:none;background:{PRIMARY_COLOR};border-radius:14px;}} QPushButton:hover{{background:#D6655E;}}")
        title = QLabel("Active Tasks")
        title.setStyleSheet(f"font-size:16px;color:{PRIMARY_COLOR};font-weight:bold;")
        header_layout.addWidget(back_btn); header_layout.addWidget(title); header_layout.addStretch()
        return header

    def _create_scroll_area(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""QScrollArea{{border:none;background:transparent;}} QScrollBar:vertical{{background:#E8E8E8;width:6px;margin:0px;border-radius:3px;}} QScrollBar::handle:vertical{{background:{PRIMARY_COLOR};min-height:20px;border-radius:3px;}} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0px;background:none;}} QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{{background:none;}}""")
        task_container = QWidget(); task_container.setStyleSheet("background:transparent;")
        task_layout = QVBoxLayout(task_container); task_layout.setContentsMargins(0,0,0,0); task_layout.setSpacing(0); task_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Align top
        return scroll, task_container, task_layout

    def update_ui(self):
        # --- Clear Layout ---
        widgets_to_remove = []
        for i in range(self.task_layout.count()):
            item = self.task_layout.itemAt(i)
            widget = item.widget()
            if widget and isinstance(widget, TaskItemWidget):
                widgets_to_remove.append(widget)

        for widget in widgets_to_remove:
             widget.setParent(None)
             widget.deleteLater()

        # --- Filter and Sort Tasks ---
        active_tasks = [t for t in self.model.tasks if not t.completed]
        active_tasks.sort(key=lambda t: not t.prioritized)

        # --- Rebuild Layout ---
        insertion_index = self.task_layout.indexOf(self.vertical_spacer)
        if insertion_index == -1: insertion_index = 0

        for i, task in enumerate(reversed(active_tasks)): # Insert active tasks before spacer
            widget = TaskItemWidget(task, self.model, is_mini=True)
            self.task_layout.insertWidget(insertion_index, widget) # Insert at the determined point

        # Ensure spacer is still physically last
        current_spacer_item = self.task_layout.itemAt(self.task_layout.count() - 1)
        if not current_spacer_item or current_spacer_item.spacerItem() != self.vertical_spacer:
             self.task_layout.removeItem(self.vertical_spacer)
             self.task_layout.addItem(self.vertical_spacer)


    def show_main_window(self):
        self.close(); self.main_window_ref.show(); self.main_window_ref.activateWindow()

    # --- Frameless Window Dragging ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Use position() relative to the window for dragging calculation
            self._drag_pos = event.position().toPoint()
            event.accept()
        else: super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            diff = event.globalPosition().toPoint() - self.mapToGlobal(self._drag_pos)
            self.move(self.pos() + diff)
            event.accept()
        else: super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._drag_pos:
            self._drag_pos = None; event.accept()
        else: super().mouseReleaseEvent(event)


# --- Main Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Check if Assets folder exists relative to executable/script
    assets_dir = resource_path("Assets")
    if not os.path.isdir(assets_dir):
        print(f"FATAL ERROR: Assets directory not found at expected location: {assets_dir}")
        print("Please ensure the 'Assets' folder is placed next to the executable or script.")
        sys.exit(1)
        
    model = TaskModel()
    main_window = MainWindow(model)
    main_window.show()

    sys.exit(app.exec())