import boto3
import os
from datetime import datetime

iam = boto3.client('iam')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['FINDINGS_TABLE'])
sns = boto3.client('sns')

DRY_RUN = os.environ.get('DRY_RUN', 'false').lower() == 'true'

def quarantine_key(username, access_key_id):
    if DRY_RUN:
        print(f"DRY RUN: Would deactivate key {access_key_id} for user {username}")
        return
    
    iam.update_access_key(
        UserName=username,
        AccessKeyId=access_key_id,
        Status='Inactive'
    )
    
    iam.attach_user_policy(
        UserName=username,
        PolicyArn='arn:aws:iam::aws:policy/AWSDenyAll'
    )

def save_finding(username, access_key_id, dry_run):
    table.put_item(Item={
        'finding_id': f"remediation-{access_key_id}",
        'timestamp': datetime.utcnow().isoformat(),
        'username': username,
        'access_key_id': access_key_id,
        'action': 'KEY_QUARANTINED',
        'status': 'DRY_RUN' if dry_run else 'REMEDIATED'
    })

def lambda_handler(event, context):
    detail = event.get('detail', {})
    
    username = detail.get('userIdentity', {}).get('userName', 'unknown')
    access_key_id = detail.get('accessKeyDetails', {}).get('accessKeyId', 'unknown')
    
    print(f"Processing finding for user: {username}, key: {access_key_id}")
    
    quarantine_key(username, access_key_id)
    save_finding(username, access_key_id, DRY_RUN)
    
    if not DRY_RUN:
        sns.publish(
            TopicArn=os.environ['SNS_TOPIC_ARN'],
            Subject='Security Alert: IAM Key Quarantined',
            Message=f'Key {access_key_id} for user {username} has been quarantined automatically.'
        )
    
    return {
        'statusCode': 200,
        'message': f'Key {access_key_id} processed',
        'dry_run': DRY_RUN
    }