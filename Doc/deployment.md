# Deployment checklist

## 1. DynamoDB
Create on-demand tables:
- `GameSessions`, partition key `sessionId` (String)
- `GameRooms`, partition key `room_id` (String)

## 2. SQS and SNS
Create an SNS standard topic named `GameSessionNotifications`, subscribe an email address and confirm the subscription. Create an SQS standard queue named `GameEventsQueue`. Copy the queue URL and SNS topic ARN.

## 3. Lambda packaging
For each Lambda function, package its handler file together with `backend/common/app.py` at the ZIP root (rename/copy `app.py` beside `lambda_function.py`). Include `boto3` only if your chosen runtime/package strategy requires it; Lambda Python runtimes include boto3, but pin dependencies in a controlled deployment for production.

Set handler to `lambda_function.lambda_handler`. Set environment variables from the root README.

For the first three functions, add `backend/common` to the deployment ZIP as `app.py` at the root. The process-event function does not need the common module.

## 4. IAM
Create dedicated roles. Add only the DynamoDB and SQS/SNS actions described in README. Add CloudWatch Logs permissions.

## 5. API Gateway
Create a REST API and Lambda proxy integrations:
- `POST /sessions` → CreateSession
- `POST /sessions/join` → JoinSession
- `GET /sessions/{sessionId}` → GetSession

Deploy to a stage such as `prod`. Enable CORS for the frontend origin and allow `GET,POST,OPTIONS` and `Content-Type`. Add Lambda invoke permissions for API Gateway.

## 6. SQS trigger
Add `GameEventsQueue` as an event source for ProcessGameEvent. Enable `ReportBatchItemFailures` (partial batch response). Set a visibility timeout longer than the Lambda timeout and configure a dead-letter queue/redrive policy.

## 7. S3 frontend
Edit `frontend/app.js` and set `API_BASE_URL` to the deployed API Gateway stage URL. Upload `index.html`, `styles.css`, and `app.js` to an S3 bucket. Enable static website hosting. For a portfolio demo, configure read access deliberately; for production, use CloudFront with a private S3 origin.

## 8. Validate
Create a session, join with a second player, retrieve session details, verify DynamoDB items, inspect SQS/Lambda logs, and confirm SNS email notifications.

## 9. GitHub
Create a public repository, upload the project files, and add screenshots with account IDs, email addresses, API keys, and other personal data hidden. Never upload `.env` files or AWS credentials.
