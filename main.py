import sys
import json
from pathlib import Path
import pygame  # for sound playback
from PySide6.QtCore import Qt, QSize, Signal, QObject
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QMenu, QLabel, QSizePolicy, QScrollArea, QFrame, QDialog)

ICON_PATH = Path(__file__).parent / "icons"
PRIMARY_COLOR = "#C6534E"

class Task:
    def __init__(self, description, completed=False, prioritized=False):
        self.description = description
        self.completed = completed
        self.prioritized = prioritized

class TaskModel(QObject):
    data_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.load_tasks()
        # Initialize pygame mixer for sound playback.
        pygame.mixer.init()
        self.complete_sound = pygame.mixer.Sound(str(ICON_PATH / "complete.mp3"))
        
    def add_task(self, description):
        self.tasks.append(Task(description))
        self.save_tasks()
        self.data_changed.emit()
        
    def delete_task(self, index):
        del self.tasks[index]
        self.save_tasks()
        self.data_changed.emit()
        
    def toggle_complete(self, index):
        self.tasks[index].completed = not self.tasks[index].completed
        self.save_tasks()
        self.data_changed.emit()
        # Only play the sound when a task is marked complete (not when unchecking)
        if self.tasks[index].completed:
            self.complete_sound.play()
        
    def toggle_priority(self, index):
        self.tasks[index].prioritized = not self.tasks[index].prioritized
        self.save_tasks()
        self.data_changed.emit()
        
    def edit_task(self, index, new_description):
        self.tasks[index].description = new_description
        self.save_tasks()
        self.data_changed.emit()
        
    def save_tasks(self):
        data = [{"description": t.description, "completed": t.completed, "prioritized": t.prioritized} 
               for t in self.tasks]
        with open("tasks.json", "w") as f:
            json.dump(data, f)
            
    def load_tasks(self):
        try:
            with open("tasks.json", "r") as f:
                data = json.load(f)
                self.tasks = [Task(t["description"], t["completed"], t.get("prioritized", False)) 
                             for t in data]
        except FileNotFoundError:
            self.tasks = []

class TaskItemWidget(QFrame):
    def __init__(self, task, index, model, is_mini=False):
        super().__init__()
        self.index = index
        self.model = model
        self.task = task
        self.is_mini = is_mini
        
        # Increase the fixed height a bit for better readability.
        self.setFixedHeight(60)
        self.setStyleSheet(f"""
            background: white;
            border-radius: 8px;
            margin: 4px 0;
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(15)

        # Status button
        self.status_btn = QPushButton()
        self.status_btn.setFixedSize(24, 24)
        self.status_btn.setCheckable(True)
        self.status_btn.setChecked(task.completed)
        self.status_btn.clicked.connect(lambda: self.model.toggle_complete(self.index))
        self.update_status_icon()
        
        # Task text
        self.text_label = QLabel(task.description)
        self.text_label.setStyleSheet("font-size: 14px; color: #333;")
        self.text_label.setWordWrap(True)
        self.text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if task.completed:
            self.text_label.setStyleSheet("color: #888; text-decoration: line-through; font-size: 14px;")
        
        # Priority (star) button -- always added so it shows in every window.
        self.priority_btn = QPushButton()
        self.priority_btn.setFixedSize(24, 24)
        self.priority_btn.setCheckable(True)
        self.priority_btn.setChecked(task.prioritized)
        self.priority_btn.clicked.connect(lambda: self.model.toggle_priority(self.index))
        self.update_priority_icon()
        
        layout.addWidget(self.status_btn)
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.priority_btn)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def update_status_icon(self):
        icon_name = "check.svg" if self.task.completed else "radio.svg"
        self.status_btn.setIcon(QIcon(str(ICON_PATH / icon_name)))
        self.status_btn.setIconSize(QSize(24, 24))
        
    def update_priority_icon(self):
        icon_name = "star_filled.svg" if self.task.prioritized else "star.svg"
        self.priority_btn.setIcon(QIcon(str(ICON_PATH / icon_name)))
        self.priority_btn.setIconSize(QSize(20, 20))
        self.priority_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                color: {PRIMARY_COLOR if self.task.prioritized else "#ccc"};
            }}
        """)
        
    def show_context_menu(self, pos):
        # Only show the context menu in the main window.
        if not self.is_mini:
            menu = QMenu()
            edit_action = QAction("Edit", self)
            edit_action.triggered.connect(self.edit_task)
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.model.delete_task(self.index))
            menu.addAction(edit_action)
            menu.addAction(delete_action)
            menu.exec_(self.mapToGlobal(pos))
            
    def edit_task(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Task")
        layout = QVBoxLayout()
        edit_input = QLineEdit(self.task.description)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_edit(edit_input.text(), dialog))
        layout.addWidget(edit_input)
        layout.addWidget(save_btn)
        dialog.setLayout(layout)
        dialog.exec_()
        
    def save_edit(self, text, dialog):
        if text:
            self.model.edit_task(self.index, text)
            self.text_label.setText(text)
            dialog.close()

class MainWindow(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.init_ui()
        self.model.data_changed.connect(self.update_ui)
        
    def init_ui(self):
        self.setWindowTitle("Tasks")
        self.setWindowIcon(QIcon(str(ICON_PATH / "house.svg")))
        self.setGeometry(100, 100, 400, 600)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        # Left header
        left_header = QWidget()
        left_layout = QHBoxLayout(left_header)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        icon = QLabel()
        icon.setPixmap(QIcon(str(ICON_PATH / "house.svg")).pixmap(24, 24))
        title = QLabel("Tasks")
        title.setStyleSheet(f"font-size: 20px; color: {PRIMARY_COLOR}; font-weight: bold;")
        left_layout.addWidget(icon)
        left_layout.addWidget(title)
        left_layout.addStretch()
        
        # Right header
        self.mini_btn = QPushButton()
        self.mini_btn.setIcon(QIcon(str(ICON_PATH / "minimize.svg")))
        self.mini_btn.setFixedSize(32, 32)
        self.mini_btn.clicked.connect(self.show_mini_window)
        self.mini_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: {PRIMARY_COLOR};
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background: #D6655E;
            }}
        """)
        
        header_layout.addWidget(left_header)
        header_layout.addStretch()
        header_layout.addWidget(self.mini_btn)
        
        # Task list
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{
                background: #f5f5f5;
                width: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {PRIMARY_COLOR};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
            }}
        """)
        
        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setContentsMargins(0, 0, 0, 0)
        self.task_layout.setSpacing(8)
        
        # Completed section with fixed spacing and top alignment
        self.completed_header = QPushButton("Completed 0  ⌄")
        self.completed_header.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 8px;
                font-size: 14px;
                color: {PRIMARY_COLOR};
                border: none;
            }}
        """)
        self.completed_header.clicked.connect(self.toggle_completed_visibility)
        self.completed_items = QWidget()
        self.completed_items.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.completed_layout = QVBoxLayout(self.completed_items)
        self.completed_layout.setContentsMargins(0, 0, 0, 0)
        self.completed_layout.setSpacing(6)
        self.completed_layout.setAlignment(Qt.AlignTop)
        
        self.task_layout.addWidget(self.completed_header)
        self.task_layout.addWidget(self.completed_items)
        self.scroll.setWidget(self.task_container)
        
        # Add task button
        self.add_btn = QPushButton("+ Add a task")
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #D6655E;
            }}
        """)
        self.add_btn.clicked.connect(self.show_add_task_input)
        
        layout.addWidget(header)
        layout.addWidget(self.scroll)
        layout.addWidget(self.add_btn)
        
        # Hidden input for new tasks
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Type a new task...")
        self.task_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        self.task_input.returnPressed.connect(self.add_task)
        self.task_input.hide()
        layout.insertWidget(2, self.task_input)
        
        self.setCentralWidget(main_widget)
        self.update_ui()
        
    def show_add_task_input(self):
        self.add_btn.hide()
        self.task_input.show()
        self.task_input.setFocus()
        
    def add_task(self):
        text = self.task_input.text()
        if text:
            self.model.add_task(text)
            self.task_input.clear()
            self.add_btn.show()
            self.task_input.hide()
            
    def toggle_completed_visibility(self):
        self.completed_items.setVisible(not self.completed_items.isVisible())
        visible_symbol = "⌄" if self.completed_items.isVisible() else "⌃"
        self.completed_header.setText(f"Completed {sum(t.completed for t in self.model.tasks)}  {visible_symbol}")
            
    def update_ui(self):
        # Clear active (non-completed) tasks (the completed section remains at the top)
        while self.task_layout.count() > 2:
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Add prioritized tasks first, then normal tasks
        prioritized_tasks = [t for t in self.model.tasks if not t.completed and t.prioritized]
        normal_tasks = [t for t in self.model.tasks if not t.completed and not t.prioritized]
        for task in prioritized_tasks + normal_tasks:
            widget = TaskItemWidget(task, self.model.tasks.index(task), self.model)
            # Insert above the completed section (which is always at position count()-2)
            self.task_layout.insertWidget(self.task_layout.count()-2, widget)
            
        # Update completed tasks
        while self.completed_layout.count():
            item = self.completed_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        completed_tasks = [t for t in self.model.tasks if t.completed]
        self.completed_header.setText(f"Completed {len(completed_tasks)}  ⌄")
        for task in completed_tasks:
            widget = TaskItemWidget(task, self.model.tasks.index(task), self.model)
            self.completed_layout.addWidget(widget)
            
    def show_mini_window(self):
        self.mini_window = MiniWindow(self.model)
        self.mini_window.show()
        self.hide()

class MiniWindow(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.init_ui()
        self.model.data_changed.connect(self.update_ui)
        
    def init_ui(self):
        self.setWindowTitle("Tasks Mini")
        self.setWindowIcon(QIcon(str(ICON_PATH / "house.svg")))
        self.setGeometry(100, 100, 300, 400)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header with back button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        back_btn = QPushButton()
        back_btn.setIcon(QIcon(str(ICON_PATH / "back.svg")))
        back_btn.setFixedSize(32, 32)
        back_btn.clicked.connect(self.show_main_window)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: {PRIMARY_COLOR};
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background: #D6655E;
            }}
        """)
        
        title = QLabel("Tasks")
        title.setStyleSheet(f"font-size: 20px; color: {PRIMARY_COLOR}; font-weight: bold;")
        
        header_layout.addWidget(back_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Task list for active (non-completed) tasks
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{
                background: #f5f5f5;
                width: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {PRIMARY_COLOR};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
            }}
        """)
        
        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setContentsMargins(0, 0, 0, 0)
        self.task_layout.setSpacing(8)
        # Align the layout to the top so no extra spacing is added.
        self.task_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.task_container)
        
        layout.addWidget(header)
        layout.addWidget(self.scroll)
        self.setCentralWidget(main_widget)
        
        self.update_ui()
        
    def update_ui(self):
        # Clear existing tasks in the mini-window layout
        while self.task_layout.count():
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get active tasks (non-completed) and sort so that prioritized tasks come first.
        active_tasks = [t for t in self.model.tasks if not t.completed]
        active_tasks = sorted(active_tasks, key=lambda t: not t.prioritized)
        for task in active_tasks:
            widget = TaskItemWidget(task, self.model.tasks.index(task), self.model, is_mini=True)
            self.task_layout.addWidget(widget)
            
        # (No stretch added here so the spacing remains consistent.)
        
    def show_main_window(self):
        self.close()
        main_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = TaskModel()
    main_window = MainWindow(model)
    main_window.show()
    sys.exit(app.exec())
