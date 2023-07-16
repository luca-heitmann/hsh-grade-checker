# HSH Grade checker
Periodically fetches HSH iCMS for new grades and sends an email if a new grade was found.

Environment variables (* required):
- ICMS_USERNAME*: String
- ICMS_PASSWORD*: String
- SMTP_SERVER*: String
- SMTP_PORT*: Int (requires starttls)
- SMTP_FROM*: String
- SMTP_TO*: String
- SMTP_USERNAME*: String
- SMTP_PASSWORD*: String
- SMTP_DEBUG: Int (0 = off (default) / 1 = on)
- REFRESH_SECONDS: Int (300 default => fetches every 5 min)
- SIGN_OF_LIFE_AFTER_REFRESHES: Int (120 default => sign of life every 5min*120 = 600min = 10h)

Usage:

```
docker run -d \
    -e ICMS_USERNAME="xxx-xxx-u1" \
    -e ICMS_PASSWORD="xxx" \
    -e SMTP_SERVER="xxx" \
    -e SMTP_PORT="587" \
    -e SMTP_FROM="xxx@xxx.xx" \
    -e SMTP_TO="xxx@xxx.xx" \
    -e SMTP_USERNAME="xxx" \
    -e SMTP_PASSWORD="xxx" \
    ghcr.io/luca-heitmann/hsh-grade-checker:latest
```
