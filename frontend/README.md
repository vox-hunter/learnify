# Learnify Frontend

## Quick Start

### Prerequisites
* Node.js 18+ (LTS recommended)
* npm 9+ or yarn 3+
* Git

### Installation
```bash
# Install dependencies
npm install

# Copy environment file (if needed)
cp .env.example .env.local

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

## Available Scripts

### Development
* `npm run dev` - Start development server with HMR
* `npm run dev:host` - Start dev server accessible from network

### Building
* `npm run build` - Create production build
* `npm run preview` - Preview production build locally

### Testing
* `npm run test` - Run unit tests
* `npm run test:watch` - Run tests in watch mode
* `npm run test:coverage` - Generate test coverage report

### Code Quality
* `npm run lint` - Run ESLint
* `npm run lint:fix` - Fix ESLint errors
* `npm run type-check` - Run TypeScript compiler check

## Project Structure

```
src/
├── components/        # Reusable UI components
│   ├── ui/           # Base UI components
│   ├── forms/        # Form components
│   └── layout/       # Layout components
├── pages/            # Page components
├── hooks/            # Custom React hooks
├── services/         # API services
├── utils/            # Utility functions
├── types/            # TypeScript definitions
├── styles/           # Global styles
└── assets/           # Static assets
```

## Environment Variables

Create a `.env.local` file for local development:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:3000/api

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_NOTIFICATIONS=true

# Development
VITE_LOG_LEVEL=debug
```

## Technology Stack

* **React 18+** - Modern React with Hooks and Concurrent Features
* **TypeScript 5.x** - Type-safe JavaScript
* **Vite 5.x** - Fast build tool with HMR
* **React Router** - Client-side routing
* **React Query** - Data fetching and caching
* **Tailwind CSS** - Utility-first styling
* **React Testing Library** - Component testing
* **Jest** - Test runner

## Key Features

### Accessibility
* ARIA compliant components
* Keyboard navigation support
* Screen reader compatibility
* Focus management
* High contrast mode support

### Performance
* Code splitting and lazy loading
* Bundle size optimization
* Image optimization
* Performance monitoring
* Service worker support

### User Experience
* Responsive design
* Dark/light theme support
* Offline functionality
* Real-time notifications
* Progressive Web App features

## Development Guidelines

### Code Style
* Use TypeScript for all new files
* Follow React Hooks patterns
* Implement proper error handling
* Write tests for components
* Use semantic HTML elements

### Component Structure
```typescript
// Example component structure
interface ComponentProps {
  prop: string;
}

export const Component: React.FC<ComponentProps> = ({ prop }) => {
  // Custom hooks
  const { data, loading, error } = useData();
  
  // Event handlers
  const handleClick = () => {
    // Handle click
  };
  
  // Render
  return (
    <div>
      {/* Component content */}
    </div>
  );
};
```

### Testing
* Unit tests for components
* Integration tests for user flows  
* Accessibility tests
* Performance tests
* Mock external dependencies

## Deployment

### Build for Production
```bash
npm run build
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

## Browser Support
* Chrome 90+
* Firefox 88+
* Safari 14+
* Edge 90+

## Performance Targets
* First Contentful Paint (FCP): < 1.5s
* Largest Contentful Paint (LCP): < 2.5s
* First Input Delay (FID): < 100ms
* Cumulative Layout Shift (CLS): < 0.1

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Troubleshooting

### Common Issues

**Development server won't start:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Build errors:**
```bash
npm run type-check
npm run lint
```

**Memory issues:**
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

For more help, check the documentation in the `src/docs/` directory.