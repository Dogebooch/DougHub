# Manual QA Checklist

This document serves as a manual test plan for UI and UX quality assurance. It is derived from the project's design principles and ensures that the application's visual polish, interaction design, and accessibility meet the high standards defined in the project's design resources.

## 1. Theme Behavior

- [ ] **Light/Dark Mode Switching**
    - [ ] Verify that the application correctly detects the system theme on startup.
    - [ ] Toggle between Light and Dark modes in the settings (if available) or system settings.
    - [ ] Ensure all UI elements (backgrounds, text, borders, icons) update immediately and correctly.
    - [ ] Check for any "flash of unstyled content" or artifacts during the switch.
    - [ ] Verify that high-contrast elements remain visible and legible in both modes.

- [ ] **Accent Color Propagation**
    - [ ] Verify that the primary accent color is applied consistently across all active elements (buttons, links, focus rings, active tabs).
    - [ ] Ensure the accent color has sufficient contrast against the background in both Light and Dark modes.

## 2. Responsiveness

- [ ] **Window Resizing**
    - [ ] Resize the application window from minimum to maximum dimensions.
    - [ ] Verify that the layout adapts fluidly without breaking or overlapping content.
    - [ ] Ensure that the minimum window size is enforced and prevents the UI from becoming unusable.

- [ ] **Content Reflow**
    - [ ] Check that text wraps correctly in variable-width containers.
    - [ ] Verify that grids and lists adjust their column count or item width appropriately.

- [ ] **Scrollbar Behavior**
    - [ ] Ensure scrollbars appear only when content overflows.
    - [ ] Verify that scrollbars are styled consistently with the theme (QFluentWidgets style).
    - [ ] Check that scrolling is smooth and responsive.

## 3. Worst-Case Content

- [ ] **Empty States**
    - [ ] Verify that all lists and data views have a clear, user-friendly "empty state" message or illustration when no data is present.
    - [ ] Ensure that actions available in empty states (e.g., "Add Item") are clearly visible and functional.

- [ ] **Long Text**
    - [ ] Test with extremely long titles, descriptions, or labels.
    - [ ] Verify that text is truncated with an ellipsis (...) or wrapped correctly, rather than overflowing its container.
    - [ ] Check tooltips or expansion mechanisms for truncated text.

- [ ] **Missing Optional Data**
    - [ ] Verify that the UI handles missing optional fields gracefully (e.g., missing images, missing tags).
    - [ ] Ensure that layout does not shift or break due to missing elements.

## 4. Accessibility

- [ ] **Keyboard Navigation**
    - [ ] Navigate through the entire application using only the `Tab` key.
    - [ ] Verify that the tab order is logical (top-to-bottom, left-to-right).
    - [ ] Ensure all interactive elements (buttons, inputs, links) are reachable via keyboard.
    - [ ] Verify that `Enter` and `Space` keys activate the focused element.

- [ ] **Focus Indicators**
    - [ ] Ensure that the currently focused element has a clearly visible focus ring or style change.
    - [ ] Verify that the focus indicator is visible in both Light and Dark modes.

- [ ] **Screen Reader Support (Basic)**
    - [ ] Verify that standard controls expose their name and role to accessibility tools (if applicable/supported by framework).

## 5. Visual Consistency

- [ ] **Alignment**
    - [ ] Verify that all elements are aligned to the defined grid or spacing system.
    - [ ] Check for pixel-perfect alignment of text baselines and icon centers.

- [ ] **Spacing**
    - [ ] Ensure consistent padding and margins between elements (following the 4px/8px grid rule).
    - [ ] Verify that related elements are grouped closer together than unrelated ones.

- [ ] **Component Usage**
    - [ ] Verify that standard QFluentWidgets components are used consistently (e.g., same button style for primary actions).
    - [ ] Check that font sizes and weights follow the typography scale.

## 6. Integration Failure Handling

- [ ] **Anki Disconnected**
    - [ ] Simulate Anki being closed or AnkiConnect unavailable.
    - [ ] Verify that the application displays a clear, non-intrusive error message.
    - [ ] Ensure the application does not crash or hang.

- [ ] **Notebook Sync Issues**
    - [ ] Simulate missing notes directory.
    - [ ] Verify that the application alerts the user and offers a way to resolve the issue (e.g., settings).

## 7. Data Integrity

- [ ] **Import/Export**
    - [ ] Verify that imported data appears correctly in the UI.
    - [ ] Check that special characters and formatting are preserved.

- [ ] **Persistence**
    - [ ] Make changes, restart the application, and verify that changes are saved.
