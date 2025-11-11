# Add Firebase Authentication

## Why
The current JWT-based authentication system requires manual password management and lacks social login options. Firebase Authentication provides secure, managed infrastructure with support for multiple OAuth providers (Google, GitHub), reducing development overhead and improving user experience while maintaining security standards suitable for home server deployment.

## What Changes
- **Add Firebase Authentication SDK** to both frontend and backend
- **Implement OAuth2 providers** (Google, GitHub) for social login
- **Create hybrid authentication system** supporting both Firebase and traditional email/password
- **Update user data model** to store Firebase provider information and OAuth tokens
- **Add account linking functionality** to connect social accounts to existing users
- **Implement Firebase token verification** on backend for secure authentication
- **Update authentication UI** with social login buttons and improved UX
- **Configure Firebase project settings** for home server domain and OAuth callbacks

## Impact
- **Affected specs**: `user-auth` authentication system capabilities
- **Affected code**:
  - Backend: `unified_backend.py`, authentication routes, user model
  - Frontend: Authentication context, login/register components, auth pages
  - Configuration: Environment variables, CORS settings, Firebase configuration
- **Home server requirements**: HTTPS setup, domain verification, Firebase console configuration
- **Migration approach**: Existing users preserved with optional social account linking
- **Dependencies**: Requires traditional email/password authentication to be working (see `resolve-registration-authentication-errors` change)
