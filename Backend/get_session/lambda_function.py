from app import response, get_sessions_table

def lambda_handler(event, context):
    try:
        path_params = event.get("pathParameters") or {}
        session_id = str(path_params.get("sessionId", "")).strip().upper()
        if not session_id:
            return response(400, {"message": "sessionId path parameter is required."})
        result = get_sessions_table().get_item(Key={"sessionId": session_id}, ConsistentRead=True)
        session = result.get("Item")
        if not session:
            return response(404, {"message": "Session not found."})
        return response(200, {"session": session})
    except Exception as exc:
        print("GetSession error:", exc)
        return response(500, {"message": "Unable to retrieve session."})
