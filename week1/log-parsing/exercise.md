
## Complete Setup Files

### Directory Structure
```
log-analysis-lab/
├── docker-compose.yml
├── generator.py
├── flask-app.py
└── logs/
```

---

## docker-compose.yml

```yaml
version: '3'
services:
  flask-app:
    image: python:3.9-slim
    ports:
      - "8080:5000"
    volumes:
      - ./flask-app.py:/app.py
    working_dir: /
    command: bash -c "pip install flask && python /app.py"
    container_name: flask-app

  log-generator:
    image: python:3.9-slim
    volumes:
      - ./generator.py:/generator.py
    command: bash -c "pip install requests && python /generator.py"
    depends_on:
      - flask-app
    container_name: log-generator
```

---

## flask-app.py

```python
#!/usr/bin/env python3
from flask import Flask, request, jsonify
from datetime import datetime
import random
import sys

app = Flask(__name__)

# Configure logging to stdout (Docker logs)
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def log_request(status_code, response_size):
    """Generate Apache-style access log"""
    timestamp = datetime.now().strftime('%d/%b/%Y:%H:%M:%S +0000')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    method = request.method
    path = request.path
    user_agent = request.headers.get('User-Agent', '-')
    
    log_line = f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status_code} {response_size} "-" "{user_agent}"'
    
    logging.info(log_line)

@app.route('/')
def home():
    response_size = random.randint(500, 2000)
    log_request(200, response_size)
    return jsonify({
        "message": "Welcome to Flask App",
        "status": "success"
    })

@app.route('/api/users')
def users():
    response_size = random.randint(1000, 5000)
    log_request(200, response_size)
    return jsonify({
        "users": ["user1", "user2", "user3"],
        "count": 3
    })

@app.route('/api/products')
def products():
    response_size = random.randint(2000, 10000)
    log_request(200, response_size)
    return jsonify({
        "products": ["product1", "product2"],
        "count": 2
    })

@app.route('/api/orders')
def orders():
    response_size = random.randint(1500, 8000)
    log_request(200, response_size)
    return jsonify({
        "orders": ["order1", "order2"],
        "count": 2
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Simulate some login failures
    if random.random() < 0.3:  # 30% failure rate
        response_size = random.randint(300, 800)
        log_request(401, response_size)
        return jsonify({"error": "Unauthorized"}), 401
    
    response_size = random.randint(500, 1500)
    log_request(200, response_size)
    return jsonify({"message": "Login successful"})

@app.route('/logout')
def logout():
    response_size = random.randint(200, 500)
    log_request(200, response_size)
    return jsonify({"message": "Logged out"})

@app.route('/admin')
def admin():
    # Simulate forbidden access
    if random.random() < 0.5:  # 50% forbidden
        response_size = random.randint(300, 600)
        log_request(403, response_size)
        return jsonify({"error": "Forbidden"}), 403
    
    response_size = random.randint(1000, 3000)
    log_request(200, response_size)
    return jsonify({"message": "Admin panel"})

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        response_size = random.randint(200, 400)
        log_request(400, response_size)
        return jsonify({"error": "Missing query parameter"}), 400
    
    response_size = random.randint(1000, 5000)
    log_request(200, response_size)
    return jsonify({
        "query": query,
        "results": []
    })

@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    # Simulate server errors occasionally
    if random.random() < 0.1:  # 10% server error
        response_size = random.randint(500, 1000)
        log_request(500, response_size)
        return jsonify({"error": "Internal Server Error"}), 500
    
    response_size = random.randint(2000, 8000)
    log_request(200, response_size)
    return jsonify({"message": "Checkout successful"})

@app.route('/static/<path:filename>')
def static_files(filename):
    response_size = random.randint(5000, 50000)
    log_request(200, response_size)
    return jsonify({"file": filename})

@app.errorhandler(404)
def not_found(e):
    response_size = random.randint(300, 600)
    log_request(404, response_size)
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    response_size = random.randint(500, 1000)
    log_request(500, response_size)
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("Starting Flask app on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
```

---

## generator.py

```python
#!/usr/bin/env python3
import random
import time
import requests
from datetime import datetime

FLASK_URL = "http://flask-app:5000"

# Simulate different endpoints
ENDPOINTS = [
    "/",
    "/api/users",
    "/api/products",
    "/api/orders",
    "/login",
    "/logout",
    "/admin",
    "/static/image.jpg",
    "/api/search?q=test",
    "/checkout",
    "/nonexistent",  # Will generate 404
    "/api/search",   # Will generate 400 (missing param)
]

# Simulate different user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "curl/7.68.0",
    "python-requests/2.28.0",
    "Googlebot/2.1",
    "BadBot/1.0",
    "Scanner/1.0"
]

# Simulate different IPs
IPS = [
    "192.168.1.100",
    "192.168.1.101", 
    "192.168.1.102",
    "10.0.0.50",
    "10.0.0.51",
    "172.16.0.10",
    "172.16.0.11",
    "203.0.113.42",  # Suspicious IP - will make many requests
    "198.51.100.50", # Another suspicious IP
]

def generate_traffic():
    """Generate realistic traffic patterns"""
    print("Waiting for Flask app to start...")
    time.sleep(10)
    print("Starting traffic generation...")
    
    request_count = 0
    
    while True:
        try:
            # Choose endpoint with weighted probability
            weights = [20, 15, 15, 10, 8, 5, 5, 5, 5, 5, 3, 2]  # Higher weight = more frequent
            endpoint = random.choices(ENDPOINTS, weights=weights)[0]
            
            user_agent = random.choice(USER_AGENTS)
            
            # Suspicious IPs make more requests
            if random.random() < 0.2:  # 20% from suspicious IPs
                ip = random.choice(["203.0.113.42", "198.51.100.50"])
            else:
                ip = random.choice(IPS)
            
            headers = {
                'User-Agent': user_agent,
                'X-Forwarded-For': ip
            }
            
            # Make request
            method = 'POST' if endpoint in ['/login', '/checkout'] and random.random() < 0.3 else 'GET'
            
            try:
                if method == 'POST':
                    response = requests.post(f"{FLASK_URL}{endpoint}", headers=headers, timeout=5)
                else:
                    response = requests.get(f"{FLASK_URL}{endpoint}", headers=headers, timeout=5)
                
                request_count += 1
                if request_count % 100 == 0:
                    print(f"Generated {request_count} requests...")
                    
            except requests.exceptions.RequestException as e:
                pass
            
            # Variable delay between requests
            # Suspicious IPs make faster requests
            if ip in ["203.0.113.42", "198.51.100.50"]:
                time.sleep(random.uniform(0.1, 0.5))  # Faster requests
            else:
                time.sleep(random.uniform(0.5, 3))    # Normal requests
            
        except Exception as e:
            print(f"Error generating traffic: {e}")
            time.sleep(5)

if __name__ == "__main__":
    generate_traffic()
```

---

## Quick Start Guide

### Step 1: Create Directory and Files

```bash
# Create directory
mkdir log-analysis-lab
cd log-analysis-lab

# Create the files (copy content from above)
# docker-compose.yml
# flask-app.py
# generator.py
```

### Step 2: Start the Lab

```bash
# Start containers
docker-compose up -d

# Check if containers are running
docker ps

# You should see:
# - flask-app (running Flask on port 8080)
# - log-generator (generating traffic)
```

### Step 3: View Logs in Real-Time

```bash
# View Flask app logs (this is your access log)
docker logs -f flask-app

# You'll see Apache-style logs like:
# 192.168.1.100 - - [27/Jan/2026:10:30:45 +0000] "GET /api/users HTTP/1.1" 200 2341 "-" "Mozilla/5.0..."
```

### Step 4: Save Logs to File for Analysis

```bash
# Save current logs to file
docker logs flask-app > access.log

# Or continuously save logs
docker logs -f flask-app >> access.log
```

### Step 5: Start Analyzing

```bash
# Now use all the commands from the lab!

# Top 10 IPs
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -10

# Error rate
awk '$9 >= 400' access.log | wc -l

# Most hit endpoints
awk '{print $7}' access.log | sort | uniq -c | sort -nr | head -10

# Follow logs live with grep
docker logs -f flask-app | grep --color=auto -E " (4|5)[0-9]{2} "
```

---

## Testing the Setup

### Test 1: Verify Flask is Running

```bash
# From your host machine
curl http://localhost:8080/

# You should get JSON response
# Check logs
docker logs flask-app | tail -5
```

### Test 2: Generate Manual Traffic

```bash
# Generate some test requests
for i in {1..10}; do curl http://localhost:8080/api/users; done
for i in {1..5}; do curl http://localhost:8080/nonexistent; done
for i in {1..3}; do curl http://localhost:8080/admin; done

# Check logs
docker logs flask-app | tail -20
```

### Test 3: Verify Log Format

```bash
docker logs flask-app | tail -1

# Should look like:
# 172.17.0.1 - - [27/Jan/2026:10:30:45 +0000] "GET /api/users HTTP/1.1" 200 2341 "-" "curl/7.68.0"
```

---

## Quick Analysis Commands

Once you have logs, try these:

```bash
# Save logs first
docker logs flask-app > access.log

# Top IPs
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -10

# Status code distribution
awk '{print $9}' access.log | sort | uniq -c | sort -nr

# Find 404 errors
grep " 404 " access.log

# Find suspicious IPs (many requests)
awk '{print $1}' access.log | sort | uniq -c | sort -nr | awk '$1 > 50'

# Requests per endpoint
awk '{print $7}' access.log | sort | uniq -c | sort -nr

# Error rate
TOTAL=$(wc -l < access.log)
ERRORS=$(awk '$9 >= 400' access.log | wc -l)
echo "Total: $TOTAL, Errors: $ERRORS, Rate: $(awk "BEGIN {printf \"%.2f%%\", ($ERRORS/$TOTAL)*100}")"
```

---

## Continuous Log Collection Script

Create `collect-logs.sh`:

```bash
#!/bin/bash

# Collect logs every 5 seconds
while true; do
    docker logs flask-app > access.log
    echo "Logs updated: $(date)"
    sleep 5
done
```

```bash
chmod +x collect-logs.sh
./collect-logs.sh &
```

Now you always have fresh logs in `access.log` file!

Now you always have fresh logs in `access.log` file!


## greping

``` bash
# 1. All POST requests to /login that failed
grep -E "POST /login.*\" (401|403)" access.log

# 2. All requests from IPs starting with 203
grep -E "^203\." access.log

# 3. All 404 errors in the last hour (hour 15)
grep -E "\[.*/.*/.* 15:.*\].*\" 404" access.log

# 4. All requests to admin panel
grep -E "/admin" access.log

# 5. All suspicious SQL patterns
grep -iE "select.*from|union.*select" access.log
```

## common grep patterns

```bash
# Basic Search
grep "pattern" file                    # Find pattern
grep -i "pattern" file                 # Case insensitive
grep -v "pattern" file                 # Invert (exclude)
grep -c "pattern" file                 # Count matches
grep -n "pattern" file                 # Show line numbers

# Context
grep -A 3 "pattern" file               # 3 lines after
grep -B 3 "pattern" file               # 3 lines before
grep -C 3 "pattern" file               # 3 lines both sides

# Regex
grep -E "pat1|pat2" file               # OR logic
grep -E "^pattern" file                # Start of line
grep -E "pattern$" file                # End of line
grep -E "[0-9]{3}" file                # Exactly 3 digits
grep -E "pat.*tern" file               # Any chars between

# Common Patterns
grep -E " [45][0-9]{2} " file          # All errors (4xx, 5xx)
grep -E "^[0-9.]+\." file              # IP addresses
grep -E "\?.*=" file                   # URLs with parameters
grep -iE "bot|crawler" file            # Bots/crawlers
```

## some regex patterns

``` bash
# Extract all status codes
grep -oE " [0-9]{3} " access.log
# Explanation: Extracts only 3-digit numbers (status codes)
```

---

## Part 2: Regex Patterns for Log Analysis

### Understanding Regex Special Characters
```
.   = Any single character
*   = Zero or more of previous
+   = One or more of previous
?   = Zero or one of previous
^   = Start of line
$   = End of line
[]  = Character class
|   = OR
()  = Grouping
{}  = Exact count
\   = Escape special character
```
---


---

## Cleanup

```bash
# Stop containers
docker-compose down

# Remove logs
rm access.log

# Restart fresh
docker-compose up -d
```

---

## Troubleshooting

**Issue: Flask app not starting**
```bash
# Check logs
docker logs flask-app

# Common issue: Port already in use
# Solution: Change port in docker-compose.yml
ports:
  - "8081:5000"  # Use different port
```

**Issue: No logs appearing**
```bash
# Check if generator is running
docker logs log-generator

# Restart if needed
docker-compose restart log-generator
```

**Issue: "requests module not found"**
```bash
# Already handled in docker-compose with:
# command: bash -c "pip install requests && python /generator.py"

# But if needed, you can manually install:
docker exec -it log-generator pip install requests
```

---

## Why This Setup Works

1. **Flask runs on 0.0.0.0:5000** - accessible from other containers
2. **requests module** - installed automatically via docker-compose command
3. **Apache-style logs** - compatible with all analysis commands from the lab
4. **Realistic traffic** - various endpoints, status codes, IPs, user agents
5. **Easy to extend** - add more endpoints, change traffic patterns

Now you can follow the entire lab using these logs! All the grep, awk, sed commands will work perfectly.
