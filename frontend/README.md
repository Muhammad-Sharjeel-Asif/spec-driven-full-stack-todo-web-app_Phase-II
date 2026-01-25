# Todo Web Application - Frontend

This is the frontend of the Todo Web Application built with Next.js 14+, TypeScript, and Tailwind CSS.

## Features

- Next.js 14+ with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Better Auth for authentication
- React Hook Form for form handling
- Jest and React Testing Library for testing
- Modern project structure with clean architecture

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── layout.tsx    # Root layout
│   │   └── page.tsx      # Home page
│   ├── components/       # Reusable UI components
│   ├── lib/             # Utility libraries
│   ├── styles/          # Global styles
│   ├── types/           # TypeScript type definitions
│   └── utils/           # Utility functions
├── styles/              # Global CSS
├── public/              # Static assets
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript configuration
├── next.config.js       # Next.js configuration
├── tailwind.config.js   # Tailwind CSS configuration
├── postcss.config.js    # PostCSS configuration
└── jest.config.js       # Jest testing configuration
```

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run test` - Run tests
- `npm run test:watch` - Run tests in watch mode

## Dependencies

- `next`: Latest Next.js version with App Router
- `react` & `react-dom`: React library
- `better-auth`: Authentication solution
- `react-hook-form`: Form handling library
- `typescript`: Type checking
- `tailwindcss`: Styling framework
- `jest` & `@testing-library/*`: Testing utilities