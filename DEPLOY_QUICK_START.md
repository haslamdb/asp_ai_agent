# Quick Start: Deploy to AWS Elastic Beanstalk

**Complete Guide:** See `AWS_DEPLOYMENT_GUIDE.md` for detailed instructions.

---

## Prerequisites (5 minutes)

```bash
# Install AWS CLI tools
pip install awsebcli awscli --upgrade

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret Key, region (us-east-1), format (json)

# Verify
eb --version
```

---

## Deploy in 5 Steps (15-20 minutes)

### 1. Initialize Elastic Beanstalk

```bash
cd /home/david/projects/asp_ai_agent

eb init
# Select:
#   Region: us-east-1 (or your preference)
#   Application name: asp-ai-agent
#   Platform: Python 3.12
#   CodeCommit: No
#   SSH: Yes
```

### 2. Create Production Environment

```bash
eb create asp-ai-agent-prod \
  --instance-type t3.small \
  --envvars FLASK_ENV=production
```

**This takes ~10-15 minutes.** AWS is creating:
- EC2 instance (t3.small)
- Load balancer
- EFS storage
- Security groups
- Health checks

### 3. Set API Keys (CRITICAL)

```bash
eb setenv \
  ANTHROPIC_API_KEY=your-actual-claude-api-key-here \
  GEMINI_API_KEY=your-actual-gemini-api-key-here \
  FLASK_ENV=production

# Verify
eb printenv
```

### 4. Deploy Application

```bash
eb deploy

# Check status
eb status

# View health
eb health
```

### 5. Test Your Deployment

```bash
# Get your URL
eb status | grep CNAME

# Open in browser
eb open

# Test health endpoint
curl http://your-app-url.elasticbeanstalk.com/health
```

**Expected response:**
```json
{"status": "healthy"}
```

---

## What Happens on First Deploy

1. **Package Upload** (~30 seconds)
   - Uploads your code to S3

2. **Environment Setup** (~5 minutes)
   - Creates EC2 instance
   - Installs Python 3.12
   - Installs system packages (gcc, git, etc.)

3. **Python Dependencies** (~3-5 minutes)
   - Installs all packages from requirements.txt
   - Downloads sentence-transformers model (~1GB)
   - ⚠️ This is the longest step

4. **Storage Setup** (~2 minutes)
   - Creates EFS file system
   - Mounts at /mnt/efs
   - Creates data directories

5. **Application Start** (~1 minute)
   - Initializes RAG systems
   - Loads embedding models
   - Starts Flask server

**Total first deploy: 10-15 minutes**

**Subsequent deploys: 3-5 minutes** (models already cached)

---

## Verify Everything Works

### Test Endpoints

```bash
# Get your app URL
URL=$(eb status | grep CNAME | awk '{print $3}')

# Test health
curl http://$URL/health

# Test ASP feedback (replace with your API keys)
curl -X POST http://$URL/api/asp-feedback \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "A 3-year-old with fever and cough",
    "user_response": "Start broad-spectrum antibiotics",
    "difficulty": "intermediate"
  }'

# Test CICU scenarios
curl http://$URL/api/modules/cicu/scenario
```

### Check Logs

```bash
# View recent logs
eb logs

# Real-time log streaming
eb logs --stream
```

### Check Data Persistence

```bash
# SSH into instance
eb ssh

# Check EFS mount
df -h | grep efs
# Should show: /mnt/efs mounted

# Check data directory
ls -la /var/app/current/data
# Should show: asp_sessions.db, expert_embeddings/, literature_embeddings/

# Exit SSH
exit
```

---

## Common First-Deploy Issues

### Issue: "Environment creation failed"

**Check:** EC2 service limits
```bash
# Verify you can create EC2 instances in your region
aws ec2 describe-account-attributes --region us-east-1
```

**Fix:** Request limit increase in AWS Console

---

### Issue: "Application not responding"

**Check logs:**
```bash
eb logs | grep ERROR
```

**Common causes:**
1. Missing API keys → Set with `eb setenv`
2. Model download timeout → Wait longer, check logs for "Downloading"
3. Port conflict → Check `.ebextensions/01_packages.config`

---

### Issue: "502 Bad Gateway"

**Cause:** App failed to start

**Debug:**
```bash
# SSH into instance
eb ssh

# Check app logs
sudo tail -100 /var/log/web.stdout.log

# Check for Python errors
sudo tail -100 /var/log/eb-engine.log
```

---

## Post-Deployment Setup

### Configure HTTPS (Recommended)

1. Request SSL certificate in AWS Certificate Manager
2. Add certificate ARN to `.ebextensions/01_packages.config`:
   ```yaml
   aws:elbv2:listener:443:
     Protocol: HTTPS
     SSLCertificateArns: arn:aws:acm:REGION:ACCOUNT:certificate/ID
   ```
3. Deploy: `eb deploy`

### Set Up Custom Domain

1. Go to Route 53 → Create hosted zone
2. Create A record → Alias to Elastic Beanstalk
3. Update domain registrar nameservers

### Enable Cost Alerts

1. AWS Console → Billing → Budgets
2. Create budget: $50/month
3. Alert at 80% and 100%

### Enable Monitoring

Already configured! View in CloudWatch:
- Application requests
- Response times
- Error rates
- CPU/memory usage

---

## Daily Operations

### Deploy Updates

```bash
# Make code changes
git add .
git commit -m "Update: description"

# Deploy
eb deploy

# Verify
eb health
```

### View Logs

```bash
eb logs --stream
```

### Update Environment Variables

```bash
eb setenv NEW_VAR=value
```

### Scale Up/Down

```bash
# Add more instances
eb scale 2

# Change instance size (edit .ebextensions/01_packages.config)
# Then: eb deploy
```

---

## Costs

**Expected monthly cost:** ~$35-40

| Service | Cost |
|---------|------|
| EC2 t3.small | $15 |
| Load Balancer | $16 |
| EFS (1-5GB) | $0.30-1.50 |
| Data Transfer | $1-5 |
| CloudWatch | $3 |

**First 12 months with Free Tier:** ~$20-25/month

---

## Next Steps

1. ✅ Deploy to production
2. ✅ Test with 5-10 users
3. ✅ Monitor costs and performance
4. ✅ Collect expert feedback
5. ✅ Import expert knowledge
6. ✅ Expand to regional partners
7. ✅ National launch

---

## Need Help?

- **Detailed Guide:** `AWS_DEPLOYMENT_GUIDE.md`
- **AWS Docs:** https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html
- **AWS Support:** https://console.aws.amazon.com/support/home
- **Your IT Department:** They likely have AWS expertise!

---

## Emergency Commands

```bash
# Restart app
eb restart

# Terminate environment (WARNING: deletes everything!)
eb terminate asp-ai-agent-prod

# Restore from snapshot
# (Only if you configured EFS backups)
```

---

**You're ready to deploy! 🚀**

Questions? See the full guide in `AWS_DEPLOYMENT_GUIDE.md`
