# Modern Icons Guide for PyFlowGraph

## Overview

This guide covers modern icon alternatives to Font Awesome for PyFlowGraph's dark theme Qt application. Research conducted January 2025 to identify the best icon solutions for PySide6 applications.

## Current Status

**Current Implementation**: Font Awesome icons via embedded fonts
**Issue**: Font Awesome icons don't look modern/professional in dark theme
**Solution**: Migrate to QtAwesome with modern icon sets

## Recommended Icon Libraries

### 1. Phosphor Icons (Primary Recommendation)

**Why Phosphor is the best choice for PyFlowGraph:**
- 4,470 icons with 5 different weights (Thin, Light, Regular, Bold, Fill)
- Designed at 16px×16px - perfect for Qt toolbar elements
- Excellent legibility at small sizes
- Consistent design language across all icons
- Multiple weights allow perfect matching with Qt's design system

**Implementation:**
```python
import qtawesome as qta

# Different weights for different UI elements
file_icon = qta.icon('ph.file-thin')           # Thin for subtle elements
save_icon = qta.icon('ph.floppy-disk-fill')    # Fill for primary actions
settings_icon = qta.icon('ph.gear-bold')       # Bold for important actions
search_icon = qta.icon('ph.magnifying-glass-light')  # Light for secondary
```

### 2. Alternative Modern Icon Sets

#### Remix Icons
- 2,271 modern icons
- Neutral and timeless look
- Sharp aesthetic with adjustable stroke width
- Good for Qt's design language

```python
truck_icon = qta.icon('ri.truck-fill')
home_icon = qta.icon('ri.home-line')
```

#### Material Design Icons
- Follows Google's Material Design guidelines
- Explicit dark theme color guidance
- High versatility and platform optimization

```python
network_icon = qta.icon('mdi6.access-point-network')
cloud_icon = qta.icon('mdi6.cloud-upload')
```

#### Microsoft Codicons
- 569 professional icons
- Clean, technical aesthetic
- Perfect for developer tools

```python
code_icon = qta.icon('msc.code')
terminal_icon = qta.icon('msc.terminal')
```

## Dark Theme Integration

### Recommended Dark Theme Library: PyQtDarkTheme

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar
import qtawesome as qta
import qdarktheme

app = QApplication(sys.argv)
qdarktheme.setup_theme()  # Apply modern dark theme

# Create toolbar with Phosphor icons
toolbar = QToolBar()
toolbar.addAction(qta.icon('ph.file-thin'), "New")
toolbar.addAction(qta.icon('ph.floppy-disk-fill'), "Save")
toolbar.addAction(qta.icon('ph.gear-bold'), "Settings")
```

### Dark Theme Color Guidelines

For Material Design Icons on dark backgrounds:
- **Active icons**: White at 100% opacity
- **Inactive icons**: White at 30% opacity

For Phosphor Icons:
- Use **Bold** or **Fill** weights for better visibility on dark backgrounds
- **Thin** and **Light** weights for subtle/secondary elements

## Installation Requirements

```bash
pip install QtAwesome      # Icon library with multiple icon sets
pip install pyqtdarktheme  # Modern dark theme
```

## Icon Browser Tool

QtAwesome includes a browser to preview all available icons:
```bash
qta-browser
```

Use this tool to:
- Search for specific icons
- Compare different icon sets
- Copy exact icon names for implementation

## Implementation Strategy for PyFlowGraph

### Phase 1: Replace Toolbar Icons
1. Replace Font Awesome toolbar icons with Phosphor equivalents
2. Use Bold/Fill weights for primary actions
3. Use Thin/Light weights for secondary actions

### Phase 2: Dark Theme Integration
1. Implement PyQtDarkTheme
2. Adjust icon weights for optimal dark theme visibility
3. Test icon legibility across different screen densities

### Phase 3: Comprehensive Icon Audit
1. Replace all Font Awesome icons throughout application
2. Ensure consistent icon weights and styles
3. Document icon usage patterns for future development

## Icon Weight Usage Guidelines

| Weight | Use Case | Example |
|--------|----------|---------|
| **Thin** | Subtle UI elements, secondary actions | Navigation arrows, minor controls |
| **Light** | Supporting actions, informational icons | Help icons, status indicators |
| **Regular** | Standard UI elements, default choice | General toolbar actions |
| **Bold** | Important actions, emphasized elements | Primary save/load actions |
| **Fill** | Critical actions, active states | Active tool selection, alerts |

## Technical Notes

- QtAwesome integrates seamlessly with existing PySide6 code
- No changes required to existing icon loading infrastructure
- Icons are vector-based and scale perfectly at any size
- All icon sets are included in single QtAwesome package
- Phosphor icons work exceptionally well with Qt's native styling

## References

- [QtAwesome GitHub Repository](https://github.com/spyder-ide/qtawesome)
- [Phosphor Icons Website](https://phosphoricons.com/)
- [PyQtDarkTheme Documentation](https://github.com/5yutan5/PyQtDarkTheme)
- Research conducted: January 2025

## Future Considerations

- Monitor QtAwesome updates for new icon sets
- Consider custom icon creation for PyFlowGraph-specific actions
- Evaluate user feedback on icon clarity and recognition
- Potential integration with Qt's native dark mode detection