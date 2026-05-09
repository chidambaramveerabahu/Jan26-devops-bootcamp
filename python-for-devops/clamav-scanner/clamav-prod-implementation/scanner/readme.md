1. create a buclet name landing bucket 
2. create a sqs queue -> clamav scanner queue
3. attach a sqs policy to the queue -> allow the bucket to send notification on each upload

# sqs queue policy to allow s3 notification
```bash

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ToSendMessage",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "SQS:SendMessage",
      "Resource": "arn:aws:sqs:ap-south-1:879381241087:*",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "879381241087"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:s3:::*"
        }
      }
    }
  ]
}
```

4. configure bucket notification from landing bucket -> sqs queue you created

# scanner part start
## flow will be

- scanner job is dockerised with proper os deps
- sqs will trigger the automation
- automation will start
- update the clamav db -> freshclam 
- flow will start ->>>
-> read the message from the queue
-> doiwnload the bucket object from landiung and place iot locally
-> scan the file and notedown the outcome -> clean/dirty
-> Create bucket object in landing bucket -> tahs -> scanned = true, scan_result = clean/dirty
-> if the file is clean -> sent the file to clean bucket
-> if the file is dirty -> send a notification either via sqs or sns

