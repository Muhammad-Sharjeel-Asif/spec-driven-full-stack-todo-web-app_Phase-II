// Better Auth client configuration
import { initClient } from 'better-auth/client';
import { betterAuth } from 'better-auth';

// Initialize the client
export const authClient = initClient(betterAuth(), {
  fetch: globalThis.fetch,
});