<img width="1354" height="677" alt="image" src="https://github.com/user-attachments/assets/a9e92c54-f7c5-47bf-afed-af190c997eda" /># AWS Security Posture Management (SPM) Platform

A real-time cloud security monitoring and auto-remediation platform built on AWS.
Continuously monitors an AWS account, scores it against CIS Benchmark standards,
automatically remediates threats, and displays everything on a live dashboard.

## Architecture

Data Sources → EventBridge → Lambda Functions → DynamoDB → Dashboard

## Features

- Real-time security scoring based on CIS Benchmark (0-100 score)
- Automated threat detection using GuardDuty, CloudTrail, AWS Config, IAM Access Analyzer, Security Hub
- Auto-remediation of compromised IAM keys (deactivates key + attaches deny-all policy in under 10 seconds)
- Dry run mode for safe testing before enabling auto-remediation in production
- Full audit trail of all remediation actions stored in DynamoDB
- Weekly compliance reports automatically generated and emailed via SNS
- Live dashboard built with Streamlit showing score, findings, and CIS checks

## AWS Services Used

- GuardDuty — threat detection
- CloudTrail — API audit logging
- AWS Config — resource compliance rules
- IAM Access Analyzer — external access detection
- Security Hub — findings aggregation
- EventBridge — event routing
- Lambda — serverless processing
- DynamoDB — real-time data storage
- S3 — logs and reports storage
- SNS/SES — alerts and email reports

## Lambda Functions

### Score Calculator
- Runs CIS Benchmark checks using boto3
- Calculates security score out of 100
- Stores results in DynamoDB with timestamp

### Auto Remediator
- Triggered by high severity GuardDuty findings (severity >= 7)
- Deactivates compromised IAM access keys
- Attaches AWSDenyAll policy to compromised user
- Supports dry run mode
- Logs all actions to DynamoDB for audit trail
- Sends SNS alert on every remediation

### Report Generator
- Runs every Monday 8am via EventBridge scheduler
- Pulls latest score and findings from DynamoDB
- Uploads JSON report to S3
- Emails weekly summary via SNS

## EventBridge Rules

- High severity findings (severity >= 7) → Remediator Lambda
- All findings → Score Calculator Lambda
- Weekly schedule (Monday 8am) → Report Generator Lambda

## Security Best Practices Implemented

- All Lambda functions use least-privilege IAM roles
- S3 buckets have public access blocked
- CloudTrail enabled across all regions
- DynamoDB encryption at rest enabled
- Dry run mode for safe auto-remediation testing
- Full audit trail for all security actions

## Setup

1. Enable AWS services: GuardDuty, CloudTrail, Config, IAM Access Analyzer, Security Hub
2. Create DynamoDB tables: spm-security-scores, spm-findings
3. Deploy Lambda functions with environment variables
4. Create EventBridge rules
5. Run dashboard: streamlit run dashboard/dashboard.py

## Dashboard Using Streamlit

Live security dashboard showing:
- Security score with color indicator (green/yellow/red)
- Open vs remediated findings count
- CIS Benchmark checks pass/fail
- Recent findings table with status

  <img width="1354" height="677" alt="image" src="https://github.com/user-attachments/assets/8e37630f-6db9-4e65-8647-ebee053f7618" />

