import json
import os
import boto3

sns = boto3.client("sns")

def lambda_handler(event, context):
    topic_arn = os.environ["SNS_TOPIC_ARN"]
    batch_failures = []

    for record in event.get("Records", []):
        message_id = record.get("messageId")
        try:
            payload = json.loads(record["body"])
            event_type = payload.get("eventType", "GAME_EVENT")
            session_id = payload.get("sessionId", "unknown")
            details = payload.get("details", {})
            subject = f"Game session update: {event_type}"[:100]
            message = (
                f"Event: {event_type}\n"
                f"Session ID: {session_id}\n"
                f"Occurred at: {payload.get('occurredAt', 'unknown')}\n"
                f"Details: {json.dumps(details)}"
            )
            sns.publish(TopicArn=topic_arn, Subject=subject, Message=message)
        except Exception as exc:
            print(f"Failed to process SQS message {message_id}: {exc}")
            batch_failures.append({"itemIdentifier": message_id})

    # Enable ReportBatchItemFailures on the SQS event source mapping.
    return {"batchItemFailures": batch_failures}
