## 1. Remove AI Credit System
- [x] 1.1 Remove ai_credits field from user database model
- [x] 1.2 Remove ai_credits logic from all server files (testing_server.py, auth_service.py, etc.)
- [x] 1.3 Remove profile type based credit allocation from registration
- [x] 1.4 Remove credit checking logic from AI generation endpoints

## 2. OpenAI API Key Management
- [x] 2.1 Add encrypted openai_api_key field to user model
- [x] 2.2 Create API key validation endpoint (check key validity with OpenAI)
- [x] 2.3 Implement secure key storage using environment encryption
- [x] 2.4 Add API key update/delete functionality

## 3. OpenAI API Integration
- [x] 3.1 Install OpenAI Python SDK
- [x] 3.2 Replace mock AI generation with real OpenAI API calls
- [x] 3.3 Implement proper error handling for API failures
- [x] 3.4 Add rate limiting based on OpenAI API limits

## 4. Cost Tracking & Usage
- [x] 4.1 Implement token usage tracking for each generation
- [x] 4.2 Calculate and display real OpenAI API costs
- [x] 4.3 Create usage statistics dashboard
- [x] 4.4 Add cost estimates before generation

## 5. Frontend Updates
- [x] 5.1 Remove AI credit display from user profile
- [x] 5.2 Add API key management interface in user settings
- [x] 5.3 Update registration form (remove profile type, add API key option)
- [x] 5.4 Add cost tracking display to generation interface

## 6. Security Implementation
- [x] 6.1 Implement server-side encryption for stored API keys
- [x] 6.2 Add API key usage monitoring and alerts
- [x] 6.3 Implement key rotation functionality
- [x] 6.4 Add security headers and validation for API endpoints

## 7. Data Migration
- [x] 7.1 Create migration script to remove ai_credits from existing users
- [x] 7.2 Update existing user accounts to remove credit limits
- [x] 7.3 Back up current data before migration
- [x] 7.4 Test migration on development data first

## 8. Testing & Validation
- [x] 8.1 Test API key validation with real OpenAI keys
- [x] 8.2 Test cost calculation accuracy
- [x] 8.3 Test security of key storage and transmission
- [x] 8.4 Test edge cases (invalid keys, API outages, etc.)