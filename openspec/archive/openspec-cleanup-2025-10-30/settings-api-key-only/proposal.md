# Perfect Authentication with Settings-Based API Key Management

## Purpose
Restore the perfect authentication design from the archived industry-standard UI spec, but move OpenAI API key management exclusively to the settings area for a cleaner, more professional user experience.

## Why
The current authentication interface includes API key management on the registration/login forms, which creates friction during onboarding and complicates the authentication flow. Users should be able to:

1. Create accounts easily without technical complexity
2. Log in seamlessly without needing to remember API keys
3. Add API keys later when they're ready to use AI features
4. Manage API keys in a dedicated settings area

The archived authentication UI was perfect for user experience - we need to maintain that design while moving API key functionality to settings.

## What Changes
- **Restore Perfect Authentication Design**: Use the exact design patterns from `2025-10-27-industry-auth-ui`
- **Remove API Key from Registration/Login**: Simplify forms to email, username, password, and full name only
- **Add Settings-Based API Key Management**: Create a dedicated settings area for API key management
- **Enhanced Dashboard Flow**: Guide users to add API key when they first try to create journals
- **Clear API Key Education**: Provide helpful guidance in settings when users are ready to add their key

## Implementation Plan

### Phase 1: Restore Perfect Authentication Design
- Implement the exact authentication design from the archived spec
- Remove all API key fields from registration and login forms
- Maintain all the accessibility, validation, and security features
- Keep the modern, professional visual design

### Phase 2: Create Settings-Based API Key Management
- Build a dedicated settings page with API key management
- Add API key validation, update, and delete functionality
- Include helpful guidance and links to get OpenAI API keys
- Implement secure key storage with encryption

### Phase 3: Enhanced User Guidance
- Add clear prompts when users try AI features without an API key
- Create onboarding flow to guide users to settings for key setup
- Add API key status indicators in the dashboard
- Provide helpful tooltips and educational content

### Phase 4: Polish and Testing
- Ensure seamless flow from authentication to settings
- Test all API key management scenarios
- Verify security and encryption implementation
- Validate user experience and accessibility compliance

## Success Metrics
- Reduced friction during user registration and login
- Higher conversion rates for account creation
- Better understanding of API key requirements
- Improved user satisfaction with clean, professional interface
- Enhanced security with settings-based key management

## User Impact
- **Easier Onboarding**: Users can create accounts without technical complexity
- **Cleaner Experience**: Authentication forms are simple and focused
- **Better Organization**: API key management is logically placed in settings
- **Educated Users**: Clear guidance when API keys are needed
- **Professional Interface**: Maintains the high-quality design from archived spec

## Technical Changes
- Update authentication forms to remove API key fields
- Create new settings page for API key management
- Implement dashboard prompts for API key setup
- Update user data models and validation
- Ensure secure key storage and management in settings