# Architecture and request flow

## Components
- **Amazon S3:** stores and serves the browser frontend.
- **Amazon API Gateway:** exposes HTTPS endpoints to the frontend.
- **AWS Lambda:** handles create, join, read, and asynchronous event-processing logic.
- **Amazon DynamoDB:** stores game session and room records.
- **Amazon SQS:** buffers session events so notification processing is decoupled from user requests.
- **Amazon SNS:** distributes session-created and player-joined notifications to email subscribers.

## Main flows
1. **Create:** Browser → API Gateway → CreateSession Lambda → DynamoDB; Lambda sends `SESSION_CREATED` to SQS.
2. **Join:** Browser → API Gateway → JoinSession Lambda → conditional DynamoDB update; Lambda sends `PLAYER_JOINED` to SQS.
3. **Read:** Browser → API Gateway → GetSession Lambda → DynamoDB → browser renders session details.
4. **Notify:** SQS → ProcessGameEvent Lambda → SNS topic → confirmed email subscribers.

## DynamoDB fields
`GameSessions` partition key: `sessionId` (String). Sample attributes: `host`, `players` (String list), `playerCount` (Number), `maxPlayers` (Number), `status` (String), `createdAt` (String).

`GameRooms` partition key: `room_id` (String). This sample stores a room reference and basic room metadata.

## Scope
This project manages game rooms and lobby sessions. It does not implement the actual multiplayer game engine, real-time gameplay transport, voice chat, ranking matchmaking, or payments.
