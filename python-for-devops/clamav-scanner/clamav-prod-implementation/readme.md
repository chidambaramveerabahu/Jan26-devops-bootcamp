


Queue_url = os.getenv("QUEUE_URL")
clean_bucket = os.getenv("CLEAN_BUCKET")
locals_path = os.getenv("LOCAL_PATH", "/tmp")
from_email = os.getenv("FROM_EMAIL")
to_email = os.getenv("TO_EMAIL").split(",")


# running locally
```bash
export QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/879381241087/clamav-scanner-queue
export CLEAN_BUCKET=clean-bucket-879381241087
export FROM_EMAIL=aditiyamishranit@gmail.com
export TO_EMAIL="livingdevops@gmail.com,Nimmaturi234@gmail.com"
export AWS_ACCESS_KEY_ID=<aws access key>
export AWS_SECRET_ACCESS_KEY=<aws secrfet key>
export AWS_REGION=ap-south-1 
```

```bash
python main.py
```


## if running with docker

```bash
docker run \
-e QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/879381241087/clamav-scanner-queue \
-e CLEAN_BUCKET=clean-bucket-879381241087 \
-e FROM_EMAIL=aditiyamishranit@gmail.com \
-e TO_EMAIL="livingdevops@gmail.com,Nimmaturi234@gmail.com" \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
-e AWS_REGION=ap-south-1 \
livingdevopswithakhilesh/clamav-scanner:arm64

```

running it on aws ecs

use -> 