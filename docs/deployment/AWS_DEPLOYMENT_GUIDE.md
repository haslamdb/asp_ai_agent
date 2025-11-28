# AWS Elastic Beanstalk Deployment Guide
## ASP AI Agent - Production Deployment for National Access

---

## 📋 Prerequisites

### 1. AWS Account
- ✅ You already have an AWS account
- Ensure you have access to the AWS Console
- Verify billing is enabled

### 2. Install AWS EB CLI

```bash
# Install AWS Elastic Beanstalk CLI
pip install awsebcli --upgrade

# Verify installation
eb --version
```

### 3. Configure AWS Credentials

```bash
# Install AWS CLI if not already installed
pip install awscli --upgrade

# Configure with your AWS credentials
aws configure
# Enter:
#   AWS Access Key ID: [your-access-key]
#   AWS Secret Access Key: [your-secret-key]
#   Default region: us-east-1  (or your preferred region)
#   Default output format: json
```

### 4. Prepare Environment Variables

You'll need to set these as Elastic Beanstalk environment variables:

```bash
ANTHROPIC_API_KEY=your-claude-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
FLASK_ENV=production
```

---

## 🚀 Step-by-Step Deployment

### Step 1: Initialize Elastic Beanstalk

From your project directory (`/home/david/projects/asp_ai_agent`):

```bash
# Initialize EB application
eb init

# When prompted:
# 1. Select region: us-east-1 (or your preferred region)
# 2. Create new application: asp-ai-agent
# 3. Platform: Python
# 4. Platform version: Python 3.12
# 5. CodeCommit: No
# 6. SSH: Yes (recommended for troubleshooting)
```

### Step 2: Create Environment

```bash
# Create production environment
eb create asp-ai-agent-prod \
  --instance-type t3.small \
  --envvars FLASK_ENV=production

# This will:
# - Create a load balancer
# - Launch EC2 instance (t3.small)
# - Set up security groups
# - Deploy your application
# - Takes ~10-15 minutes
```

### Step 3: Set Environment Variables

```bash
# Set API keys (CRITICAL - app won't work without these)
eb setenv \
  ANTHROPIC_API_KEY=your-actual-claude-api-key \
  GEMINI_API_KEY=your-actual-gemini-api-key \
  FLASK_ENV=production

# Verify environment variables were set
eb printenv
```

### Step 4: Configure Persistent Storage (EFS)

The `.ebextensions/03_storage.config` file will automatically create EFS storage.

**Verify EFS was created:**

1. Go to AWS Console → EFS
2. Look for file system named `asp-ai-agent-storage`
3. Verify it's in "Available" state

**The EFS will be automatically mounted at `/mnt/efs` and symlinked to `/var/app/current/data`**

### Step 5: Deploy Application

```bash
# Deploy current code
eb deploy

# Monitor deployment
eb status

# Check health
eb health --refresh
```

### Step 6: View Logs

```bash
# View recent logs
eb logs

# Tail logs in real-time
eb logs --stream
```

### Step 7: Open Your Application

```bash
# Open in browser
eb open

# Get the URL
eb status | grep "CNAME"
```

Your application will be available at:
`http://asp-ai-agent-prod.us-east-1.elasticbeanstalk.com`

---

## 🔒 Configure HTTPS (Recommended for Production)

### Option 1: Using AWS Certificate Manager (ACM) - FREE

**Step 1: Request SSL Certificate**

1. Go to AWS Console → Certificate Manager
2. Click "Request a certificate"
3. Choose "Request a public certificate"
4. Enter domain name (e.g., `aspfellows.org` or `www.aspfellows.org`)
5. Validation method: DNS validation (recommended)
6. Add DNS records as instructed (in your domain registrar)
7. Wait for validation (~5-30 minutes)

**Step 2: Add Certificate to Load Balancer**

Edit `.ebextensions/01_packages.config` and add your certificate ARN:

```yaml
option_settings:
  # ... existing settings ...

  aws:elbv2:listener:443:
    Protocol: HTTPS
    SSLCertificateArns: arn:aws:acm:us-east-1:YOUR-ACCOUNT-ID:certificate/CERTIFICATE-ID
```

Then deploy:

```bash
eb deploy
```

### Option 2: Use Elastic Beanstalk Domain

The default `.elasticbeanstalk.com` domain doesn't support HTTPS by default, but you can:

1. Use CloudFront in front of Elastic Beanstalk
2. Configure HTTPS on CloudFront with ACM certificate
3. Point your domain to CloudFront

---

## 🎯 Custom Domain Setup

### Step 1: Configure Route 53 (AWS DNS)

1. Go to AWS Console → Route 53
2. Create hosted zone for your domain (e.g., `aspfellows.org`)
3. Create A record:
   - Type: A - IPv4 address
   - Alias: Yes
   - Alias Target: Your Elastic Beanstalk environment
   - Routing Policy: Simple

### Step 2: Update Domain Registrar

Update your domain registrar (GoDaddy, Namecheap, etc.) to use Route 53 nameservers:

```
ns-123.awsdns-12.com
ns-456.awsdns-45.net
ns-789.awsdns-78.org
ns-012.awsdns-01.co.uk
```

(Get actual nameservers from Route 53 hosted zone)

### Step 3: Verify

```bash
# Check DNS propagation (may take 24-48 hours)
dig aspfellows.org

# Or use online tool:
# https://www.whatsmydns.net
```

---

## 📊 Monitoring and Health Checks

### Built-in Health Endpoint

Your app has a health check at `/health`:

```bash
# Test health endpoint
curl http://your-app.elasticbeanstalk.com/health
```

### CloudWatch Monitoring

Elastic Beanstalk automatically sends metrics to CloudWatch:

1. Go to AWS Console → CloudWatch
2. Navigate to "All alarms"
3. View metrics:
   - CPU utilization
   - Network traffic
   - Request latency
   - HTTP response codes

### Set Up Alarms

**Create alarm for high error rate:**

1. CloudWatch → Alarms → Create alarm
2. Metric: ApplicationELB → UnhealthyHostCount
3. Threshold: > 0 for 2 consecutive periods
4. Actions: Send SNS notification to your email

---

## 💰 Cost Monitoring

### Set Billing Alerts

**Recommended: Set budget alert at $50/month**

1. AWS Console → Billing → Budgets
2. Create budget:
   - Budget type: Cost budget
   - Period: Monthly
   - Budgeted amount: $50
   - Alerts: 80% and 100%
   - Email: your-email@institution.edu

### Expected Monthly Costs

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **EC2** | t3.small (1 instance) | ~$15 |
| **EFS** | 1-5 GB storage | ~$0.30-1.50 |
| **Load Balancer** | Application Load Balancer | ~$16 |
| **Data Transfer** | 10 GB/month | ~$1 |
| **CloudWatch** | Basic monitoring | ~$3 |
| **Route 53** | Hosted zone + queries | ~$1 |
| **Total** | **Base production cost** | **~$35-40/month** |

**With AWS Free Tier (first 12 months):**
- 750 hours EC2 t2.micro - FREE (you're using t3.small, so ~$15)
- 5 GB EFS - FREE
- Total first year: ~$20-25/month

---

## 🔧 Maintenance and Updates

### Deploy New Code

```bash
# From your project directory
git add .
git commit -m "Update: description"
eb deploy
```

### Update Environment Variables

```bash
# Update API keys or other settings
eb setenv NEW_VAR=value

# View current environment variables
eb printenv
```

### Scale Up/Down

```bash
# Increase instance size (if needed for more users)
eb scale 2  # Run 2 instances (auto-scaling)

# Or change instance type
# Edit .ebextensions/01_packages.config
# Change InstanceType: t3.medium
# Then: eb deploy
```

### Backup Data

Your data is on EFS, which is persistent. To back up:

1. Go to AWS Console → EFS
2. Select your file system
3. Actions → Create backup
4. Or set up automatic daily backups

### View Application Logs

```bash
# Last 100 lines
eb logs

# Continuous tail
eb logs --stream

# Download full logs
eb logs --all
```

---

## 🐛 Troubleshooting

### Issue: App Won't Start

**Check logs:**
```bash
eb logs --stream
```

**Common causes:**
- Missing environment variables (ANTHROPIC_API_KEY, GEMINI_API_KEY)
- Python package installation failed
- Database initialization error

**Solution:**
```bash
# Verify environment variables
eb printenv

# SSH into instance to debug
eb ssh
cd /var/app/current
cat /var/log/eb-engine.log
```

### Issue: Model Downloads Failing

**Cause:** Sentence-transformers models (~1GB) take time to download on first boot

**Solution:**
1. The first deployment may take 5-10 minutes to download models
2. Subsequent deployments will be faster (models cached in /root/.cache)
3. Check logs: `eb logs` - look for "Downloading model" messages

### Issue: Database Not Persisting

**Check EFS mount:**
```bash
eb ssh
df -h | grep efs
ls -la /var/app/current/data
```

**Should show:**
```
/mnt/efs                 8.0E     0  8.0E   0% /mnt/efs
lrwxrwxrwx 1 root root 14 Dec 10 12:00 /var/app/current/data -> /mnt/efs/data
```

**Fix if needed:**
```bash
sudo mkdir -p /mnt/efs/data
sudo chmod 777 /mnt/efs/data
sudo ln -sf /mnt/efs/data /var/app/current/data
```

### Issue: High Costs

**Check what's consuming resources:**
1. AWS Console → Cost Explorer
2. View costs by service
3. Common culprits:
   - Data transfer (high traffic)
   - EFS storage (if very large)
   - Multiple instances running

**Reduce costs:**
```bash
# Use smaller instance
# Edit .ebextensions/01_packages.config: InstanceType: t3.micro
eb deploy

# Scale down to single instance
eb scale 1
```

### Issue: Slow Response Times

**Causes:**
- Cold start (first request after idle)
- Model inference time
- Many concurrent users

**Solutions:**
1. Use larger instance (t3.medium instead of t3.small)
2. Enable CloudFront CDN for static assets
3. Consider caching frequent queries
4. Scale to multiple instances: `eb scale 2`

---

## 🔐 Security Best Practices

### 1. Enable HTTPS (Required for Production)

See "Configure HTTPS" section above

### 2. Restrict Access (If Needed)

If you want to limit access to specific institutions:

**Edit `.ebextensions/01_packages.config`:**

```yaml
option_settings:
  # Add IP restrictions
  aws:elbv2:listener:default:
    Rules: |
      [
        {
          "Priority": 1,
          "Actions": [{"Type": "fixed-response", "FixedResponseConfig": {"StatusCode": "403"}}],
          "Conditions": [{"Field": "source-ip", "Values": ["0.0.0.0/0"]}]
        }
      ]
```

### 3. Enable Access Logs

**Edit `.ebextensions/01_packages.config`:**

```yaml
option_settings:
  aws:elbv2:loadbalancer:
    AccessLogsS3Enabled: true
    AccessLogsS3Bucket: asp-ai-agent-logs
```

### 4. Rotate API Keys Regularly

```bash
# Update API keys every 90 days
eb setenv ANTHROPIC_API_KEY=new-key GEMINI_API_KEY=new-key
```

### 5. HIPAA Compliance (If Needed)

If fellows will discuss real patient cases:

1. Sign AWS Business Associate Agreement (BAA)
   - Contact AWS sales: https://aws.amazon.com/compliance/hipaa-compliance/
2. Enable encryption at rest (already enabled in EFS)
3. Enable access logging (see above)
4. Add audit trail for user actions
5. Regular security reviews

---

## 📞 Support and Help

### AWS Support Plans

- **Basic (Free):** 24/7 access to documentation, forums
- **Developer ($29/mo):** Business hours email support, <24hr response
- **Business ($100/mo):** 24/7 phone/chat support, <1hr response for critical issues

**Recommendation:** Start with free tier, upgrade to Developer if you need support

### Useful AWS Documentation

- Elastic Beanstalk Python: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html
- EFS Setup: https://docs.aws.amazon.com/efs/latest/ug/getting-started.html
- HTTPS Configuration: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https.html

### Getting Help

1. **AWS Forums:** https://forums.aws.amazon.com/
2. **Stack Overflow:** Tag with `aws-elastic-beanstalk`
3. **Your Institution's IT Department** - They likely have AWS expertise

---

## ✅ Post-Deployment Checklist

After deploying, verify:

- [ ] Application is accessible at public URL
- [ ] Health endpoint returns `{"status": "healthy"}`: `/health`
- [ ] API endpoints work:
  - [ ] POST `/api/asp-feedback` - Returns AI feedback
  - [ ] POST `/api/feedback/enhanced` - Returns enhanced feedback
  - [ ] GET `/api/modules/cicu/scenario` - Returns CICU scenarios
- [ ] Databases are persisting (create session, restart app, verify session exists)
- [ ] Logs are accessible: `eb logs`
- [ ] CloudWatch metrics are being recorded
- [ ] Billing alerts are configured
- [ ] HTTPS is enabled (if using custom domain)
- [ ] Custom domain works (if configured)

---

## 🎓 Next Steps for National Rollout

### Phase 1: Pilot Testing (Week 1-2)

1. Deploy to production
2. Test with 5-10 fellows from your institution
3. Collect initial feedback
4. Monitor costs and performance

### Phase 2: Expert Review Collection (Week 3-6)

1. Send Google Form to ASP experts
2. Collect 20-50 expert corrections
3. Import using `add_expert_knowledge.py`
4. Test enhanced feedback quality

### Phase 3: Regional Expansion (Month 2-3)

1. Invite 2-3 partner institutions
2. Monitor scaling (add instances if needed)
3. Collect usage metrics
4. Refine based on multi-site feedback

### Phase 4: National Launch (Month 4+)

1. Announce to all pediatric ID fellowship programs
2. Set up usage tracking
3. Prepare for publications/presentations
4. Consider scaling to t3.medium or multiple instances

---

## 📊 Monitoring Success Metrics

Track these metrics monthly:

### Usage Metrics
- Number of active users (fellows)
- Number of sessions created
- Number of feedback requests
- Most popular modules
- Average session duration

### Performance Metrics
- Average response time
- Error rate
- Uptime percentage
- User satisfaction (via surveys)

### Cost Metrics
- Monthly AWS spend
- Cost per user
- Cost per interaction

### Quality Metrics
- Expert review feedback scores
- User-reported issues
- Feedback improvement (with vs without expert RAG)

---

## 🚨 Emergency Procedures

### App is Down

```bash
# Check status
eb health

# View logs
eb logs --stream

# Restart app
eb restart

# If that fails, redeploy
eb deploy
```

### High Costs Alert

1. Check Cost Explorer in AWS Console
2. Identify expensive service
3. Scale down if needed: `eb scale 1`
4. Check for data transfer spikes
5. Contact AWS support if unexpected charges

### Data Loss

1. Check EFS console for file system status
2. Restore from EFS backup (if configured)
3. If no backup, data may be lost (why backups are critical!)

---

## 📝 Deployment Commands Quick Reference

```bash
# Initial setup
eb init                          # Initialize EB application
eb create asp-ai-agent-prod      # Create environment
eb setenv KEY=value              # Set environment variables

# Regular deployment
eb deploy                        # Deploy current code
eb status                        # Check environment status
eb health                        # Check application health

# Monitoring
eb logs                          # View recent logs
eb logs --stream                 # Tail logs in real-time
eb printenv                      # View environment variables

# Scaling
eb scale 2                       # Scale to 2 instances
eb restart                       # Restart application

# Cleanup
eb terminate asp-ai-agent-prod   # Terminate environment (WARNING: deletes everything!)
```

---

## 🎉 You're Ready!

Your ASP AI Agent is now ready for national deployment on AWS Elastic Beanstalk!

**Key Features:**
- ✅ Professional, scalable infrastructure
- ✅ 99.99% uptime SLA
- ✅ Persistent data storage (EFS)
- ✅ Auto-scaling capabilities
- ✅ HIPAA-compliant infrastructure (if BAA signed)
- ✅ Monitoring and logging
- ✅ Cost-effective (~$35-40/month)

**Questions?** Review the troubleshooting section or contact AWS support.

**Good luck with your national ASP fellowship curriculum!** 🎓🏥
