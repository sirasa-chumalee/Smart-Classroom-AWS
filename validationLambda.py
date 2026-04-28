import boto3
import json
from decimal import Decimal


rekognition_client = boto3.client('rekognition')
textract_client = boto3.client('textract')
s3_client = boto3.client('s3')
dynamodb = boto3.resource("dynamodb")


LAB_TABLE = "Lab"
lab_table = dynamodb.Table(LAB_TABLE)


SUBMISSION_TABLE = "Submission"
submission_table = dynamodb.Table(SUBMISSION_TABLE)




def normalize(text):
    return text.lower().replace(" ", "")




def find_keywords(text_items, target_keywords, min_confidence):
    found_keywords = set()
    confidences = []


    for text, confidence in text_items:
        if confidence < min_confidence:
            continue


        normalized = normalize(text)


        for kw in target_keywords:
            if kw in normalized:
                found_keywords.add(kw)
                confidences.append(confidence)


    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    return found_keywords, avg_conf




def run_rekognition(image_bytes, target_keywords, min_confidence):
    response = rekognition_client.detect_text(Image={"Bytes": image_bytes})


    text_items = [
        (t["DetectedText"], t["Confidence"])
        for t in response.get("TextDetections", [])
    ]


    return find_keywords(text_items, target_keywords, min_confidence)




def run_textract(image_bytes, target_keywords, min_confidence):
    response = textract_client.detect_document_text(
        Document={"Bytes": image_bytes}
    )


    text_items = [
        (block["Text"], block["Confidence"])
        for block in response.get("Blocks", [])
        if block["BlockType"] == "LINE"
    ]


    return find_keywords(text_items, target_keywords, min_confidence)




def save_submission_result(lab_id, submission_id, engine, avg_conf, status, keywords_detected, missing):
    submission_table.put_item(
        Item={
            "labId": lab_id,
            "submissionId": submission_id,
            "engine": engine,
            "avgConfidence": Decimal(str(round(avg_conf, 2))),
            "status": status,
            "keywordsDetected": list(keywords_detected),
            "missingWords": list(missing)
        }
    )




def lambda_handler(event, context):


    # Detect if this is S3 trigger or API Gateway
    if "Records" in event:  # S3 trigger
        record = event["Records"][0]
        bucket_name = record["s3"]["bucket"]["name"]
        image_key = record["s3"]["object"]["key"]
    else:  # API Gateway
        body = json.loads(event.get("body", "{}"))
        bucket_name = body["bucket"]
        image_key = body["key"]


    parts = image_key.split("/")
    lab_id = parts[1]
    submission_id = parts[3]


    print("Processing:", image_key)


    lab_response = lab_table.get_item(Key={"labId": lab_id})


    if "Item" not in lab_response:
        print("Lab not found:", lab_id)
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Lab not found"})
        }


    lab = lab_response["Item"]


    target_keywords = set(normalize(k) for k in lab.get("keywords", []))
    min_confidence = lab.get("minConfidence", 50)


    print("Keywords:", target_keywords)
    print("Min confidence:", min_confidence)


    # Get image from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=image_key)
    image_bytes = response["Body"].read()


    # --- Run Rekognition ---
    try:
        found, avg_conf = run_rekognition(image_bytes, target_keywords, min_confidence)
        if target_keywords.issubset(found):
            status = "accepted"
            save_submission_result(lab_id, submission_id, "Rekognition", avg_conf, status, found, [])
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "labId": lab_id,
                    "submissionId": submission_id,
                    "avg_confidence": round(avg_conf, 2),
                    "engine": "Rekognition",
                    "keywordDetected": list(found),
                    "status": status,
                    "missing_words": []
                })
            }
    except Exception as e:
        print("Rekognition failed:", str(e))


    # --- Textract fallback ---
    try:
        found, avg_conf = run_textract(image_bytes, target_keywords, min_confidence)
        missing = list(target_keywords - found)
        status = "accepted" if not missing else "failed"
        save_submission_result(lab_id, submission_id, "Textract", avg_conf, status, found, missing)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "labId": lab_id,
                "submissionId": submission_id,
                "avg_confidence": round(avg_conf, 2),
                "engine": "Textract",
                "keywordDetected": list(found),
                "status": status,
                "missing_words": missing
            })
        }
    except Exception as e:
        print("Textract error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Processing failed"})
        }
