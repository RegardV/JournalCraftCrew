## ADDED Requirements

### Requirement: OpenAI API Key Management
The system SHALL allow users to securely store and manage their own OpenAI API keys for AI journal generation.

#### Scenario: User adds OpenAI API key
- GIVEN user is logged into their account
- WHEN user navigates to API key settings
- THEN user SHALL be able to input their OpenAI API key
- AND system SHALL validate the key with OpenAI
- AND system SHALL store the key securely using encryption
- AND user SHALL receive confirmation of successful key addition

#### Scenario: User validates API key
- GIVEN user has entered an OpenAI API key
- WHEN user submits the key for validation
- THEN system SHALL make a test call to OpenAI API
- AND system SHALL verify the key has appropriate permissions
- AND system SHALL return validation result to user
- AND invalid keys SHALL be rejected with clear error message

### Requirement: Secure Key Storage
The system SHALL implement enterprise-grade security for storing user API keys.

#### Scenario: Key encryption at rest
- GIVEN user has provided an OpenAI API key
- WHEN key is stored in database
- THEN key SHALL be encrypted using AES-256 encryption
- AND encryption keys SHALL be managed securely
- AND keys SHALL never be stored in plain text
- AND database access SHALL not expose unencrypted keys

#### Scenario: Key transmission security
- GIVEN user is submitting their API key
- WHEN key is transmitted to server
- THEN transmission SHALL use HTTPS/TLS encryption
- AND key SHALL not be logged or cached
- AND memory SHALL be cleared after processing
- AND headers SHALL prevent caching of sensitive data

### Requirement: Cost Transparency and Usage Tracking
The system SHALL provide real-time cost tracking and usage statistics for OpenAI API usage.

#### Scenario: User generates journal content
- GIVEN user initiates AI journal generation
- WHEN generation process completes
- THEN system SHALL track token usage
- AND system SHALL calculate actual API cost incurred
- AND user SHALL see cost breakdown in their usage history
- AND system SHALL update running cost totals

#### Scenario: User views usage dashboard
- GIVEN user has used AI generation features
- WHEN user navigates to usage statistics
- THEN user SHALL see total API costs incurred
- AND user SHALL see usage trends over time
- AND user SHALL see cost per generation type
- AND system SHALL show estimated costs for future generations

### Requirement: API Integration and Error Handling
The system SHALL integrate seamlessly with OpenAI API while handling edge cases gracefully.

#### Scenario: API rate limit exceeded
- GIVEN user exceeds OpenAI API rate limits
- WHEN API call is made
- THEN system SHALL detect rate limit error
- AND user SHALL receive clear rate limit notification
- AND system SHALL implement exponential backoff retry
- AND user SHALL be informed when to try again

#### Scenario: Invalid API key during generation
- GIVEN user's API key becomes invalid
- WHEN system attempts to make API call
- THEN system SHALL handle authentication error
- AND user SHALL be notified of key invalidity
- AND system SHALL prompt user to update their key
- AND generation job SHALL be paused until key is updated

### Requirement: Key Lifecycle Management
The system SHALL provide full lifecycle management for API keys including rotation and deletion.

#### Scenario: User rotates API key
- GIVEN user wants to replace their existing API key
- WHEN user submits new key
- THEN system SHALL validate the new key
- AND old key SHALL be securely deleted
- AND new key SHALL replace the old one
- AND user SHALL receive confirmation of successful rotation

#### Scenario: User deletes API key
- GIVEN user wants to remove their API key from the system
- WHEN user confirms key deletion
- THEN system SHALL immediately revoke access
- AND key SHALL be securely deleted from database
- AND user SHALL be notified of account AI access removal
- AND all queued generation jobs SHALL be cancelled

## REMOVED Requirements

### Requirement: AI Credit Allocation
**Reason**: The artificial credit system limits user flexibility and doesn't reflect actual API costs.
**Migration**: Replace with direct API key usage where users pay OpenAI directly.

#### Scenario: User registration credit allocation
- ~~GIVEN new user registers with profile type~~
- ~~WHEN account is created~~
- ~~THEN system SHALL allocate 10 credits for personal journaler~~
- ~~OR system SHALL allocate 50 credits for content creator~~

### Requirement: Credit Consumption Tracking
**Reason**: Credit tracking is replaced by actual cost tracking from OpenAI API.
**Migration**: Replace credit deduction with cost calculation and display.

#### Scenario: AI generation credit deduction
- ~~GIVEN user initiates AI generation~~
- ~~WHEN generation starts~~
- ~~THEN system SHALL deduct appropriate credits~~
- ~~AND user SHALL see remaining credit balance~~
- ~~AND generation SHALL fail if insufficient credits~~