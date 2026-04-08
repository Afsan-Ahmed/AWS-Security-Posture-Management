import json
import os
from datetime import datetime
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
iam = boto3.client('iam')   


def check_root_account():
    response = iam.get_account_summary()
    return response['SummaryMap']['AccountMFAEnabled'] == 1

def check_account_access_keys():
    response = iam.get_account_summary()
    return response['SummaryMap']['AccountAccessKeysPresent'] == 1

def check_cloudtrail():
    ct = boto3.client('cloudtrail')
    response = ct.describe_trails()
    return len(response['trailList']) > 0

def check_password_policy():
    try:
        iam.get_account_password_policy()
        return True
    except:
        return False

def lambda_handler(event, context):
    check = [
        ('check_root_account', check_root_account()),
        ('check_account_access_keys', check_account_access_keys()),
        ('check_cloudtrail', check_cloudtrail()),
        ('check_password_policy', check_password_policy())
    ]

    passed = sum(1 for _, result in check if result)
    score = round((passed / len(check)) * 100)


    table.put_item(Item={
        'account_id': os.environ['ACCOUNT_ID'],
        'timestamp': datetime.utcnow().isoformat(),
        'score': score,
        'checks_passed': passed,
        'checks_total': len(check)
    })
    
    return {
        'statusCode': 200,
        'score': score,
        'passed': passed,
        'total': len(check)
    }