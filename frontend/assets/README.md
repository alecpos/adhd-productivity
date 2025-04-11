# Assets Directory

This directory contains static assets used in the ADHD Calendar frontend application.

## Overview

The assets directory houses all static assets used throughout the application, including images, icons, fonts, animations, and other media files. These assets are organized by type and purpose to maintain a clean and manageable structure.

## Directory Structure

- **images/**: Contains image files
  - **backgrounds/**: Background images
  - **illustrations/**: Illustration graphics
  - **logos/**: App and brand logos
  - **placeholders/**: Placeholder images
  - **icons/**: Custom icon images
- **fonts/**: Custom font files
- **animations/**: Lottie animation files
- **sounds/**: Sound effect files
- **videos/**: Video assets

## Asset File Formats

### Images

- PNG format for icons and illustrations with transparency
- JPG format for photographs and complex images without transparency
- SVG format for scalable vector graphics
- WebP format for optimized image delivery

### Fonts

- TTF (TrueType Font)
- OTF (OpenType Font)
- WOFF (Web Open Font Format)
- WOFF2 (Web Open Font Format 2)

### Animations

- JSON files for Lottie animations
- GIF files for simple animations

### Sounds

- MP3 format for general audio
- WAV format for high-quality sound effects

## Asset Naming Convention

Assets follow a consistent naming convention:

- All lowercase
- Words separated by underscores
- Purpose or category prefixed when appropriate
- Descriptive names that indicate content and usage

Examples:
- `bg_primary.png` - Primary background image
- `icon_calendar.svg` - Calendar icon
- `illustration_empty_state.svg` - Empty state illustration
- `logo_main.png` - Main application logo
- `animation_loading.json` - Loading animation

## Usage Example

```tsx
import React from 'react';
import { Image, StyleSheet } from 'react-native';
import LottieView from 'lottie-react-native';

// Using images
const ProfileHeader = () => (
  <Image
    source={require('../assets/images/backgrounds/profile_header.jpg')}
    style={styles.headerImage}
  />
);

// Using animations
const LoadingIndicator = () => (
  <LottieView
    source={require('../assets/animations/loading_spinner.json')}
    autoPlay
    loop
    style={styles.loadingAnimation}
  />
);
```

## Icon System

The application uses a combination of:

- Custom icons (stored in the assets directory)
- Icon font library (@expo/vector-icons)

```tsx
import React from 'react';
import { Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// Custom icon
const CustomIcon = () => (
  <Image
    source={require('../assets/images/icons/custom_icon.png')}
    style={{ width: 24, height: 24 }}
  />
);

// Icon font
const StandardIcon = () => (
  <Ionicons name="calendar" size={24} color="black" />
);
```

## Responsive Assets

For images that need different resolutions:

- Use resolution suffixes (`@2x`, `@3x`)
- Provide multiple sizes for different device densities
- Use SVG where possible for resolution independence

## Asset Optimization

Assets should be optimized for:

- File size (to reduce bundle size and loading times)
- Performance (appropriate formats and resolutions)
- Device compatibility (supported formats across platforms)

## Development Guidelines

When adding or modifying assets:

1. Use appropriate file formats for each asset type
2. Optimize assets for file size and quality
3. Follow the naming conventions
4. Place assets in the correct subdirectory
5. Provide multiple resolutions when necessary
6. Use vector formats (SVG) when possible
7. Consider accessibility (e.g., providing alternative text)

## Related Documentation

- [Image Usage Guide](../docs/image_usage.md)
- [Asset Management](../docs/asset_management.md)
- [Icon System](../docs/icon_system.md)
- [App Branding](../docs/app_branding.md)
