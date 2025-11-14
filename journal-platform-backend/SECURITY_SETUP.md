# 🔐 Journal Platform Backend - Security Setup Guide

This document provides comprehensive instructions for setting up secure secrets management and configuring the production environment.

## 🚀 Quick Setup

### 1. Generate Secure Environment Configuration
```bash
# For Development
python scripts/setup_secrets.py development

# For Production
python scripts/setup_secrets.py production
```

### 2. Add Your API Keys
Edit the generated `.env` file and add your actual credentials:
- OpenAI API Key: Get from https://platform.openai.com/api-keys
- Database credentials
- Email configuration (optional)
- Other service credentials

### 3. Set Secure File Permissions
```bash
chmod 600 .env  # Read/write for owner only
```

## 📋 Environment File Types

| File | Purpose | Safe to Commit? |
|------|---------|-----------------|
| `.env.template` | Production template with security instructions | ✅ Yes |
| `.env.example` | Development example with safe defaults | ✅ Yes |
| `.env` | **Actual secrets** - NEVER commit | ❌ **NEVER** |

## 🔧 Configuration Options

### Required Variables
- `SECRET_KEY`: 32+ character random string for JWT signing
- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API key for AI features

### Optional Variables
- `REDIS_URL`: Redis connection for caching
- `SMTP_*`: Email configuration for notifications
- `KDP_*`: Amazon KDP integration
- `GOOGLE_*`/`GITHUB_*`: OAuth2 providers
- `SENTRY_DSN`: Error tracking

## 🛡️ Security Best Practices

### ✅ What We've Implemented
1. **Secure Secret Generation**: Cryptographically secure random keys
2. **Environment Variables**: All credentials externalized
3. **File Permissions**: Secure .env file permissions (600)
4. **Git Protection**: Comprehensive .gitignore to prevent commits
5. **Validation**: Warning system for placeholder values
6. **Production Hardening**: Separate production templates

### 🔒 Security Features
- **JWT Authentication**: Secure token-based auth with configurable expiration
- **Password Hashing**: bcrypt with salt and proper length validation
- **API Key Validation**: Format checking for OpenAI API keys
- **CORS Protection**: Configurable origin whitelisting
- **SSL/TLS Support**: HTTPS with secure certificate handling

## 🚨 PRODUCTION DEPLOYMENT CHECKLIST

### Before Going Live:
- [ ] Run `python scripts/setup_secrets.py production`
- [ ] Replace ALL placeholder values in `.env`
- [ ] Generate real OpenAI API key from https://platform.openai.com/api-keys
- [ ] Set up secure database credentials
- [ ] Configure actual domain names in `CORS_ORIGINS` and `ALLOWED_HOSTS`
- [ ] Set up SSL certificates and update paths
- [ ] Set file permissions: `chmod 600 .env`
- [ ] Verify `.env` is NOT committed to git

### Security Verification:
```bash
# Check for placeholder values
python -c "
import os
with open('.env', 'r') as f:
    content = f.read()
    issues = []
    if 'CHANGE_ME' in content: issues.append('CHANGE_ME placeholder')
    if 'example-' in content: issues.append('example credentials')
    if 'GENERATE_SECURE' in content: issues.append('un-generated secrets')
    if issues:
        print('❌ Security Issues:', issues)
    else:
        print('✅ No obvious security issues')
"
```

## 🔍 Security Validation

### Automatic Checks
The application automatically validates:
- Secret key length and format
- Database connection strings
- API key formats (OpenAI keys must start with 'sk-')
- SSL certificate existence

### Manual Verification
```bash
# Run the validation script
python scripts/setup_secrets.py

# Check environment permissions
ls -la .env  # Should show -rw-------

# Verify git ignore is working
git status  # .env should NOT appear
```

## 🔄 Environment Management

### Development
```bash
# Copy development example
cp .env.example .env
# Edit with your development values
```

### Production
```bash
# Use production template
cp .env.template .env
# Generate secure secrets
python scripts/setup_secrets.py production
# Edit with production values
```

### Docker/Containers
```bash
# Use environment variables or Docker secrets
docker run -e SECRET_KEY="your-secure-key" -e OPENAI_API_KEY="your-key" ...
```

## 🚨 Emergency Procedures

### If Secrets Are Exposed
1. **Immediate**: Regenerate ALL secrets and API keys
2. **Update**: Replace all values in `.env`
3. **Restart**: Restart all application services
4. **Monitor**: Monitor for unusual activity
5. **Audit**: Review access logs

### Regenerating Secrets
```bash
# Generate new secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update your .env with the new value
# Restart the application
```

## 🛠️ Troubleshooting

### Common Issues
1. **"SECRET_KEY is too short"**: Use `python scripts/setup_secrets.py`
2. **"OpenAI API key format invalid"**: Keys must start with 'sk-'
3. **"Database connection failed"**: Check DATABASE_URL format
4. **"SSL certificate not found"**: Update SSL_CERT_PATH and SSL_KEY_PATH

### Debug Mode
For development, you can enable debug mode:
```bash
# Add to .env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📞 Support

For security issues or questions:
1. Check this document first
2. Review the validation messages
3. Ensure all placeholders are replaced
4. Verify file permissions are set correctly

---

**Remember**: Never commit `.env` files to version control! Use the provided templates and scripts to manage secrets securely.