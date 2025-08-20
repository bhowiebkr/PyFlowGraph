# Utils Module

This module provides utility functions and helper classes that support PyFlowGraph's core functionality. It contains commonly used operations, configuration management, and debugging tools that are shared across multiple application components.

## Purpose

The utils module centralizes common functionality and helper utilities that are used throughout PyFlowGraph. It provides reusable components that support debugging, color management, and configuration, ensuring consistent behavior across the application.

## Key Files

### `__init__.py`
Standard Python package initialization file.

### `color_utils.py`
- **Color Management**: Utilities for color manipulation and conversion
- RGB, HSV, and hex color format conversions
- Color palette generation for node types and themes
- Color interpolation and blending functions
- Theme-aware color selection and management
- Accessibility-friendly color contrast utilities

### `debug_config.py`
- **Debug Configuration**: Development and debugging configuration management
- Debug flag management for different application subsystems
- Logging level configuration and output formatting
- Performance profiling and timing utilities
- Memory usage monitoring and reporting
- Development mode feature toggles and testing aids

## Features

### Color Management
- **Format Conversion**: Seamless conversion between color formats (RGB, HSV, hex)
- **Palette Generation**: Automatic color palette creation for consistent theming
- **Contrast Utilities**: Tools for ensuring readable color combinations
- **Theme Integration**: Color management that works with application themes

### Debug Infrastructure
- **Configurable Logging**: Flexible logging system with adjustable verbosity levels
- **Performance Monitoring**: Built-in timing and profiling capabilities
- **Memory Tracking**: Memory usage analysis for performance optimization
- **Feature Toggles**: Development flags for testing experimental features

### Utility Functions
- **Common Operations**: Frequently used functions shared across modules
- **Helper Classes**: Reusable utility classes for common patterns
- **Configuration Management**: Centralized configuration handling
- **Cross-Platform Support**: Platform-aware utilities for Windows compatibility

## Dependencies

- **Python Standard Library**: Built on standard Python utilities and tools
- **Qt Color System**: Integration with Qt's color management for UI consistency
- **Logging Framework**: Uses Python's logging module for debug output
- **Configuration Systems**: Integration with application settings and preferences

## Usage Notes

- Color utilities ensure consistent visual appearance across the application
- Debug configuration supports both development and production modes
- All utilities are designed to be lightweight and efficient
- Functions provide sensible defaults while allowing customization
- Platform-specific considerations are handled transparently

## Color Utilities

### Color Conversions
- **RGB to HSV**: Convert RGB values to hue, saturation, value format
- **Hex to RGB**: Parse hexadecimal color strings to RGB tuples
- **Color Validation**: Ensure color values are within valid ranges
- **Format Detection**: Automatically detect and handle different color formats

### Palette Management
- **Theme Colors**: Generate coordinated color schemes for interface elements
- **Node Colors**: Automatic color assignment for different node types
- **Contrast Analysis**: Ensure adequate contrast for accessibility
- **Color Interpolation**: Smooth color transitions and gradients

## Debug Configuration

### Logging Control
- **Subsystem Logging**: Individual logging controls for different modules
- **Verbosity Levels**: Configurable detail levels for debug output
- **Output Formatting**: Customizable log message formatting and structure
- **Performance Logging**: Specialized logging for timing and performance data

### Development Tools
- **Feature Flags**: Toggle experimental features during development
- **Testing Modes**: Special configurations for automated testing
- **Debug Visualization**: Visual debug overlays and information displays
- **Memory Profiling**: Track memory usage patterns and potential leaks

## Architecture Integration

The utils module provides essential supporting functionality that enhances PyFlowGraph's reliability, maintainability, and visual consistency. By centralizing common operations and debugging tools, it ensures that all application components have access to consistent, well-tested utility functions.