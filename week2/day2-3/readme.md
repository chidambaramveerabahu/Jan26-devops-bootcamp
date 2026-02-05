

<!-- to decrypt the private key -->

openssl rsa -in private_key.txt -out private_key.pem


# Create SSL directory
``` bash
sudo mkdir -p /etc/nginx/ssl
sudo chmod 700 /etc/nginx/ssl
```
# copy 3 files from local machine
``` bash
 touch your_certificate.crt
 touch decrypted_private.key
  touch ca_bundle.crt
```
``` bash
 vi your_certificate.crt
 ```
 ``` bash
 vi decrypted_private.key
 ```

 ``` bash
 vi ca_bundle.crt 
 ```


# Copy your files (adjust names based on what you have)
sudo cp your_certificate.crt /etc/nginx/ssl/certificate.crt
sudo cp decrypted_private.key /etc/nginx/ssl/private.key

# If you have CA bundle/chain file
sudo cp ca_bundle.crt /etc/nginx/ssl/ca_bundle.crt

# Set proper permissions (CRITICAL for security)
sudo chmod 600 /etc/nginx/ssl/private.key
sudo chmod 644 /etc/nginx/ssl/certificate.crt
sudo chmod 644 /etc/nginx/ssl/ca_bundle.crt

# Verify ownership
sudo chown root:root /etc/nginx/ssl/*




# run app as systemctl service

 touch /etc/systemd/system/akhilesh.service

 # paste below content 

 ```bash
 [Unit]
Description=My Python Application with Nginx
After=network.target

[Service]
Type=forking
User=nginx
Group=nginx
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/app/.venv/bin"
ExecStartPre=/bin/bash -c 'python3 -m venv .venv'
ExecStartPre=/bin/bash -c 'source .venv/bin/activate && pip install -r requirements.txt'
ExecStart=/bin/bash -c 'source .venv/bin/activate && gunicorn -w 4 -b 0.0.0.0:8000 app:app --daemon && nginx -g "daemon off;"'
ExecStop=/usr/bin/pkill -f gunicorn
ExecStop=/usr/bin/nginx -s stop
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```