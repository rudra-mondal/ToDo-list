
## 2024-05-15 - Enhancing Keyboard Navigation and Accessibility for Qt Icon Buttons
**Learning:** Qt `QPushButton`s set as icon-only often lack visible focus indicators and accessible names, which breaks keyboard navigation. The default `setFocusPolicy` is sometimes disabled (`Qt.FocusPolicy.NoFocus`) for cosmetic reasons, further degrading accessibility.
**Action:** Always enable `Qt.FocusPolicy.StrongFocus` on interactive elements, provide explicit `setToolTip` and `setAccessibleName` values (especially when dynamic, like toggle buttons), and style `:focus` pseudo-states to ensure keyboard users have visual feedback.

## 2025-02-28 - PySide6 Accessible Names & Hover States
**Learning:** PySide6 components like `QPushButton` and `QLineEdit` used dynamically or exclusively for icons/inputs often lack screen reader support and proper mouse affordance if not explicitly configured. `setAccessibleName` ensures screen readers can announce the purpose of these non-text elements. Using custom `QFrame`s for list items requires explicit `:hover` stylesheet definitions to make them feel interactive, unlike native buttons.
**Action:** Always add `setAccessibleName` to inputs and icon-only buttons. Add explicit `:hover` styles to custom `QFrame` interactable containers to provide visual feedback to users, ensuring the UI feels responsive to mouse movement. Always set `setCursor(Qt.CursorShape.PointingHandCursor)` on clickable elements that aren't natively styled to do so.
## 2025-02-18 - Qt Stylesheet Keyboard Accessibility Focus Issues
**Learning:** In PySide6/Qt stylesheets, setting `border: none;` on interactive elements (like `QPushButton`) completely removes native focus rings. When developers try to restore custom focus rings by adding `:focus { border: 2px solid [color]; }`, it causes layout shifts because the element grows by 4px (2px per side).
**Action:** Use `border: 2px solid transparent;` as the default state instead of `border: none;` to reserve space for the focus ring, and ensure all interactive components use `setFocusPolicy(Qt.FocusPolicy.StrongFocus)` alongside a defined `:focus` border style to maintain keyboard accessibility without layout jank.

## 2025-05-18 - PySide6 Custom Context Menu Discoverability
**Learning:** PySide6 components with custom context menus lack visual discoverability by default. Users, especially those relying on screen readers or unaware of hidden features, may not know that a right-click action is available to edit or delete items.
**Action:** Always add a `setToolTip` and `setAccessibleDescription` to components that implement a custom context menu (e.g., `setToolTip("Right-click to edit or delete")`). This provides explicit affordance, indicating the available actions and improving both mouse hover discoverability and screen reader accessibility.

## 2025-02-18 - Qt Dynamic Empty States and Clear Focus Styling
**Learning:** In Qt applications, QLineEdits may have low-contrast focus borders that fail accessibility guidelines, and empty lists can leave users confused about what to do next or if the application is broken.
**Action:** Always provide explicit, high-contrast `:focus` styling for text inputs. Additionally, implement dynamic "Empty State" labels that appear when list layouts (like task lists) are empty, offering helpful guidance or a call to action to improve the overall user experience and reduce cognitive load.

## 2024-04-24 - QFrame Custom Context Menu Keyboard Accessibility
**Learning:** By default, custom context menus on generic Qt widgets (like `QFrame`) are strictly mouse-only (triggered via right-click). They ignore the "Menu" key on the keyboard entirely, breaking keyboard accessibility.
**Action:** When implementing custom context menus on generic components, always manually configure `setFocusPolicy(Qt.FocusPolicy.StrongFocus)`, add a visual `:focus` state in the QSS, and override `keyPressEvent` to intercept `Qt.Key.Key_Menu` (and optionally `Return`/`Enter`) to programmatically emit the `customContextMenuRequested` signal. Update tooltip strings to explicitly announce the keyboard shortcut.

## 2025-05-19 - Contextual Accessible Names and Eliminating Layout Shifts in Qt
**Learning:** Generic names like "Mark as completed" lack context when a user interacts with list items using screen readers, as they won't know *which* item is being acted upon. Furthermore, adding focus rings in Qt stylesheets via thicker borders (`border: 2px`) on components that originally had thinner borders (`border: 1px`) inherently introduces layout shifts if margins are not properly adjusted to compensate.
**Action:** When creating list items with interactive buttons (like a task list), always inject the specific item's context into the `accessibleName` (e.g., `f"Mark as completed: {item.title}"`). When assigning thicker borders to `:focus` or `:hover` states, correspondingly reduce the outer `margin` by the exact pixel difference to maintain the component's total layout dimensions and prevent UI jumping.

## 2025-05-20 - Preserving Keyboard Focus During Dynamic UI Rebuilds
**Learning:** In PySide6 applications, when user actions (like toggling a checkbox) trigger a data model update that completely rebuilds the layout, the widget that had focus is destroyed. This causes the application to lose focus entirely (`None`), severely disrupting keyboard navigation because the user has to tab back from the beginning of the window.
**Action:** When dynamic UI rebuilds are unavoidable, temporarily store a reference to the underlying data model (e.g., the specific task object) and the sub-component that had focus before the rebuild. After repopulating the layout, search for the newly created widget bound to that data model and explicitly call `setFocus()` on it to restore seamless keyboard accessibility.

## 2025-05-20 - Accessible Form Validation Feedback in Qt
**Learning:** In PySide6/Qt UIs, relying solely on changing the border color of a `QLineEdit` (e.g., to red) to indicate form validation failure is inaccessible for colorblind users and screen readers.
**Action:** Always provide explicit, text-based inline error messages (e.g., using a `QLabel` with red text) adjacent to the input field. Additionally, when a validation error occurs, dynamically update the `accessibleDescription` of the `QLineEdit` so screen readers announce the error context clearly.

## 2024-05-15 - Adding explicit tooltips for Qt keyboard shortcuts
**Learning:** PySide6/Qt doesn't automatically show keyboard shortcuts in tooltips when you set a shortcut via `setShortcut()`. Screen readers and visual users might miss these shortcuts if they're not explicitly documented in the UI.
**Action:** Always append the keyboard shortcut (e.g., "(Ctrl+N)") to the `setToolTip` string when applying a `setShortcut` to a Qt component to ensure proper discoverability.
