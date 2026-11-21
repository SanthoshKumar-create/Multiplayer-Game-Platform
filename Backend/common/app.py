import base64
import json
import os
import uuid
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN", "*"),
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
        },
        "body": json.dumps(body, default=str)
    }

def parse_body(event):
    raw = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    return json.loads(raw)

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def send_event(event_type, session_id, details=None):
    queue_url = os.environ["EVENTS_QUEUE_URL"]
    message = {
        "eventType": event_type,
        "sessionId": session_id,
        "occurredAt": now_iso(),
        "details": details or {}
    }
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))

def get_sessions_table():
    return dynamodb.Table(os.environ.get("SESSIONS_TABLE", "GameSessions"))
