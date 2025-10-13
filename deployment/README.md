# Deployment Configuration

This directory contains deployment configuration files and documentation for SlayFlashcards.

## Files

- **`secrets.example.json`** - Example template showing the secrets format (safe to commit)
- **`SECRETS_SETUP.md`** - Comprehensive guide for setting up GitHub Secrets
- **`slayflashcards-backend-staging.service`** - systemd service for staging backend
- **`slayflashcards-backend-production.service`** - systemd service for production backend
- **`slayflashcards-frontend-staging.service`** - systemd service for staging frontend
- **`slayflashcards-frontend-production.service`** - systemd service for production frontend

## Quick Start

### 1. Configure Secrets for GitHub Actions

Follow the instructions in [`SECRETS_SETUP.md`](./SECRETS_SETUP.md) to:
1. Create your `secrets.staging.json` and `secrets.production.json` files
2. Add them as GitHub Secrets (`STAGING_SECRETS` and `PRODUCTION_SECRETS`)
3. Never commit the actual secrets files

### 2. Secrets Format

See `secrets.example.json` for the complete format. Currently used fields:

```json
{
  "demo_users": [
    {
      "username": "YourUsername",
      "email": "user@example.com",
      "password": "SecurePassword123!",
      "full_name": "Full Name"
    }
  ]
}
```

### 3. How Secrets Are Used

**In CI/CD Pipeline:**
1. GitHub Actions reads `STAGING_SECRETS` or `PRODUCTION_SECRETS` based on environment
2. Sets `DEMO_SECRETS` environment variable in the deployment step
3. Database initialization script reads `DEMO_SECRETS` and creates demo users

**Local Development:**
- Set `DEMO_SECRETS` environment variable before running scripts
- Or let it use default fallback credentials (hardcoded in `scripts/create_demo_data.py`)

### 4. Security Notes

- **Never commit actual secrets** - only `secrets.example.json` should be in git
- Use strong passwords (8+ chars, mixed case, digits, special characters)
- Different passwords for staging and production
- Rotate credentials regularly
- `.gitignore` is configured to block `secrets.*.json` files

## Future Enhancements

The secrets format supports additional fields for future use:

- **Database credentials** - for PostgreSQL or other database connections
- **JWT configuration** - for authentication token signing
- **API keys** - for third-party services
- **Email configuration** - for sending notifications

These can be added to the JSON structure without breaking existing functionality.

## Troubleshooting

### Demo users not created
- Check GitHub Actions logs for error messages
- Verify secret name is exactly `STAGING_SECRETS` or `PRODUCTION_SECRETS`
- Validate JSON format (use [jsonlint.com](https://jsonlint.com/))

### Password validation errors
- Ensure passwords meet requirements: 8+ chars, uppercase, lowercase, digit, special char
- Avoid special characters that need escaping in JSON (or escape them properly)

### Environment variable not passed
- Ensure the `env:` section is present in the deployment step
- Check that `DEMO_SECRETS` is passed to the `sudo` command

For more details, see [`SECRETS_SETUP.md`](./SECRETS_SETUP.md).
