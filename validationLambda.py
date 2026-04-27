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
MIN_CONFIDENCE = 90

def normalize(text):
    """Clean input """
    return text.lower().replace(" ", "")

def find_keywords(text_items):
    found_keywords = set()
    confidences = []

    for text, confidence in text_items:
        if confidence < MIN_CONFIDENCE:
            continue
        normalized = normalize(text)
        for kw in TARGET_KEYWORDS:
            if kw in normalized:
                found_keywords.add(kw)
                confidences.append(confidence)

    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    return found_keywords, avg_conf

def run_rekognition(image_bytes):
    response = rekognition_client.detect_text(Image={"Bytes": image_bytes})
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

#Lambda
def lambda_handler(event, context):
    bucket_name = "thisone99"
    image_key = "image (1).png"

    print(f"Fetching image from S3: {image_key} ...")
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=image_key)
        image_bytes = response["Body"].read()
        print("Image loaded successfully\n")
    except Exception as e:
        print("Error fetching image:", str(e))
        return {"statusCode": 500, "body": {"error": "Cannot fetch image from S3"}}

    #Rekognition
    try:
        print("Running Rekognition...")
        found, avg_conf = run_rekognition(image_bytes)
        print("Rekognition result:", [(t, round(c,2)) for t, c in zip(found, [avg_conf]*len(found))])

        if TARGET_KEYWORDS.issubset(found):
            print("Rekognition PASS\n")
            return {
                "statusCode": 200,
                "body": {
                    "submissionId": event.get("submissionId", ""),
                    "avg_confidence": round(avg_conf, 2),
                    "engine": "Rekognition",
                    "keywordDetected": list(found),
                    "status": "accepted",
                    "missing_words": []
                }
            }
    except Exception as e:
        print("Rekognition failed:", str(e))
        print("Falling back to Textract...\n")

    #Textract
    try:
        print("Running Textract...")
        found, avg_conf = run_textract(image_bytes)
        print("Textract result:", [(t, round(avg_conf,2)) for t, c in zip(found, [avg_conf]*len(found))])

        missing = list(TARGET_KEYWORDS - set(found))
        if not missing:
            print("Textract PASS\n")
            return {
                "statusCode": 200,
                "body": {
                    "submissionId": event.get("submissionId", ""),
                    "avg_confidence": round(avg_conf, 2),
                    "engine": "Textract",
                    "keywordDetected": list(found),
                    "status": "accepted",
                    "missing_words": []
                }
            }
        else:
            print("Keywords missing:", missing)
            return {
                "statusCode": 200,
                "body": {
                    "submissionId": event.get("submissionId", ""),
                    "avg_confidence": round(avg_conf, 2),
                    "engine": "Textract",
                    "keywordDetected": list(found),
                    "status": "failed",
                    "missing_words": missing
                }
            }
    except Exception as e:
        print("Textract error:", str(e))
        return {
            "statusCode": 500,
            "body": {"error": "Textract failed"}
        }

if __name__ == "__main__":
    test_event = {"submissionId": "sub-123"} #test local
    result = lambda_handler(test_event, None)
    print("\nFINAL RESULT:")
    print(json.dumps(result, indent=4))
