# Multiplayer Game Session Management Platform

**Author:** Santhosh Kumar  
**Cloud stack:** Amazon S3, API Gateway, AWS Lambda, DynamoDB, SQS, SNS

A serverless session/lobby management demo. Players can create a room, join an existing session, view its players and status, and receive event notifications through an asynchronous SQS → Lambda → SNS workflow.

> This repository is a reproducible implementation of the project described in the report. Replace placeholders with your own AWS account resources before deployment. Never commit AWS access keys, secret keys, account-specific credentials, or private email addresses.

## Architecture

```text
Browser
  |
  v
Amazon S3 (static HTML/CSS/JS)
  |
  v
Amazon API Gateway (REST API)
  | POST /sessions       | POST /sessions/join       | GET /sessions/{sessionId}
  v                      v                           v
CreateSession Lambda   JoinSession Lambda           GetSession Lambda
  |                      |                           |
  +----------------------+---------------------------+
                         |
                         v
                  DynamoDB GameSessions
                  DynamoDB GameRooms
                         |
                  Session event message
                         v
                  Amazon SQS GameEventsQueue
                         |
                         v
                 ProcessGameEvent Lambda
                         |
                         v
                 Amazon SNS GameSessionNotifications
                         |
                         v
                 Email subscribers
```

## Repository layout

```text
frontend/
  index.html
  styles.css
  app.js
backend/
  create_session/
    lambda_function.py
  join_session/
    lambda_function.py
  get_session/
    lambda_function.py
  process_game_event/
    lambda_function.py
  common/
    app.py
docs/
  architecture.md
  deployment.md
```

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/sessions` | Create a game session |
| POST | `/sessions/join` | Join a session |
| GET | `/sessions/{sessionId}` | Get session details |

Example create request:
```json
{"host":"Santhosh","maxPlayers":4}
```

Example join request:
```json
{"sessionId":"YOUR_SESSION_ID","playerName":"Player2"}
```

## AWS resources to create

1. DynamoDB table `GameSessions`, partition key `sessionId` (String).
2. DynamoDB table `GameRooms`, partition key `room_id` (String).
3. SQS queue `GameEventsQueue` (recommended: also create a dead-letter queue).
4. SNS topic `GameSessionNotifications`; add and confirm an email subscription.
5. Four Lambda functions using Python 3.12 or a currently supported Python runtime:
   - `CreateSession`
   - `JoinSession`
   - `GetSession`
   - `ProcessGameEvent`
6. API Gateway routes listed above, with Lambda proxy integration and CORS enabled.
7. An SQS event source mapping from `GameEventsQueue` to `ProcessGameEvent`.
8. An S3 bucket configured for static website hosting, containing the `frontend/` files.

## Lambda environment variables

| Function | Variables |
|---|---|
| CreateSession | `SESSIONS_TABLE=GameSessions`, `ROOMS_TABLE=GameRooms`, `EVENTS_QUEUE_URL=<queue-url>` |
| JoinSession | `SESSIONS_TABLE=GameSessions`, `EVENTS_QUEUE_URL=<queue-url>` |
| GetSession | `SESSIONS_TABLE=GameSessions` |
| ProcessGameEvent | `SNS_TOPIC_ARN=<topic-arn>` |

## IAM permissions

Use a separate least-privilege execution role for each function:
- CreateSession: `dynamodb:PutItem` on both tables; `sqs:SendMessage` on the event queue.
- JoinSession: `dynamodb:GetItem`, `dynamodb:UpdateItem`; `sqs:SendMessage` on the event queue.
- GetSession: `dynamodb:GetItem` on `GameSessions`.
- ProcessGameEvent: `sns:Publish` on the notification topic; allow Lambda to read/delete messages from the SQS queue using the standard SQS event-source permissions.

Also attach the basic Lambda logging policy to each function. Do not use administrator permissions in a production deployment.

## Configure the frontend

Open `frontend/app.js` and replace:
```js
const API_BASE_URL = "PASTE_API_GATEWAY_INVOKE_URL_HERE";
```
with your deployed API Gateway invoke URL, for example `https://xxxx.execute-api.ap-south-1.amazonaws.com/prod` (use your own URL).

Upload the three frontend files to the S3 bucket. Enable static website hosting and allow public read only if you intentionally want a public demo. For a real deployment, put CloudFront in front of a private S3 origin.

## Test

1. Open the S3 website endpoint.
2. Create a room with a host name and maximum player count.
3. Copy the generated session ID.
4. Join from another browser/device using that ID.
5. Refresh session details and confirm player count/status.
6. Check SQS messages and the Lambda logs.
7. Confirm the SNS email subscription and check for `SESSION_CREATED` / `PLAYER_JOINED` notifications.

## Important notes

- This is a session/lobby manager, not a real-time game engine.
- The sample uses a simple `WAITING` status. Add authenticated users, expiration/TTL, rate limiting, stronger validation, and explicit status transitions before production use.
- API Gateway CORS must allow your S3 website origin and the required methods/headers.
- Configure a queue redrive policy and alarms for production.
