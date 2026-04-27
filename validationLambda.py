import boto3
import json

MY_ACCESS_KEY = "XXX"
MY_SECRET_KEY = "XXX"
MY_SESSION_TOKEN = "XXX"
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

s3_client = boto3.client(
    's3',
    region_name='us-east-1',
    aws_access_key_id=MY_ACCESS_KEY,
    aws_secret_access_key=MY_SECRET_KEY,
    aws_session_token=MY_SESSION_TOKEN    
)

TARGET_KEYWORDS = {"enabled", "30days"}

#Clean input text
def normalize(text):
    return text.lower().replace(" ", "")

#เช็ค text กับ keyword
def find_keywords(text_items):
    found_keywords = set()
    confidences = []

    for text, confidence in text_items:
        normalized = normalize(text)

        for kw in TARGET_KEYWORDS:
            if kw in normalized:
                found_keywords.add(kw)
                confidences.append(confidence)

    avg_conf = 0
    if confidences:
        avg_conf = sum(confidences) / len(confidences)

    return found_keywords, avg_conf

def run_rekognition(image_bytes):
    response = rekognition_client.detect_text(Image={"Bytes": image_bytes})

    #เอาทั้ง text กับ confidence
    text_items = [
        (t["DetectedText"], t["Confidence"])
        for t in response.get("TextDetections", [])
    ]

    return find_keywords(text_items)


def run_textract(image_bytes):
    response = textract_client.detect_document_text(Document={"Bytes": image_bytes})

    text_items = [
        (block["Text"], block["Confidence"])
        for block in response.get("Blocks", [])
        if block["BlockType"] == "LINE"
    ]

    return find_keywords(text_items)


def lambda_handler(event, context):

    bucket_name = "thisone99"
    image_key = "image (1).png"

    print(f"Fetching image from S3: {image_key}")

    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=image_key
    )

    image_bytes = response["Body"].read()

    # Tier 1: Rekognition
    try:
        print("Tier 1: Rekognition")
        found, avg_conf = run_rekognition(image_bytes)

        #ต้องเจอ Keyword ครบทุกคำถึงจะ Pass
        if TARGET_KEYWORDS.issubset(found):
            print("Pass: Rekognition found all required keywords.")
            r_missing=[]
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "avg_confidence": avg_conf,
                    "engine": "Rekognition",
                    "keywordDetected": list(found),
                    "status": "accepted",
                    "missing_words": r_missing

                })
            }

    except Exception as e:
        print(f"Rekognition Error: {str(e)}. Proceeding to fallback.")

    print("Rekognition fallback triggered. Executing Tier 2: Amazon Textract...")

    # Tier 2: Textract
    try:
        print("Tier 2: Textract")
        found = run_textract(image_bytes)

        if TARGET_KEYWORDS.issubset(found):
            print("Pass: Textract found all required keywords.")
            t_missing=[]
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "avg_confidence": avg_conf,
                    "engine": "Textract",
                    "keywordDetected": list(found),
                    "status": "accepted",
                    "missing_words": t_missing                  
                })
            }

        missing = list(TARGET_KEYWORDS - set(found))
        print(f"Reject: Missing keywords: {missing}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "avg_confidence": avg_conf,
                "engine": "None",
                "keywordDetected":list(found),
                "status": "failed",
                "missing_words": missing
            })
        }

    except Exception as e:
        print("Textract error:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({"status": "Error"})
        }


if __name__ == "__main__":
    result = lambda_handler({}, None)
    print(json.dumps(result, indent=4))
