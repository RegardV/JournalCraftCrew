## Why
The current AI credit system (10 credits for personal journalers, 50 for content creators) creates artificial limitations and doesn't scale with actual OpenAI API costs. Users should have direct control over their AI usage by bringing their own OpenAI API keys, eliminating the need for platform-managed credits and providing unlimited usage based on their own OpenAI account.

## What Changes
- **Remove AI Credit System**: Eliminate ai_credits field from user model and all related functionality
- **Add OpenAI API Key Storage**: Securely store and manage user-provided OpenAI API keys
- **Direct API Integration**: Replace mock AI generation with actual OpenAI API calls using user keys
- **Usage Cost Transparency**: Show users real OpenAI API costs and usage statistics
- **Key Security**: Implement secure key storage, validation, and usage monitoring
- **Unlimited Usage**: Remove artificial limits while providing cost visibility

## Impact
- **Affected specs**: Remove ai-credit system specs, add new api-key-management capability
- **Affected code**:
  - All backend files with ai_credits logic (testing_server.py, auth_service.py, user models)
  - User registration/profile management (remove profile type based credit allocation)
  - AI generation endpoints (integrate real OpenAI API)
  - Frontend user profile pages (add API key management)
- **Database Changes**: Remove ai_credits column, add encrypted OpenAI API key storage
- **User Experience**: Transform from limited credit system to unlimited, cost-transparent usage