
## 2024-05-15 - Enhancing Keyboard Navigation and Accessibility for Qt Icon Buttons
**Learning:** Qt `QPushButton`s set as icon-only often lack visible focus indicators and accessible names, which breaks keyboard navigation. The default `setFocusPolicy` is sometimes disabled (`Qt.FocusPolicy.NoFocus`) for cosmetic reasons, further degrading accessibility.
**Action:** Always enable `Qt.FocusPolicy.StrongFocus` on interactive elements, provide explicit `setToolTip` and `setAccessibleName` values (especially when dynamic, like toggle buttons), and style `:focus` pseudo-states to ensure keyboard users have visual feedback.

## 2025-02-28 - PySide6 Accessible Names & Hover States
**Learning:** PySide6 components like `QPushButton` and `QLineEdit` used dynamically or exclusively for icons/inputs often lack screen reader support and proper mouse affordance if not explicitly configured. `setAccessibleName` ensures screen readers can announce the purpose of these non-text elements. Using custom `QFrame`s for list items requires explicit `:hover` stylesheet definitions to make them feel interactive, unlike native buttons.
**Action:** Always add `setAccessibleName` to inputs and icon-only buttons. Add explicit `:hover` styles to custom `QFrame` interactable containers to provide visual feedback to users, ensuring the UI feels responsive to mouse movement. Always set `setCursor(Qt.CursorShape.PointingHandCursor)` on clickable elements that aren't natively styled to do so.

## 2024-05-24 - Qt Border Hover Layout Shift
**Learning:** In PySide6, setting `border: none` removes native focus rings. When adding a border back for focus visible states, it causes an ugly 2px layout shift.
**Action:** When restyling buttons in Qt apps to handle `:focus` rings explicitly, use `border: 2px solid transparent;` by default instead of `border: none;`. Adjust padding down by the border width (e.g., `padding: 12px;` becomes `padding: 10px;`) to maintain consistent dimensions and avoid layout jumps when the border changes color on focus.
