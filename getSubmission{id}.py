import boto3
import json
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    print("Received GET request for specific submission.")

    table_name = os.environ.get('TABLE_NAME', 'Submission')
    table = dynamodb.Table(table_name)

    try:
        path_params = event.get('pathParameters') or {}
        submission_id = path_params.get('submissionId')

        if not submission_id:
            print("Error: Missing submissionId in path parameters.")
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Missing submissionId path parameter'})
            }

        print(f"Fetching record for submissionId: {submission_id}")
        
        # Use get_item for exact match query (Fastest operation in DynamoDB)
        response = table.get_item(
            Key={
                'submissionId': submission_id
            }
        )

        item = response.get('Item')

        if not item:
            print(f"Record not found for submissionId: {submission_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Submission not found'})
            }

        formatted_item = {
            "submissionId": item.get("submissionId", "unknown"),
            "labId": item.get("labId", "unknown"),
            "studentId": item.get("studentId", "unknown"),
            "fileKey": item.get("fileKey", "unknown"),
            "avgConfidence": float(item.get("avgConfidence", 0.0)),
            "grade": int(item.get("grade", 0)),
            "engine": item.get("engine", "N/A"),
            "keywordsDetected": item.get("keywordsDetected", []),
            "status": item.get("status", "pending"),
            "missingWords": item.get("missingWords", [])
        }

        print("Successfully retrieved record.")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*', 
                'Access-Control-Allow-Credentials': True,
                'Content-Type': 'application/json'
            },
            'body': json.dumps(formatted_item)
        }

    except Exception as e:
        print(f"Database Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal Server Error while fetching data'})
        }
