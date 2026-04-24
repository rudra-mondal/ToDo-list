## 2026-04-03 - PySide6 QIcon Repeated Loading Bottleneck
**Learning:** In list-based PySide6 UIs (like `TaskItemWidget` repeated many times), repeatedly loading the same icon from disk using `QIcon(filepath)` and checking `os.path.isfile()` causes significant main thread blocking and slows down UI updates (re-renders drop from ~14s to ~10s for 500 tasks with cache).
**Action:** Always implement a simple dict cache (`ICON_CACHE = {}`) for `QIcon` objects to avoid redundant filesystem reads and instantiation during list rendering or UI updates. QIcons are implicitly shared in Qt, so caching is safe and memory-efficient.

## 2026-04-24 - PySide6 Layout Clearing O(N²) Bottleneck
**Learning:** Clearing Qt layouts by iteratively taking the first item (`takeAt(0)`) or tracking and deleting in a forward loop is an O(N²) operation because removing early items causes the underlying array to shift.
**Action:** Always clear Qt layouts by iterating backwards (`reversed(range(layout.count()))`) and using `takeAt(i)` combined with `deleteLater()`. This changes the removal from O(N²) to O(N) and drastically reduces layout update times.
