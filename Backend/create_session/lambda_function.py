import os
import uuid
from datetime import datetime, timezone

from botocore.exceptions import ClientError
from app import response, parse_body, send_event, get_sessions_table
import boto3

dynamodb = boto3.resource("dynamodb")

def lambda_handler(event, context):
    try:
        body = parse_body(event)
        host = str(body.get("host", "")).strip()
        max_players = int(body.get("maxPlayers", 4))
        if not host or len(host) > 30:
            return response(400, {"message": "Host name is required (maximum 30 characters)."})
        if max_players < 2 or max_players > 8:
            return response(400, {"message": "maxPlayers must be between 2 and 8."})

        session_id = uuid.uuid4().hex[:8].upper()
        created_at = datetime.now(timezone.utc).isoformat()
        item = {
            "sessionId": session_id,
            "host": host,
            "players": [host],
            "playerCount": 1,
            "maxPlayers": max_players,
            "status": "WAITING",
            "createdAt": created_at
        }
        get_sessions_table().put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(sessionId)"
        )

        rooms_table_name = os.environ.get("ROOMS_TABLE", "GameRooms")
        dynamodb.Table(rooms_table_name).put_item(Item={
            "room_id": session_id,
            "sessionId": session_id,
            "host": host,
            "status": "WAITING",
            "createdAt": created_at
        })
        send_event("SESSION_CREATED", session_id, {"host": host, "maxPlayers": max_players})
        return response(201, {"message": "Session created successfully.", "session": item})
    except (ValueError, TypeError):
        return response(400, {"message": "Invalid request. Check maxPlayers."})
    except ClientError as exc:
        print("CreateSession AWS error:", exc)
        return response(500, {"message": "Unable to create session."})
    except Exception as exc:
        print("CreateSession error:", exc)
        return response(500, {"message": "Internal server error."})
