
## 2024-05-15 - Enhancing Keyboard Navigation and Accessibility for Qt Icon Buttons
**Learning:** Qt `QPushButton`s set as icon-only often lack visible focus indicators and accessible names, which breaks keyboard navigation. The default `setFocusPolicy` is sometimes disabled (`Qt.FocusPolicy.NoFocus`) for cosmetic reasons, further degrading accessibility.
**Action:** Always enable `Qt.FocusPolicy.StrongFocus` on interactive elements, provide explicit `setToolTip` and `setAccessibleName` values (especially when dynamic, like toggle buttons), and style `:focus` pseudo-states to ensure keyboard users have visual feedback.

## 2025-02-28 - PySide6 Accessible Names & Hover States
**Learning:** PySide6 components like `QPushButton` and `QLineEdit` used dynamically or exclusively for icons/inputs often lack screen reader support and proper mouse affordance if not explicitly configured. `setAccessibleName` ensures screen readers can announce the purpose of these non-text elements. Using custom `QFrame`s for list items requires explicit `:hover` stylesheet definitions to make them feel interactive, unlike native buttons.
**Action:** Always add `setAccessibleName` to inputs and icon-only buttons. Add explicit `:hover` styles to custom `QFrame` interactable containers to provide visual feedback to users, ensuring the UI feels responsive to mouse movement. Always set `setCursor(Qt.CursorShape.PointingHandCursor)` on clickable elements that aren't natively styled to do so.
## 2025-02-18 - Qt Stylesheet Keyboard Accessibility Focus Issues
**Learning:** In PySide6/Qt stylesheets, setting `border: none;` on interactive elements (like `QPushButton`) completely removes native focus rings. When developers try to restore custom focus rings by adding `:focus { border: 2px solid [color]; }`, it causes layout shifts because the element grows by 4px (2px per side).
**Action:** Use `border: 2px solid transparent;` as the default state instead of `border: none;` to reserve space for the focus ring, and ensure all interactive components use `setFocusPolicy(Qt.FocusPolicy.StrongFocus)` alongside a defined `:focus` border style to maintain keyboard accessibility without layout jank.

## 2025-04-15 - Context Menu Discoverability in PySide6
**Learning:** Components in PySide6 with custom context menus lack visual and screen reader discoverability by default. Users may not realize right-click actions (like edit or delete) are available.
**Action:** Always add a `setToolTip` and `setAccessibleDescription` to components with custom context menus to explicitly indicate the available actions (e.g., 'Right-click to edit or delete') for both mouse and screen reader users.
