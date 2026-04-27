import boto3
import json
import os
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    print("Received GET request for specific submission.")
    
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

        table_name = os.environ.get('TABLE_NAME', 'Submission')
        table = dynamodb.Table(table_name)
        
        print(f"Fetching record for submissionId: {submission_id}")
        
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

        print("Successfully retrieved record.")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(item, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error fetching submission: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }

if __name__ == "__main__":
    print("Initializing mock Lambda execution for GET /submissions/{submissionId}...")
    
    mock_event = {
        "pathParameters": {
            "submissionId": "sub-123"
        }
    }
    
    result = lambda_handler(mock_event, None)
    
    print("\nSimulated API Response:")
    print(json.dumps(result, indent=4))
