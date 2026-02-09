# UI Implementation Guide

Comprehensive guide for the Todo Application UI built with Next.js 16+, TypeScript, and Tailwind CSS.

## Overview

This UI implementation provides a modern, accessible, and visually stunning interface for the Todo application. Built with performance and user experience in mind, it features smooth animations, responsive design, and a carefully crafted color palette.

## Technology Stack

- **Next.js 16+**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS 4**: Utility-first CSS framework
- **React 19**: Latest React features
- **Better Auth**: Authentication integration

## Design System

### Color Palette

The application uses a custom color palette designed for visual appeal:

- **Bubblegum Pink**: Primary brand color (#fb3d87)
- **Lavender Blush**: Secondary accent (#d55fd0)
- **Coffee Bean**: Neutral tones (#87796d)
- **Black Cherry**: Dark accents (#c23d5e)
- **Cinnabar**: Alert/error states (#ee4f44)

Each color has 10 shades (50-900) for flexibility.

### Typography

- **Font Family**: System fonts with fallbacks
- **Font Sizes**: Responsive scale from xs (0.75rem) to 6xl (3.75rem)
- **Line Heights**: Optimized for readability

### Spacing

- Standard Tailwind spacing scale
- Custom additions: 18 (4.5rem), 88 (22rem), 112 (28rem), 128 (32rem)

### Animations

Custom animations for smooth interactions:
- `fade-in/out`: Opacity transitions
- `slide-in/out`: Vertical movement
- `scale-in/out`: Scale transformations
- `bounce-subtle`: Gentle bounce effect
- `pulse-subtle`: Breathing animation

## Component Library

### Base UI Components

Located in `src/components/ui/`:

#### Button
Versatile button component with multiple variants:
- **Variants**: primary, secondary, ghost, outline, destructive
- **Sizes**: sm, md, lg
- **States**: loading, disabled
- **Accessibility**: ARIA labels, keyboard navigation

#### Card
Container component for content grouping:
- **Parts**: CardHeader, CardContent, CardFooter
- **Variants**: default, elevated, bordered
- **Responsive**: Adapts to screen size

#### Input
Form input with validation:
- **Types**: text, email, password, number, etc.
- **States**: error, success, disabled
- **Features**: label, helper text, validation messages
- **Accessibility**: ARIA attributes, proper labeling

#### Badge
Status indicators and labels:
- **Variants**: primary, secondary, success, warning, error
- **Sizes**: sm, md, lg
- **Use cases**: status, counts, tags

#### Avatar
User profile images with fallbacks:
- **Sizes**: xs, sm, md, lg, xl
- **Fallback**: Initials from name
- **Features**: Image error handling

#### Modal
Overlay dialogs:
- **Features**: Focus trap, ESC to close, backdrop click
- **Accessibility**: ARIA dialog, focus management
- **Animations**: Smooth open/close transitions

#### Dropdown
Contextual menus:
- **Features**: Keyboard navigation, auto-positioning
- **Accessibility**: ARIA menu, focus management
- **Use cases**: User menus, filters, actions

#### Skeleton
Loading placeholders:
- **Variants**: text, circular, rectangular
- **Animation**: Pulse effect
- **Use cases**: Content loading states

#### Toast
Notification system:
- **Types**: success, error, warning, info
- **Features**: Auto-dismiss, action buttons
- **Position**: Configurable placement

#### Tooltip
Contextual help:
- **Features**: Hover/focus trigger, auto-positioning
- **Accessibility**: ARIA describedby
- **Delay**: Configurable show/hide timing

### Layout Components

Located in `src/components/layout/`:

#### Navbar
Top navigation bar:
- **Features**: Logo, navigation links, user menu
- **Responsive**: Mobile hamburger menu
- **Sticky**: Fixed to top on scroll

#### Sidebar
Side navigation:
- **Features**: Navigation links, user profile section
- **Responsive**: Hidden on mobile, drawer on tablet
- **Collapsible**: Can be toggled

#### Header
Page header:
- **Features**: Title, description, action buttons
- **Responsive**: Stacks on mobile
- **Flexible**: Customizable content

#### MainLayout
Main application layout:
- **Structure**: Navbar + Sidebar + Content
- **Responsive**: Adapts to all screen sizes
- **Semantic**: Proper HTML5 structure

#### Footer
Page footer:
- **Features**: Copyright, links
- **Minimal**: Unobtrusive design

### Task Components

Located in `src/components/tasks/`:

#### TaskCard
Individual task display:
- **Features**: Title, description, status, priority
- **Actions**: Complete, edit, delete
- **Animations**: Hover effects, completion animation
- **Accessibility**: Keyboard actions, ARIA labels

#### TaskList
Task collection display:
- **Features**: Virtualization for performance
- **States**: Loading, empty, error
- **Animations**: Staggered fade-in

#### TaskForm
Task creation/editing:
- **Features**: All task fields, validation
- **States**: Creating, editing
- **Validation**: Real-time feedback

#### TaskFilter
Filtering and sorting:
- **Filters**: Status, priority, completion
- **Sort**: Multiple fields, ascending/descending
- **UI**: Dropdown menus, active filter badges

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   ├── auth/              # Authentication pages
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── forgot-password/
│   │   └── dashboard/         # Dashboard pages
│   │       ├── layout.tsx     # Dashboard layout
│   │       ├── page.tsx       # Dashboard home
│   │       ├── tasks/         # Task pages
│   │       ├── statistics/    # Analytics pages
│   │       └── settings/      # Settings pages
│   ├── components/
│   │   ├── ui/               # Base UI components
│   │   ├── layout/           # Layout components
│   │   ├── tasks/            # Task-specific components
│   │   └── auth/             # Auth components
│   ├── hooks/                # Custom React hooks
│   ├── lib/                  # Utilities and helpers
│   ├── providers/            # Context providers
│   ├── styles/               # Global styles
│   └── types/                # TypeScript types
├── public/                   # Static assets
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json            # TypeScript configuration
├── next.config.ts           # Next.js configuration
└── package.json             # Dependencies
```

## Responsive Design

### Breakpoints

- **sm**: 640px (Mobile landscape, small tablets)
- **md**: 768px (Tablets)
- **lg**: 1024px (Laptops, small desktops)
- **xl**: 1280px (Desktops)
- **2xl**: 1536px (Large desktops)

### Mobile-First Approach

All components are designed mobile-first, then enhanced for larger screens:

```tsx
// Mobile: Stack vertically
// Desktop: Side by side
<div className="flex flex-col lg:flex-row">
```

## Accessibility

### WCAG 2.1 AA Compliance

- **Color Contrast**: All text meets 4.5:1 ratio
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Proper ARIA labels and roles
- **Focus Management**: Visible focus indicators
- **Semantic HTML**: Proper heading hierarchy

### Best Practices

1. **Always use semantic HTML**
2. **Provide alt text for images**
3. **Use ARIA attributes appropriately**
4. **Ensure keyboard accessibility**
5. **Test with screen readers**
6. **Respect reduced motion preferences**

## Performance

### Optimization Techniques

1. **Code Splitting**: Automatic with Next.js
2. **Image Optimization**: Next.js Image component
3. **Lazy Loading**: React.lazy for heavy components
4. **Virtualization**: For long lists
5. **Memoization**: React.memo for expensive renders

### Performance Targets

- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3.5s
- **Lighthouse Score**: > 90

## Development

### Running Locally

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000

### Building for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## Component Usage Examples

### Button

```tsx
import Button from '@/components/ui/Button';

<Button variant="primary" size="md" onClick={handleClick}>
  Click Me
</Button>
```

### Card

```tsx
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/Card';

<Card>
  <CardHeader>
    <h3>Title</h3>
  </CardHeader>
  <CardContent>
    <p>Content goes here</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Modal

```tsx
import Modal from '@/components/ui/Modal';

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm Action"
>
  <p>Are you sure?</p>
  <Button onClick={handleConfirm}>Confirm</Button>
</Modal>
```

## Styling Guidelines

### Tailwind Best Practices

1. **Use utility classes**: Prefer utilities over custom CSS
2. **Extract components**: For repeated patterns
3. **Use @apply sparingly**: Only for complex patterns
4. **Responsive design**: Mobile-first approach
5. **Dark mode**: Use dark: prefix for dark mode styles

### Custom Classes

Avoid custom CSS when possible. If needed, add to `globals.css`:

```css
@layer components {
  .custom-class {
    @apply flex items-center justify-center;
  }
}
```

## Testing

### Component Testing

```bash
npm test
```

### Accessibility Testing

- Use axe DevTools browser extension
- Test with keyboard only
- Test with screen reader (NVDA, JAWS, VoiceOver)

## Deployment

### Vercel (Recommended)

```bash
vercel
```

### Docker

```bash
docker build -t todo-frontend .
docker run -p 3000:3000 todo-frontend
```

## Troubleshooting

### Common Issues

**Tailwind classes not working**
- Check `tailwind.config.ts` content paths
- Restart dev server

**TypeScript errors**
- Run `npm run type-check`
- Check `tsconfig.json` configuration

**Build errors**
- Clear `.next` directory
- Delete `node_modules` and reinstall

## Contributing

### Code Style

- Use TypeScript for all components
- Follow ESLint rules
- Use Prettier for formatting
- Write meaningful commit messages

### Component Checklist

- [ ] TypeScript types defined
- [ ] Accessibility features implemented
- [ ] Responsive design tested
- [ ] Dark mode support
- [ ] Loading states handled
- [ ] Error states handled
- [ ] Documentation added

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Documentation](https://react.dev)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
