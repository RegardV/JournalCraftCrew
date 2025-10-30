# Journal Craft Crew - UI Design Standards

## 🎨 Design System Overview

This document defines the established UI design standards used in the splash screen, login, and register pages. These standards should be consistently applied across the dashboard and all other components.

## 🌈 Color Palette

### Primary Colors
- **Primary Gradient**: `from-indigo-600 to-indigo-700`
- **Primary Light**: `indigo-50`
- **Primary Dark**: `indigo-800`

### Accent Colors
- **Secondary**: `purple-50` to `purple-600` gradients
- **Success**: `green-100` background, `green-800` text
- **Warning**: `yellow-100` background, `yellow-800` text
- **Error**: `red-50` background, `red-600` text
- **Info**: `blue-100` background, `blue-800` text

### Neutral Colors
- **Background**: `white` primary, `gray-50` secondary
- **Text Primary**: `gray-900`
- **Text Secondary**: `gray-600`
- **Text Muted**: `gray-500`
- **Borders**: `gray-200`, `gray-100`
- **Gray Gradients**: `from-white to-gray-50`

## 📐 Typography Hierarchy

### Headings
- **Display**: `text-4xl md:text-5xl font-bold` (Hero titles)
- **Heading**: `text-2xl md:text-3xl font-bold` (Section titles)
- **Subheading**: `text-lg md:text-xl font-semibold` (Card titles)
- **Body**: `text-base` (Regular text)
- **Caption**: `text-sm text-gray-500` (Metadata)

### Text Utilities
- **Gradient Text**: `bg-gradient-to-r from-indigo-600 to-indigo-700 bg-clip-text text-transparent`
- **Font**: 'Inter', system-ui, sans-serif
- **Line Height**: 1.6

## 🎯 Component Standards

### 1. Cards & Containers

#### Content Card
```css
.content-card {
  @apply bg-white rounded-2xl shadow-lg border border-gray-100 p-8 hover:shadow-xl transition-all duration-300;
}
```

#### Metric Card
```css
.metric-card {
  @apply bg-gradient-to-br from-white to-gray-50 rounded-xl p-6 border border-gray-100 hover:shadow-lg transition-all duration-200;
}
```

#### Glass Effect
```css
.glass-effect {
  @apply bg-white/80 backdrop-blur-sm border border-white/20;
}
```

### 2. Buttons

#### Primary Button
```css
.btn-primary {
  @apply bg-gradient-to-r from-indigo-600 to-indigo-700 text-white hover:from-indigo-700 hover:to-indigo-800 shadow-lg hover:shadow-xl;
}
```

#### Outline Button
```css
.btn-outline {
  @apply border-2 border-gray-300 bg-transparent text-gray-900 hover:bg-gray-100 hover:border-indigo-600;
}
```

#### Ghost Button
```css
.btn-ghost {
  @apply text-gray-600 hover:text-gray-900 hover:bg-gray-100;
}
```

**Base Button Class**: `rounded-xl text-sm font-medium transition-all duration-200 shadow-sm hover:shadow-md`

### 3. Form Elements

#### Input Fields
```css
.input {
  @apply flex h-12 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2 focus-visible:border-indigo-600 transition-all duration-200;
}
```

**Input with Icons**: Add `pl-11` for left icon, `pr-11` for right icon

### 4. Backgrounds

#### Main Background
```css
.gradient-bg {
  @apply bg-gradient-to-br from-indigo-50 via-white to-purple-50;
}
```

#### Section Container
```css
.section-container {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
}
```

## 🔲 Spacing & Layout

### Consistent Spacing
- **Card Padding**: `p-8` (32px)
- **Section Spacing**: `space-y-6` (24px between elements)
- **Element Spacing**: `space-y-4` (16px between elements)
- **Tight Spacing**: `space-y-2` (8px between elements)

### Layout Patterns
- **Max Width**: `max-w-md` for forms, `max-w-7xl` for sections
- **Center Alignment**: `flex items-center justify-center`
- **Responsive Padding**: `p-4` mobile, scaled up for larger screens

## 🎭 Interactive States

### Hover Effects
- **Lift Effect**: `hover:-translate-y-1 hover:shadow-xl`
- **Scale Effect**: `hover:scale-105`
- **Color Transitions**: `transition-colors duration-200`

### Focus States
- **Ring Focus**: `focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2`
- **Border Focus**: `focus-visible:border-indigo-600`

### Loading States
- **Spinner**: `animate-spin rounded-full h-8 w-8 border-2 border-indigo-600 border-t-transparent`
- **Disabled**: `disabled:opacity-50 disabled:cursor-not-allowed`

## 🎨 Iconography

### Icon Standards
- **Primary Icons**: `w-5 h-5` (inline with text)
- **Large Icons**: `w-8 h-8` (hero sections)
- **Small Icons**: `w-3 h-3` (badges)
- **Colors**: `text-gray-400` (muted), `text-white` (on colored backgrounds)

### Icon Containers
- **Square Gradient**: `w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl`
- **Circle**: `w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl`

## 📱 Responsive Design

### Breakpoints
- **Mobile**: Default styles
- **Tablet**: `md:` prefix (768px+)
- **Desktop**: `lg:` prefix (1024px+)

### Typography Scaling
- **Display**: `text-4xl md:text-5xl`
- **Heading**: `text-2xl md:text-3xl`
- **Subheading**: `text-lg md:text-xl`

## 🔍 Status Indicators

### Badges
```css
.status-badge {
  @apply inline-flex items-center px-3 py-1 rounded-full text-xs font-medium;
}

.status-success { @apply bg-green-100 text-green-800; }
.status-warning { @apply bg-yellow-100 text-yellow-800; }
.status-error { @apply bg-red-100 text-red-800; }
.status-info { @apply bg-blue-100 text-blue-800; }
```

### File Type Badges
- **Container**: `inline-flex items-center px-2 py-1 rounded-full text-xs bg-indigo-100 text-indigo-800`
- **Icon**: `w-3 h-3 mr-1`

## 🎯 Design Principles

### 1. Visual Hierarchy
- Clear distinction between primary, secondary, and tertiary actions
- Consistent use of color gradients for brand identity
- Proper spacing to guide user attention

### 2. Accessibility
- High contrast ratios (gray-900 on white, white on indigo-600)
- Clear focus indicators with ring effects
- Semantic HTML structure

### 3. Consistency
- Unified border radius (`rounded-xl`, `rounded-2xl`)
- Consistent shadow system (`shadow-sm`, `shadow-lg`, `shadow-xl`)
- Standardized transition durations (`duration-200`, `duration-300`)

### 4. Modern Aesthetics
- Gradient backgrounds and buttons
- Glass morphism effects
- Smooth micro-interactions
- Professional color scheme

## 🚀 Implementation Checklist

When applying these standards to new components:

- [ ] Use `.gradient-bg` for main backgrounds
- [ ] Use `.content-card` for main content areas
- [ ] Apply `.btn-primary` for primary actions
- [ ] Use `.metric-card` for stats/overview cards
- [ ] Apply proper typography hierarchy
- [ ] Include hover states with `.hover-lift` or `.hover-scale`
- [ ] Add focus states with ring effects
- [ ] Use consistent spacing (`space-y-6`, `space-y-4`)
- [ ] Apply proper icon sizing and colors
- [ ] Include loading and disabled states
- [ ] Ensure responsive design with proper breakpoints

## 📋 Component Patterns

### Authentication Pages Pattern
```jsx
<div className="min-h-screen gradient-bg flex items-center justify-center p-4">
  <div className="w-full max-w-md">
    <!-- Navigation -->
    <Link className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-8 transition-colors">

    <!-- Main Content -->
    <div className="content-card">
      <!-- Icon and Title -->
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl mb-4">

        <h1 className="text-3xl font-bold text-gray-900 mb-2">
        <p className="text-gray-600">
      </div>

      <!-- Form Content -->
      <form className="space-y-6">
        <!-- Form Fields -->
      </form>
    </div>
  </div>
</div>
```

### Dashboard Card Pattern
```jsx
<div className="content-card">
  <div className="flex items-center justify-between mb-6">
    <h3 className="text-subheading font-semibold">
    <button className="btn btn-ghost">
  </div>

  <!-- Card Content -->
  <div className="space-y-4">
    <!-- Content Items -->
  </div>
</div>
```

This design system ensures consistency, accessibility, and a modern, professional appearance across the entire Journal Craft Crew application.