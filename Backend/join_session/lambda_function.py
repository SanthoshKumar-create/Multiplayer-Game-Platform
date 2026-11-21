from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
from app import response, parse_body, send_event, get_sessions_table

def lambda_handler(event, context):
    try:
        body = parse_body(event)
        session_id = str(body.get("sessionId", "")).strip().upper()
        player_name = str(body.get("playerName", "")).strip()
        if not session_id or not player_name or len(player_name) > 30:
            return response(400, {"message": "sessionId and playerName are required (name max 30 characters)."})

        table = get_sessions_table()
        # Conditional update protects against duplicate names and overfilling the room.
        try:
            table.update_item(
                Key={"sessionId": session_id},
                UpdateExpression="SET players = list_append(if_not_exists(players, :empty), :new_player), playerCount = if_not_exists(playerCount, :zero) + :one",
                ConditionExpression=(
                    "attribute_exists(sessionId) AND #st = :waiting "
                    "AND (attribute_not_exists(players) OR NOT contains(players, :player_name)) "
                    "AND (attribute_not_exists(playerCount) OR playerCount < maxPlayers)"
                ),
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={
                    ":empty": [], ":new_player": [player_name], ":zero": 0, ":one": 1,
                    ":waiting": "WAITING", ":player_name": player_name
                },
                ReturnValues="ALL_NEW"
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code == "ConditionalCheckFailedException":
                existing = table.get_item(Key={"sessionId": session_id}).get("Item")
                if not existing:
                    return response(404, {"message": "Session not found."})
                if player_name in existing.get("players", []):
                    return response(409, {"message": "That player name is already in this session."})
                return response(409, {"message": "Session is full or no longer accepting players."})
            raise

        session = table.get_item(Key={"sessionId": session_id}, ConsistentRead=True).get("Item")
        send_event("PLAYER_JOINED", session_id, {"playerName": player_name})
        return response(200, {"message": "Joined session successfully.", "session": session})
    except Exception as exc:
        print("JoinSession error:", exc)
        return response(500, {"message": "Unable to join session."})
