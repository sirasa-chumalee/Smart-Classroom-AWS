import boto3
import json

MY_ACCESS_KEY = "ไปเอาคีย์ในห้อง keys"
MY_SECRET_KEY = "ไปเอาคีย์ในห้อง keys"
MY_SESSION_TOKEN = "ไปเอาคีย์ในห้อง keys"

rekognition_client = boto3.client(
    'rekognition', 
    region_name='us-east-1',
    aws_access_key_id=MY_ACCESS_KEY,
    aws_secret_access_key=MY_SECRET_KEY,
    aws_session_token=MY_SESSION_TOKEN
)

textract_client = boto3.client(
    'textract', 
    region_name='us-east-1',
    aws_access_key_id=MY_ACCESS_KEY,
    aws_secret_access_key=MY_SECRET_KEY,
    aws_session_token=MY_SESSION_TOKEN
)

TARGET_KEYWORDS = ["enabled", "30days"]

def lambda_handler(event, context):
    image_filename = "test.png"
    
    
    with open(image_filename, "rb") as image_file:
        image_bytes = image_file.read()
    
    print(f"Starting image validation: {image_filename}")

    try:
        print("Executing Tier 1: Amazon Rekognition...")
        rekog_response = rekognition_client.detect_text(
            Image={'Bytes': image_bytes}
        )
        found_keywords = set()
        for text_detail in rekog_response.get('TextDetections', []):
            detected_text = text_detail['DetectedText'].lower()
            for kw in TARGET_KEYWORDS:
                if kw in detected_text:
                    found_keywords.add(kw)
                
        if len(found_keywords) == len(TARGET_KEYWORDS):
            print(f"Pass: Rekognition found all required keywords.")
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'Pass', 'engine': 'Rekognition'})
            }
            
    except Exception as e:
        print(f"Rekognition Error: {str(e)}. Proceeding to fallback.")

    print("Rekognition fallback triggered. Executing Tier 2: Amazon Textract...")
    
    try:
        textract_response = textract_client.detect_document_text(
            Document={'Bytes': image_bytes}
        )
        
        textract_found_keywords = set()
        for block in textract_response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                detected_text = block.get('Text', '').lower()
                for kw in TARGET_KEYWORDS:
                    if kw in detected_text:
                        textract_found_keywords.add(kw)
                    
        if len(textract_found_keywords) == len(TARGET_KEYWORDS):
            print(f"Pass: Textract found all required keywords.")
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'Pass', 'engine': 'Textract'})
            }
        else:
            missing = list(set(TARGET_KEYWORDS) - textract_found_keywords)
            print(f"Reject: Missing keywords: {missing}")
            return {
                'statusCode': 200, 
                'body': json.dumps({
                    'status': 'Reject', 
                    'reason': 'Missing Keywords',
                    'missing': missing
                })
            }
            
    except Exception as e:
        print(f"Textract Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'status': 'Error', 'message': 'Internal Server Error'})
        }

if __name__ == "__main__":
    print("Initializing mock Lambda execution...")
    
    mock_event = {} 
    
    result = lambda_handler(mock_event, None)
    
    print("\nSimulated API Response:")
    print(json.dumps(result, indent=4))
