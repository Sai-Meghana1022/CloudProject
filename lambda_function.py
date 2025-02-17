import json
import boto3
import urllib.parse

# Initialize AWS clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

# Replace with your actual bucket and SNS topic details
SOURCE_BUCKET = "<SOURCE_BUCKET_NAME>"
BACKUP_BUCKET = "<BACKUP_BUCKET_NAME>"
SNS_TOPIC_ARN = "arn:aws:sns:<YOUR_REGION>:<YOUR_AWS_ACCOUNT_ID>:<SNS_TOPIC_NAME>"

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        decoded_key = urllib.parse.unquote_plus(object_key)

        # Copy object to the backup bucket
        copy_source = {'Bucket': source_bucket, 'Key': decoded_key}
        try:
            s3_client.copy_object(Bucket=BACKUP_BUCKET, Key=decoded_key, CopySource=copy_source)
            copy_status = f"File '{decoded_key}' copied successfully from '{source_bucket}' to '{BACKUP_BUCKET}'."
        except Exception as e:
            copy_status = f"Error copying file '{decoded_key}': {str(e)}"

        # Construct the SNS message
        message = f"File '{decoded_key}' was uploaded to '{source_bucket}'.\n\n{copy_status}"

        # Publish message to SNS
        try:
            sns_response = sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject="New S3 Upload & Backup Status"
            )
            print("SNS Publish Response:", sns_response)
        except Exception as e:
            print(f"Error publishing to SNS: {str(e)}")

    return {
        "statusCode": 200,
        "body": json.dumps("Lambda executed successfully!")
    }
