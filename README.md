
# ✅ ToDo List App

A simple yet functional ToDo list application built with Python and the PySide6 framework. Manage your tasks efficiently with features like completion status, priority marking, editing, deleting, and a handy always-on-top mini mode. Tasks are saved locally in a `tasks.json` file.

<h4 align=center>👇 Here's a glimpse of the new look 👇</h4>
<p align=center><img src="https://github.com/user-attachments/assets/7b3db1de-06e3-4b02-8bbd-345bde957c5d" alt="ToDo List Quick Look" height="500"></img></p>

## ✨ Features

*   **Add Tasks:** Quickly add new tasks via an input field.
*   **Mark Complete:** Toggle task completion status with a click. Includes a satisfying sound effect!
*   **Prioritize Tasks:** Mark important tasks with a star icon. Prioritized tasks appear at the top of the active list.
*   **Edit Tasks:** Modify the description of existing tasks easily.
*   **Delete Tasks:** Remove tasks you no longer need via a right-click context menu.
*   **Persistent Storage:** Your tasks are automatically saved to `tasks.json` in the application's directory and loaded on startup.
*   **Mini Mode:** Switch to a compact, always-on-top window showing only active tasks – perfect for keeping your list visible while working.
*   **Clean UI:** Simple and intuitive interface built with PySide6.
*   **Cross-Platform:** Built with Python and PySide6, potentially runnable on Windows, macOS, and Linux (requires dependencies).

## 🚀 Getting Started

There are two ways to use the application:

**1. Using the Pre-built Executable (Recommended for End-Users)**

*   Go to the [Releases](https://github.com/rudra-mondal/ToDo-list/releases) page of this repository.
*   Download the latest release EXE setup file for your Windows operating system (e.g., `ToDoList_WINDOWS_setup.exe`).
*   Run the setup executable and follow the instructions to install the app.
*   Hurrah! Now enjoy the ToDo List to manage your tasks efficiently.

    *Note: On Windows, you might get a SmartScreen warning because the executable isn't signed. You may need to click "More info" -> "Run anyway".*

**2. Running from Source (For Developers)**

*   **Prerequisites:**
    *   Python 3.7+ installed.
    *   `pip` (Python package installer).
*   **Clone the repository:**
    ```bash
    git clone https://github.com/rudra-mondal/ToDo-list.git
    cd ToDo-list
    ```
*   **Install dependencies:**
    ```bash
    pip install PySide6 pygame
    ```
*   **Run the application:**
    ```bash
    python main.py
    ```

## 🛠️ Usage

*   **Adding Tasks:** Click the "+ Add a task" button, type your task in the input field that appears, and press `Enter`.
*   **Completing Tasks:** Click the circle/radio button to the left of the task description. Click again to unmark. A sound plays upon completion.
*   **Prioritizing Tasks:** Click the star icon to the right of the task description. Prioritized tasks move to the top of the active list. Click again to un-prioritize.
*   **Editing/Deleting Tasks:** Right-click on a task item in the main window to open the context menu. Select "Edit" or "Delete".
*   **Mini Mode:** Click the minimize-style button in the top-right corner of the main window header.
*   **Exiting Mini Mode:** Click the back arrow button in the top-left corner of the mini window header to return to the full view.
*   **Moving Mini Mode:** Click and drag anywhere on the mini window's background (header or task area) to move it around your screen.

## 📦 Building from Source (using PyInstaller)

If you want to create the executable yourself:

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Navigate to the project root directory** in your terminal (the one containing your `.py` script and the `Assets` folder).
3.  **Run the PyInstaller command:**

    *   **Windows (cmd):**
        ```bash
        pyinstaller --name ToDoList --onedir --windowed --icon=Assets/icon.ico main.py
        ```
    *   **Linux/macOS (bash/zsh):**
        ```bash
        pyinstaller --name ToDoList --onedir --windowed --icon=Assets/icon.ico main.py
        ```

    *   `--onedir`: Creates a folder distribution (required for external assets).
    *   `--windowed` / `--noconsole`: Prevents the command prompt from showing.
    *   `--icon`: Sets the application icon.
    *   **Do not use `--add-data`** for the `Assets` folder.

4.  **Copy Assets:** After the build finishes, find the `dist/ToDoList` folder. Manually copy the entire `Assets` folder into `dist/ToDoList`, so it sits next to `ToDoList.exe` (or the equivalent executable on other platforms).
5.  The application inside `dist/ToDoList` is now ready to run and distribute.
6. **NOTE:** You can later make a setup executable using [Inno setup](https://jrsoftware.org/isinfo.php)

## 📁 Folder Structure (when running/distributing)

For the application (especially the built version) to find its icons and sounds, the `Assets` folder must be in the same directory as the executable or the main Python script:

```
ToDoList/
├── _internal
├── Assets/
│   └── ...
├── tasks.json         (Created automatically on first save)
└── ToDoList.exe
```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

Please report any bugs or suggest features using the [GitHub Issues](https://github.com/rudra-mondal/ToDo-list/issues) page.

---
