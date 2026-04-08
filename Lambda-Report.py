import json
import boto3
import os
from date_time import date_time

dynamodb = boto3.resource('dynamodb')
scores_table = dynamodb.Table(os.environ['SCORES_TABLE'])
findings_table = dynamodb.Table(os.environ['FINDINGS_TABLE'])
s3 = boto3.client('s3')
sns = boto3.client('sns')

def get_latest_score():
    response = scores_table.scan(
        Limit=1
    )
    items = response.get('Items', [])
    if items:
        return items[0]
    return {'score': 0, 'checks_passed': 0, 'checks_total': 0}


def get_findings_summary():
    response = findings_table.scan()
    items = response.get('Items', [])
    
    open_findings = [i for i in items if i.get('status') == 'OPEN']
    remediated = [i for i in items if i.get('status') == 'REMEDIATED']
    
    return {
        'total': len(items),
        'open': len(open_findings),
        'remediated': len(remediated)
    }


def lambda_handler(event, context):
    score_data = get_latest_score()
    findings_data = get_findings_summary()
    
    report = {
        'generated_at': datetime.utcnow().isoformat(),
        'security_score': score_data.get('score', 0),
        'checks_passed': score_data.get('checks_passed', 0),
        'checks_total': score_data.get('checks_total', 0),
        'findings': findings_data
    }
    
    report_key = f"reports/report-{datetime.utcnow().strftime('%Y-%m-%d')}.json"
    s3.put_object(
        Bucket=os.environ['REPORTS_BUCKET'],
        Key=report_key,
        Body=json.dumps(report, indent=2)
    )
    
    sns.publish(
        TopicArn=os.environ['SNS_TOPIC_ARN'],
        Subject=f'Weekly Security Report - Score: {score_data.get("score", 0)}/100',
        Message=json.dumps(report, indent=2)
    )
    
    return {
        'statusCode': 200,
        'report': report
    }