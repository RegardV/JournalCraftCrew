## ADDED Requirements

### Requirement: Firebase Authentication Integration
The system SHALL integrate Firebase Authentication to provide social login capabilities alongside existing email/password authentication.

#### Scenario: Google OAuth2 login success
- **WHEN** user clicks "Sign in with Google" and completes OAuth2 flow
- **THEN** system SHALL authenticate user via Firebase and create session

#### Scenario: GitHub OAuth2 login success
- **WHEN** user clicks "Sign in with GitHub" and completes OAuth2 flow
- **THEN** system SHALL authenticate user via Firebase and create session

#### Scenario: Firebase token verification
- **WHEN** frontend sends Firebase ID token to backend
- **THEN** system SHALL verify token validity and extract user claims

### Requirement: OAuth2 Provider Support
The system SHALL support multiple OAuth2 providers through Firebase Authentication for user registration and login.

#### Scenario: Provider selection during registration
- **WHEN** new user chooses registration method
- **THEN** system SHALL display available OAuth providers (Google, GitHub) and email/password options

#### Scenario: OAuth user profile creation
- **WHEN** user authenticates via OAuth provider for first time
- **THEN** system SHALL create user profile with provider data and default settings

#### Scenario: Provider-specific data extraction
- **WHEN** user authenticates via OAuth provider
- **THEN** system SHALL extract and store profile information (name, email, avatar) from provider

### Requirement: Account Linking
The system SHALL allow users to link multiple authentication methods to a single account.

#### Scenario: Link social account to existing user
- **WHEN** authenticated user chooses to link Google or GitHub account
- **THEN** system SHALL associate OAuth provider with existing user account

#### Scenario: Switch between authentication methods
- **WHEN** user with linked accounts attempts login
- **THEN** system SHALL allow authentication via any linked method

#### Scenario: Unlink authentication method
- **WHEN** user chooses to unlink social account
- **THEN** system SHALL remove provider association while preserving user account

### Requirement: Home Server Firebase Configuration
The system SHALL support Firebase Authentication deployment on home server infrastructure with custom domains.

#### Scenario: Development environment configuration
- **WHEN** system runs in development mode
- **THEN** system SHALL use Firebase configuration for localhost domains

#### Scenario: Production domain verification
- **WHEN** deploying to production home server
- **THEN** system SHALL support custom domain verification in Firebase Console

#### Scenario: HTTPS requirement enforcement
- **WHEN** system runs in production mode
- **THEN** system SHALL enforce HTTPS for all Firebase OAuth callbacks

## MODIFIED Requirements

### Requirement: User Registration
The system SHALL support user registration via both traditional email/password and Firebase OAuth providers.

#### Scenario: Traditional email/password registration
- **WHEN** user registers with email and password
- **THEN** system SHALL create account with traditional authentication method

#### Scenario: OAuth provider registration
- **WHEN** user registers via Google or GitHub
- **THEN** system SHALL create account using Firebase provider information

#### Scenario: Registration validation
- **WHEN** user submits registration (any method)
- **THEN** system SHALL validate unique email and prevent duplicate accounts

### Requirement: User Authentication
The system SHALL authenticate users via JWT tokens generated from both traditional and Firebase authentication methods.

#### Scenario: Traditional login authentication
- **WHEN** user logs in with email/password
- **THEN** system SHALL validate credentials and generate JWT token

#### Scenario: Firebase login authentication
- **WHEN** user logs in via OAuth provider
- **THEN** system SHALL verify Firebase token and generate JWT token

#### Scenario: Token validation middleware
- **WHEN** protected API endpoint is accessed
- **THEN** system SHALL validate JWT token regardless of authentication method
