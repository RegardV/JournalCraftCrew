# Firebase Authentication Design

## Context
The Journal Craft Crew platform currently uses a custom JWT authentication system with bcrypt password hashing. The platform runs on a home server environment with custom domains and requires HTTPS for production. Users need secure authentication options with minimal infrastructure maintenance overhead.

### Home Server Environment Constraints
- Dynamic DNS or static IP setup required
- HTTPS certificate management (Let's Encrypt recommended)
- Port forwarding configuration (80 → 443)
- Firebase domain verification process
- OAuth callback URL configuration

## Goals / Non-Goals
**Goals:**
- Provide social login options (Google, GitHub) for improved user experience
- Reduce authentication infrastructure maintenance overhead
- Maintain security standards with managed Firebase authentication
- Preserve existing user accounts and authentication methods
- Enable account linking between social and traditional authentication
- Support home server deployment with custom domains

**Non-Goals:**
- Replace existing JWT system entirely (hybrid approach instead)
- Implement phone number authentication
- Add enterprise SSO providers
- Multi-tenant authentication architecture

## Decisions

### Decision 1: Firebase Authentication vs Direct OAuth2
**Choice**: Firebase Authentication
**Rationale**:
- Managed OAuth token lifecycle and refresh handling
- Built-in security features and fraud detection
- Simplified user management console
- Reduced development and maintenance overhead
- Automatic security updates and compliance

**Alternatives considered**:
- Direct OAuth2 implementation: More control but higher complexity and maintenance burden
- Auth0/Clerk: Third-party services with additional costs and vendor lock-in

### Decision 2: Hybrid Authentication Architecture
**Choice**: Support both Firebase social login and existing email/password
**Rationale**:
- Preserve existing user accounts and migration path
- Allow gradual adoption of social authentication
- Maintain system flexibility for user preferences
- Reduce migration risk and user friction

### Decision 3: Firebase Project Structure
**Choice**: Single Firebase project for both development and production environments
**Rationale**:
- Simplified configuration management
- Cost-effective for home server deployment
- Easy environment separation via Firebase authentication domains

## Home Server Technical Architecture

### Firebase Configuration Requirements
```
Development Environment:
- Frontend: http://localhost:5176
- Backend: http://localhost:6770
- Firebase Auth Domain: localhost
- OAuth Callbacks: http://localhost:5176/auth/callback

Production Environment:
- Frontend: https://your-home-domain.com
- Backend: https://your-home-domain.com/api
- Firebase Auth Domain: your-home-domain.com
- OAuth Callbacks: https://your-home-domain.com/auth/callback
```

### Network Infrastructure
```
Home Server Setup:
1. Dynamic DNS Service (if no static IP)
2. Port Forwarding: 80 → 443 (HTTPS)
3. SSL Certificate (Let's Encrypt)
4. Firebase Domain Verification
5. OAuth Provider Configuration
```

### Security Implementation
- Firebase token verification on all backend protected routes
- CORS configuration for Firebase domains
- Rate limiting on authentication endpoints
- HTTPS enforcement for production
- Firebase security rules integration

## Risks / Trade-offs

### Risk: Firebase Service Dependency
**Mitigation**: Maintain hybrid authentication system, implement local fallback mechanisms
**Impact**: Medium - Service availability affects authentication

### Risk: Home Server HTTPS Management
**Mitigation**: Automated Let's Encrypt certificate renewal, backup manual certificates
**Impact**: High - HTTPS required for Firebase OAuth callbacks

### Trade-off: Vendor Lock-in vs Managed Infrastructure
**Decision**: Accept Firebase vendor lock-in for reduced maintenance overhead
**Alternative**: Direct OAuth2 implementation considered but rejected for complexity

### Risk: Domain Verification Complexity
**Mitigation**: Step-by-step documentation, automated DNS configuration scripts
**Impact**: Medium - Initial setup complexity

## Migration Plan

### Phase 1: Firebase Project Setup
1. Create Firebase project at console.firebase.google.com
2. Configure authentication providers (Google, GitHub)
3. Set up development domains (localhost)
4. Generate Firebase configuration keys
5. Test OAuth flows in development environment

### Phase 2: Backend Integration
1. Install Firebase Admin SDK
2. Create Firebase authentication service
3. Update user model with provider fields
4. Implement token verification endpoints
5. Add account linking functionality
6. Update existing authentication routes

### Phase 3: Frontend Integration
1. Install Firebase JS SDK
2. Create social login components
3. Update authentication context
4. Add OAuth sign-in buttons
5. Implement Firebase callback handling
6. Update registration/login forms

### Phase 4: Production Deployment
1. Configure production domain in Firebase Console
2. Set up HTTPS certificate on home server
3. Configure OAuth callbacks for production domain
4. Test end-to-end authentication flows
5. Monitor system performance and security

### Rollback Strategy
- Maintain existing JWT authentication system
- Implement feature flags for Firebase authentication
- Keep migration scripts for account data
- Monitor error rates and user feedback

## Open Questions

### Technical Implementation
1. Should we implement real-time Firebase authentication state synchronization?
2. How should we handle Firebase token refresh in long-running sessions?
3. What is the optimal strategy for storing Firebase provider tokens?

### User Experience
1. Should we prioritize one OAuth provider over another in the UI?
2. How should we present account linking options to existing users?
3. What is the best approach for handling authentication errors from Firebase?

### Home Server Specific
1. What is the user's preferred domain for production deployment?
2. Should we provide automated SSL certificate setup scripts?
3. How should we handle dynamic DNS configuration for home server environments?

## Security Considerations

### Firebase Security Integration
- Implement proper Firebase project security rules
- Configure OAuth provider scopes appropriately
- Set up Firebase authentication email verification
- Monitor Firebase authentication events and anomalies

### Home Server Security
- Enforce HTTPS for all authentication endpoints
- Implement proper CORS policies for Firebase domains
- Configure firewall rules for OAuth provider communication
- Set up authentication event logging and monitoring