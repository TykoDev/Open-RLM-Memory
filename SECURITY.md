# Security Policy

## Supported Versions

Only the latest version of Open RLM Memory currently receives security updates.

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

### How to Report

**Email**: contact@tykotech.eu

Please do not create a public GitHub issue for security vulnerabilities.

### What to Include

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact if exploited
- **Steps to Reproduce**: Detailed steps or proof of concept
- **Affected Versions**: Which versions are affected
- **Proposed Fix**: If you have a suggested fix (optional)
- **Additional Context**: Any relevant information (configurations, environment, etc.)

### What NOT to Include

- Exploit code or scripts
- Detailed reverse engineering
- Sensitive information about the vulnerability

## Disclosure Process

Once we receive a report:

1. **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
2. **Investigation**: We will investigate and validate the vulnerability
3. **Resolution**: We will work on a fix
4. **Timeline**: We will provide an estimated timeline for the fix
5. **Disclosure**: We will coordinate with you on public disclosure timing

### Response Timeline

- **Critical**: Within 48 hours of acknowledgement, fix within 7 days
- **High**: Within 72 hours of acknowledgement, fix within 14 days
- **Medium**: Within 5 days of acknowledgement, fix within 30 days
- **Low**: Within 7 days of acknowledgement, fix within 60 days

### Public Disclosure

We will coordinate with you on the timing of public disclosure. Generally:

- Wait until a fix is available to all users
- Allow 7 days after fix release for users to update
- Coordinate on security advisories or blog posts

## Security Best Practices for Users

### Protect Your API Keys

- Never commit API keys to version control
- Rotate API keys regularly
- Use different keys for different environments
- Monitor API usage for unusual activity

### Secure Your Deployment

- Use HTTPS in production
- Keep dependencies updated
- Use strong passwords for your database
- Monitor logs for suspicious activity

### Data Privacy

- Only store necessary information
- Understand what data is stored (memories, embeddings, metadata)
- Use data export feature to understand your data footprint
- Delete old memories regularly

## Common Security Issues

### Phishing Attempts

Be aware of phishing attempts:
- Verify email senders before clicking links
- Never share your API keys via email
- Only use official channels for support

### Exposed Secrets

If you accidentally commit secrets:
1. Rotate the compromised credentials immediately
2. Update environment variables
3. Revoke old API keys
4. Consider rotating other related credentials

## Security Updates

We will publish security advisories for:

- Critical vulnerabilities
- High-severity vulnerabilities
- Changes that affect default configurations

Advisories will include:
- Vulnerability description and impact
- Affected versions
- Upgrade recommendations
- CVE numbers (if assigned)

## Acknowledgements

We thank security researchers who responsibly disclose vulnerabilities. We will credit researchers who report vulnerabilities that we fix, subject to their preference.

## Questions?

If you have questions about this security policy:

**Email**: contact@tykotech.eu

Thank you for helping keep Open RLM Memory secure!
