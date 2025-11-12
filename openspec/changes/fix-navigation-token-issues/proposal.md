## Why
Navigation and authentication issues are preventing users from accessing core platform features. Multiple critical problems exist:

1. **Settings page redirects to login** - Token storage mismatch between 'token' and 'access_token' keys
2. **Profile and Subscription pages inaccessible** - Same token authentication issue
3. **Empty Active Projects section** - No way to access AI generation workflow from dashboard
4. **Blank Analytics view** - No analytics dashboard implementation
5. **Broken menu navigation** - Missing routes and incorrect link mappings

These issues create a broken user experience where users cannot access essential platform functionality after successful login.

## What Changes

### 1. Fix Token Authentication Issues
- **Token Key Standardization**: Fix mismatch between localStorage keys ('token' vs 'access_token')
- **Settings Page Token Fix**: Update SettingsPage.tsx to use correct 'access_token' key
- **Authentication Flow**: Ensure consistent token retrieval across all protected routes

### 2. Add Missing Dashboard Functionality
- **Active Projects Enhancement**: Add link to AI workflow generation page
- **Analytics Dashboard**: Implement basic analytics view with user metrics
- **Dashboard Navigation**: Improve user journey from dashboard to AI features

### 3. Complete Menu Navigation
- **Create Settings Page**: Implement full settings interface with API key management
- **Fix Route Mappings**: Correct all sidebar navigation links
- **Remove Broken Links**: Eliminate non-existent routes (Collaborations)

## Impact
- **Affected specs**: navigation (menu navigation, dashboard views), authentication (token management)
- **Affected code**:
  - `journal-platform-frontend/src/pages/settings/SettingsPage.tsx:24,44` (token key fixes)
  - `journal-platform-frontend/src/components/layout/Sidebar.tsx:37,83` (navigation fixes)
  - `journal-platform-frontend/src/App.tsx:162-167,235` (settings route)
  - Dashboard components (analytics, active projects)
- **User Experience**: Users can now access all platform features without login redirects
- **Platform Functionality**: Complete navigation between all sections including Settings, AI Workflow, Analytics
- **Authentication**: Consistent token-based authentication across all protected routes

## Implementation Priority
1. **Critical**: Token authentication fixes (already implemented)
2. **High**: Dashboard analytics and active projects enhancement
3. **Medium**: Enhanced analytics dashboard implementation
4. **Low**: UI/UX improvements and additional features

The fixes ensure users have complete access to the Journal Craft Crew platform functionality with proper authentication and intuitive navigation.