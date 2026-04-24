## 2024-04-24 - QLabel Rich Text Injection
**Vulnerability:** UI Rich Text Injection via `QLabel` default `AutoText` formatting
**Learning:** PySide6/Qt's `QLabel` automatically detects and renders HTML if `setTextFormat` is not explicitly set. If user input (like a task description) contains HTML tags, it will be rendered as rich text, potentially leading to UI spoofing or injection vulnerabilities.
**Prevention:** Always explicitly set `setTextFormat(Qt.TextFormat.PlainText)` on `QLabel` widgets that display user-provided content.
