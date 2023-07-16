# HSH Grade checker
Periodically fetches HSH iCMS for new grades and sends an email if a new grade was found.

### Configuration

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

### Docker Usage

```bash
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

### Kubernetes Usage

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: "hsh-grade-checker-secret"
  namespace: "default"
type: Opaque
data:
  ICMS_USERNAME: "..."
  ICMS_PASSWORD: "..."
  SMTP_SERVER: "..."
  SMTP_PORT: "..."
  SMTP_FROM: "..."
  SMTP_TO: "..."
  SMTP_USERNAME: "..."
  SMTP_PASSWORD: "..."
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: "hsh-grade-checker"
  name: "hsh-grade-checker"
  namespace: "default"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: "hsh-grade-checker"
  template:
    metadata:
      labels:
        app: "hsh-grade-checker"
    spec:
      containers:
      - image: "ghcr.io/luca-heitmann/hsh-grade-checker:latest"
        name: "hsh-grade-checker"
        envFrom:
        - secretRef:
            name: "hsh-grade-checker-secret"
```
