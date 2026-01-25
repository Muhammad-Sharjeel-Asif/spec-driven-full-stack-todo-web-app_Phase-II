# Quickstart Guide: Frontend for Phase II Todo Full-Stack Web Application

## Prerequisites

- Node.js 18.x or higher
- npm or yarn package manager
- Git version control system
- Access to the backend API (assumed endpoints)

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

3. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

4. **Create environment file:**
   Copy the example environment file and update the values:
   ```bash
   cp .env.example .env.local
   ```

   Update the following variables in `.env.local`:
   - `NEXT_PUBLIC_API_URL`: The URL of your backend API
   - `NEXT_PUBLIC_BETTER_AUTH_URL`: The URL for your Better Auth instance

5. **Run the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

6. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000) to see the application.

## Available Scripts

- `npm run dev` - Start development server with hot reloading
- `npm run build` - Build the application for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint to check for code issues
- `npm run test` - Run unit tests
- `npm run test:watch` - Run unit tests in watch mode
- `npm run test:e2e` - Run end-to-end tests

## Key Configuration

The application uses Next.js App Router with the following key configurations:

- Authentication is handled via Better Auth
- API calls are made through the centralized API client with JWT token management
- Styling is implemented with Tailwind CSS
- Forms use React Hook Form for validation and accessibility
- TypeScript is enforced throughout the codebase