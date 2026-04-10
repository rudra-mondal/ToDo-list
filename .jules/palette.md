## 2024-05-24 - PySide6 Focus Accessibility and `border: none`

**Learning:** In PySide6/Qt stylesheets, applying `border: none;` to a widget completely removes its native focus ring, hurting keyboard accessibility. When adding a custom `:focus` border back in, it can cause layout shifts because the element grows by the border width.

**Action:** Always default to `border: 2px solid transparent;` (or similar width) instead of `border: none;` for buttons. This maintains the layout size consistently across focused and non-focused states. If retrofitting a button that had `border: none;` and specific padding, reduce the padding by the width of the new border to maintain the exact same visual size. Also, ensure `setFocusPolicy(Qt.FocusPolicy.StrongFocus)` is explicitly called on interactive elements like custom buttons to guarantee they are reachable via Tab navigation.
