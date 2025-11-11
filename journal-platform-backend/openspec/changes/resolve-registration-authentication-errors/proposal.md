# Resolve Registration Authentication Errors

## Why
The user registration system was experiencing persistent 500 Internal Server Error responses due to bcrypt password length limitations. The passlib library was validating password length (72-byte limit) before our truncation logic could handle long passwords, causing registration failures for both short and long passwords.

## What Changes
- **Replace passlib with direct bcrypt calls** in unified_backend.py hash_password() and verify_password() functions
- **Implement manual salt generation** using bcrypt.gensalt() for password hashing
- **Add explicit password truncation** to 72 bytes before bcrypt processing
- **Optimize password requirements** from 8+ chars with 4 character types to 6+ chars with 2 of 4 character types
- **Clean up CORS configuration** to use only essential ports (3000, 5173)
- **Enhance frontend error handling** for 422 validation errors that were previously displayed as 500 errors
- **Maintain backward compatibility** with existing password hashes

## Impact
- **Affected specs**: `auth` authentication system password handling and validation
- **Affected code**:
  - Backend: `unified_backend.py` (lines 97-125) - password hashing functions
  - Backend: `app/utils/validation.py` (lines 84-115) - password requirements validation
  - Frontend: `src/pages/auth/RegisterPage.tsx` - password requirements UI display
  - Frontend: `src/lib/api.ts` - enhanced validation error handling
  - Backend: `app/middleware/security.py` - CORS configuration cleanup
- **Security improvements**: Proper bcrypt implementation with automatic password truncation
- **User experience**: More user-friendly password requirements and better error feedback
- **Compatibility**: Existing user passwords continue to work without migration