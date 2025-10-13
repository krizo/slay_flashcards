# Secrets Management for SlayFlashcards

This document describes how to configure secrets for different environments (staging, production).

## Overview

Secrets are managed using GitHub Secrets for CI/CD deployments. This ensures sensitive information like passwords and database credentials are never committed to the repository.

## Secrets Format

Secrets are stored as JSON in GitHub Secrets. See `secrets.example.json` for the complete format.

### Demo Users Configuration

```json
{
  "demo_users": [
    {
      "username": "Emila",
      "email": "emila@demo.pl",
      "password": "SecurePassword123!",
      "full_name": "Emila Kowalska"
    },
    {
      "username": "Kriz",
      "email": "kriz@demo.pl",
      "password": "SecurePassword456!",
      "full_name": "Kriz Nowak"
    }
  ]
}
```

### Database Configuration (Future)

```json
{
  "database": {
    "url": "postgresql://user:password@host:port/dbname"
  }
}
```

### JWT Configuration (Future)

```json
{
  "jwt": {
    "secret_key": "your-secret-key-here-min-32-chars",
    "algorithm": "HS256",
    "access_token_expire_minutes": 60
  }
}
```

## GitHub Secrets Setup

### Required Secrets

1. **STAGING_SECRETS** - JSON string containing secrets for staging environment
2. **PRODUCTION_SECRETS** - JSON string containing secrets for production environment

### How to Add Secrets to GitHub

1. Go to your repository on GitHub
2. Navigate to: Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret:

#### For Staging:
- **Name**: `STAGING_SECRETS`
- **Value**: Copy the entire JSON from your configured `secrets.staging.json` file

#### For Production:
- **Name**: `PRODUCTION_SECRETS`
- **Value**: Copy the entire JSON from your configured `secrets.production.json` file

### Creating Your Secrets Files

1. **Copy the example file**:
   ```bash
   cp deployment/secrets.example.json deployment/secrets.staging.json
   cp deployment/secrets.example.json deployment/secrets.production.json
   ```

2. **Edit each file** and replace all `CHANGE_ME_` values with real credentials:
   - Use strong, unique passwords (min 8 chars, uppercase, lowercase, digit, special char)
   - Use valid email addresses
   - Generate a secure JWT secret key (32+ random characters)

3. **Add to GitHub Secrets** (as described above)

4. **Delete local files** (IMPORTANT - don't commit them!):
   ```bash
   rm deployment/secrets.staging.json
   rm deployment/secrets.production.json
   ```

## Security Best Practices

1. **Never commit actual secrets** to the repository
2. **Use different passwords** for staging and production
3. **Rotate secrets regularly** (update GitHub Secrets)
4. **Use strong passwords**:
   - Minimum 8 characters
   - Include uppercase and lowercase letters
   - Include at least one digit
   - Include at least one special character
5. **Limit access** to GitHub Secrets (only give access to trusted team members)

## Local Development

For local development, create a `.env` file in the project root:

```bash
# .env (this file is gitignored)
DEMO_SECRETS='{"demo_users":[{"username":"testuser","email":"test@local.dev","password":"Test123!","full_name":"Test User"}]}'
```

The `.env` file is already in `.gitignore`, so it won't be committed.

## Usage in CI/CD

The CI/CD workflow automatically:
1. Reads the appropriate secret (STAGING_SECRETS or PRODUCTION_SECRETS)
2. Passes it to the database initialization script
3. Creates demo users with the configured credentials

## Troubleshooting

### Demo data not being created
- Check that the secret name matches: `STAGING_SECRETS` or `PRODUCTION_SECRETS`
- Verify the JSON format is valid (use a JSON validator)
- Check GitHub Actions logs for error messages

### Invalid password errors
- Ensure passwords meet requirements: 8+ chars, uppercase, lowercase, digit, special char
- Check for special characters that might need escaping in JSON (use `\"` for quotes)

### Database connection errors (future)
- Verify the database URL format
- Ensure the database server is accessible from the deployment environment
- Check firewall rules and network connectivity
