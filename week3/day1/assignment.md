# Week 3 Assignment: Auto Scaling Group with Application Load Balancer

## 🎯 Objectives
- Deploy Flask app using Auto Scaling Group (ASG)
- Configure Application Load Balancer (ALB)
- Set up automatic scaling based on CPU
- Implement HTTPS with SSL certificate via ALB

---

## 📚 Reference Code

**Repository:** https://github.com/devopswithakhilesh/Jan26-devops-bootcamp/tree/main/week3/day1

Clone this code and deploy using ASG + ALB.

---

## 📋 Prerequisites

- Week 1 VPC setup completed (`jan26-vpc`, public subnets)
- Week 2 assignment completed (understand Flask deployment)
- Domain from Week 2 (will use subdomain)
- Basic understanding of horizontal scaling

---

## 🔑 Key Concepts

### Horizontal vs Vertical Scaling
- **Horizontal:** Add more VMs of same size (ASG does this)
- **Vertical:** Increase VM size (CPU/RAM) - NOT auto scaling

### Components
```
Domain → Route 53 → ALB → Target Group → ASG → EC2 Instances
```

---

## 📝 PART 1: PREPARE APPLICATION CODE

### Step 1: Clone Reference Code

```bash
git clone https://github.com/devopswithakhilesh/Jan26-devops-bootcamp.git
cd Jan26-devops-bootcamp/week3/day1
```

### Step 2: Review User Data Script

Check `user-data.sh` - this runs automatically when EC2 launches:

```bash
#!/bin/bash
sleep 30  # Wait for system to initialize

# Log current directory
pwd > /home/ec2-user/install-logs.txt

# Install Git
sudo yum install git -y

# Clone repository
cd /home/ec2-user
git clone https://github.com/devopswithakhilesh/Jan26-devops-bootcamp.git

# Navigate to app directory
cd Jan26-devops-bootcamp/week3/day1/app

# Make script executable and run
chmod u+x run.sh
./run.sh
```

**Important:** No Nginx needed! ALB handles reverse proxy.

### Step 3: Push Your Version to GitHub

```bash
# Create your repo
git remote add origin https://github.com/YOUR_USERNAME/jan26-bootcamp.git
git add .
git commit -m "Week 3: ASG with ALB setup"
git push -u origin main
```

---

## 🖥️ PART 2: CREATE LAUNCH TEMPLATE

### Step 1: Go to EC2 → Launch Templates

1. Click **Create launch template**
2. Name: `jan26-week3-template`

### Step 2: Configure Template

**AMI:**
- Quick Start → Amazon Linux 2023 (latest)

**Instance type:**
- `t2.micro`

**Key pair:**
- Select `jan26-key` (from Week 1)

**Network settings:**
- Subnet: `public-jan26` (for now - in production use private)
- Availability Zone: `ap-south-1a`

**Security group:**
- Create new: `asg-app-sg`
- Inbound rules:
  - SSH (22) from 0.0.0.0/0
  - Custom TCP (8000) from 0.0.0.0/0

**Advanced details → User data:**

Paste the user data script (modify GitHub URL to YOUR repo):

```bash
#!/bin/bash
sleep 30
pwd > /home/ec2-user/install-logs.txt
sudo yum install git -y
cd /home/ec2-user
git clone https://github.com/YOUR_USERNAME/jan26-bootcamp.git
cd jan26-bootcamp/week3/day1/app
chmod u+x run.sh
./run.sh
```

### Step 3: Create Template

Click **Create launch template**

### Step 4: Test Launch Template

1. Go to Launch template → Actions → **Launch instance from template**
2. Use default settings
3. Launch

**Verify:**
```bash
ssh -i jan26-key.pem ec2-user@<PUBLIC_IP>

# Check logs
cat /home/ec2-user/install-logs.txt

# Check if app is running
curl http://localhost:8000
```

Test in browser: `http://<PUBLIC_IP>:8000`

If working, **terminate this test instance**.

---

## 🔄 PART 3: CREATE AUTO SCALING GROUP

### Step 1: Create Second Public Subnet

ALB needs minimum 2 subnets in different AZs.

1. VPC → Subnets → **Create subnet**
2. Name: `public-jan26-2`
3. VPC: `jan26-vpc`
4. AZ: `ap-south-1b` (different from first subnet!)
5. CIDR: `10.0.3.0/24`

**Associate with public route table:**
1. VPC → Route Tables → Select `public-rt-jan26`
2. Subnet Associations → Edit
3. Add `public-jan26-2`
4. Save

### Step 2: Create Auto Scaling Group

1. EC2 → Auto Scaling Groups → **Create**
2. Name: `jan26-week3-asg`
3. Launch template: `jan26-week3-template` (latest version)
4. Click **Next**

**Network:**
- VPC: `jan26-vpc`
- Subnets: Select `public-jan26` (the one matching your launch template AZ)

**Load balancing:**
- Select: **No load balancer** (we'll attach later)

**Health checks:**
- Keep defaults

**Group size:**
- Desired: `2`
- Minimum: `1`
- Maximum: `3`

**Scaling policies:**
- Target tracking scaling policy
- Metric: Average CPU utilization
- Target value: `70`

### Step 3: Create ASG

Click through and create.

Wait 2-3 minutes. Check **Instance management** tab - you should see 2 instances launching.

---

## 🎯 PART 4: CREATE TARGET GROUP

### Step 1: Create Target Group

1. EC2 → Target Groups → **Create**
2. Target type: **Instances**
3. Name: `jan26-week3-tg`
4. Protocol: HTTP
5. Port: `8000`
6. VPC: `jan26-vpc`

**Health check:**
- Protocol: HTTP
- Path: `/`
- Port: `8000`

### Step 2: Register Targets

**Don't manually select instances!** (they're managed by ASG)

Just click **Next** then **Create target group**.

We'll connect ASG to this target group via ALB.

---

## ⚖️ PART 5: CREATE APPLICATION LOAD BALANCER

### Step 1: Create ALB

1. EC2 → Load Balancers → **Create**
2. Type: **Application Load Balancer**
3. Name: `jan26-week3-alb`

**Scheme:** Internet-facing

**Network mapping:**
- VPC: `jan26-vpc`
- Subnets: Select BOTH
  - `public-jan26` (ap-south-1a)
  - `public-jan26-2` (ap-south-1b)

### Step 2: Create ALB Security Group

Create new security group:
- Name: `alb-sg`
- VPC: `jan26-vpc`
- Inbound rules:
  - HTTP (80) from 0.0.0.0/0
  - HTTPS (443) from 0.0.0.0/0

Select this security group for ALB.

### Step 3: Configure Listener

**Default action:**
- Protocol: HTTP
- Port: 80
- Forward to: `jan26-week3-tg`

### Step 4: Create ALB

Click **Create load balancer**

Wait 2-3 minutes for ALB to become **Active**.

---

## 🌐 PART 6: CONFIGURE DNS

### Step 1: Create Subdomain Record

1. Route 53 → Hosted zones → Your domain
2. **Create record**
3. Record name: `week3` (creates week3.yourdomain.com)
4. Record type: **A**
5. **Alias:** Yes
6. Route traffic to:
   - Application and Classic Load Balancer
   - Region: `ap-south-1`
   - Select your ALB: `jan26-week3-alb`
7. Create

### Step 2: Test HTTP

Wait 2-3 minutes for DNS propagation.

Visit: `http://week3.yourdomain.com`

Should see your Flask app (but "Not Secure").

---

## 🔐 PART 7: ADD HTTPS

### Step 1: Request SSL Certificate

1. Certificate Manager → **Request certificate**
2. Domain: `week3.yourdomain.com`
3. Validation: DNS validation
4. **Do NOT enable export** (keeps it free!)
5. Request

### Step 2: Validate Certificate

1. Click certificate
2. **Create records in Route 53**
3. Wait for status: **Issued** (~5-10 minutes)

### Step 3: Add HTTPS Listener to ALB

1. Load Balancers → Select your ALB
2. **Listeners** tab → **Add listener**
3. Protocol: **HTTPS**
4. Port: `443`
5. Default action: Forward to `jan26-week3-tg`

**Secure listener settings:**
- Security policy: Recommended
- Default SSL certificate: **From ACM**
- Select: `week3.yourdomain.com`

6. **Add**

### Step 4: Test HTTPS

Visit: `https://week3.yourdomain.com`

Should see:
- ✅ Green padlock
- ✅ Your Flask app
- ✅ Valid certificate

---

## 🧪 PART 8: TEST AUTO SCALING

### Verify Current State

1. ASG → Instance management
   - Should show 2 instances

2. Target Group → Targets
   - Should show 2 healthy targets

### Test Scale Down

Low traffic → ASG scales down to 1 instance automatically.

Check after 5-10 minutes:
- ASG → Activity history (shows scaling events)
- Target Group → Should show 1 healthy target

### Test Scale Up (Optional)

Generate load to trigger scale-up:

```bash
# Install stress tool on one instance
ssh -i jan26-key.pem ec2-user@<INSTANCE_IP>
sudo amazon-linux-extras install epel -y
sudo yum install stress -y

# Create CPU load
stress --cpu 8 --timeout 300
```

Check ASG after 2-3 minutes - should scale to 2-3 instances.

### Test HA (High Availability)

1. Manually terminate one instance
2. ASG automatically launches a new one
3. Target group updates automatically
4. Application stays available throughout

---

## 🧹 CLEANUP

**IMPORTANT:** Delete in this order to avoid charges:

1. **ALB** (charged hourly)
   - Load Balancers → Delete

2. **Target Group**
   - Target Groups → Delete

3. **Auto Scaling Group**
   - Set desired/min/max to 0
   - Wait for instances to terminate
   - Delete ASG

4. **Launch Template**
   - Launch Templates → Delete

5. **Certificate** (should be free if not exported)
   - Certificate Manager → Delete

6. **Route 53 Record**
   - Delete `week3` subdomain record

---

## 📋 SUBMISSION

Post in Discord:

```
✅ Week 3 Assignment Complete!

Name: [Your Name]
Domain: https://week3.yourdomain.com
GitHub: https://github.com/YOUR_USERNAME/jan26-bootcamp

✓ ASG with 2 instances
✓ ALB distributing traffic
✓ Target group healthy
✓ HTTPS working
✓ Auto scaling tested
```

---

## 🐛 TROUBLESHOOTING

### Instances not launching
```bash
# Check user data logs on instance
ssh -i jan26-key.pem ec2-user@<IP>
cat /home/ec2-user/install-logs.txt
sudo tail -f /var/log/cloud-init-output.log
```

### Target group shows unhealthy
- Verify app is running on port 8000
- Check security group allows port 8000
- Check health check path is `/`

### ALB returns 503 error
- No healthy targets
- Check ASG has running instances
- Check target group health status

### Can't create ALB
- Need 2 public subnets in different AZs
- Both subnets must have route to IGW
- Check route table associations

### Auto scaling not working
- Check CloudWatch for CPU metrics
- Verify scaling policy is enabled
- Wait 5-10 minutes for metrics to register

---

## 🎓 KEY LEARNINGS

### ASG Benefits
1. **Automatic healing:** Failed instances replaced
2. **Cost optimization:** Scale down when not needed
3. **HA:** Instances across multiple AZs
4. **No manual intervention:** Fully automated

### ALB Benefits
1. **Single entry point:** One DNS name for all instances
2. **SSL termination:** HTTPS handled at ALB, not instances
3. **Health checks:** Only route to healthy instances
4. **No Nginx needed:** ALB is the reverse proxy

### Production Best Practices
- Use private subnets for instances (not public)
- Use Systems Manager to access instances (no SSH port)
- Multiple AZs for true HA
- Proper health check endpoints
- CloudWatch alarms for scaling events

---

## ✅ COMPLETION CHECKLIST

- [ ] Launch template created and tested
- [ ] Two public subnets in different AZs
- [ ] ASG created with 2 instances
- [ ] Target group created
- [ ] ALB created with HTTP listener
- [ ] DNS subdomain pointing to ALB
- [ ] HTTP working
- [ ] SSL certificate issued (not exported!)
- [ ] HTTPS listener added to ALB
- [ ] HTTPS working with green padlock
- [ ] Tested auto scaling (scale down verified)
- [ ] Code pushed to GitHub

**Deadline:** Sunday 11:59 PM

---

## 📚 Additional Reading

**Before next class, understand:**
1. Difference between ALB, NLB, and Gateway LB
2. Target group types (instances, IPs, Lambda)
3. ALB listener rules and path-based routing
4. Health check parameters
5. ASG lifecycle hooks

---

*"Keep iterating. Nothing works the first time. Keep troubleshooting until you get the output." - Akhilesh*
