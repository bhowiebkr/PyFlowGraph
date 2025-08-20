# Resources Module

This module contains embedded resources used by PyFlowGraph's user interface, primarily Font Awesome font files that provide scalable vector icons throughout the application.

## Purpose

The resources module centralizes all static assets required by the application, ensuring that PyFlowGraph can display professional-quality icons and graphics without external dependencies. All resources are embedded directly in the application for reliable distribution.

## Key Files

### Font Awesome Font Files

#### `Font Awesome 6 Free-Solid-900.otf`
- **Font Awesome 6 Solid**: Solid style icons from Font Awesome 6
- Contains filled, bold icons for primary UI elements
- Used for main toolbar buttons, menu icons, and prominent interface elements
- Provides consistent visual language across the application

#### `Font Awesome 7 Free-Regular-400.otf`
- **Font Awesome 7 Regular**: Regular style icons from Font Awesome 7
- Contains outlined icons for secondary UI elements
- Used for status indicators, optional features, and subtle interface elements
- Complements the solid icons with lighter visual weight

## Font Integration

### Loading Process
The fonts are loaded at application startup in `main.py`:
1. Font files are detected in the resources directory
2. Fonts are registered with the Qt font database
3. Font families become available for use throughout the application

### Usage in UI
- **Icon Rendering**: Fonts are used to render scalable vector icons
- **Consistent Styling**: Provides uniform icon appearance across different screen DPI settings
- **Performance**: Vector icons scale efficiently without pixelation
- **Customization**: Icons can be styled with CSS and Qt stylesheets

## Dependencies

- **Qt Font System**: Uses Qt's QFontDatabase for font registration
- **Main Application**: Loaded during application initialization
- **UI Components**: Used throughout the interface for icon display

## Usage Notes

- Font files are embedded as application resources
- Icons are rendered as text characters using specific Unicode points
- Font Awesome provides thousands of professional icons
- Icons automatically scale with system font size and DPI settings
- Both solid and regular styles provide visual hierarchy options

## Icon Categories

### Available Icon Types
- **File Operations**: Open, save, import, export icons
- **Edit Actions**: Cut, copy, paste, undo, redo icons  
- **Node Operations**: Add, delete, connect, group icons
- **View Controls**: Zoom, pan, fullscreen, layout icons
- **Execution**: Play, stop, pause, debug icons
- **Settings**: Configuration, preferences, options icons

## Architecture Integration

The resources module ensures PyFlowGraph has a professional, consistent visual appearance. By embedding Font Awesome fonts, the application provides scalable, high-quality icons that work reliably across different platforms and display configurations without requiring external font installations.