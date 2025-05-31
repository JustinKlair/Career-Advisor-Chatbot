import json
import logging
import boto3
import time
import uuid
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# Convert Decimal to float for JSON responses
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
chat_table = dynamodb.Table('CareerAdvisorChats')
session_index_table = dynamodb.Table('CareerAdvisorSessionIndex')

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    method = event.get('requestContext', {}).get('http', {}).get('method') or event.get('requestContext', {}).get('httpMethod', '')
    path = event.get('rawPath') or event.get('path', '')

    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'message': 'CORS preflight successful'})
        }

    try:
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        query_params = event.get('queryStringParameters') or {}

        session_id = (
            body.get('sessionId') or
            query_params.get('sessionId') or
            None
        )

    except Exception as e:
        logger.error(f"Error parsing body or sessionId: {e}")
        return error_response(400, 'Invalid request body')

    if method == 'GET':
        if path.endswith('/sessions'):
            try:
                response = session_index_table.scan()
                sessions = [
                    {
                        'sessionId': item['sessionId'],
                        'title': item.get('title', ''),
                        'createdAt': item.get('createdAt', 0)
                    }
                    for item in response.get('Items', [])
                ]
                return {
                    'statusCode': 200,
                    'headers': cors_headers(),
                    'body': json.dumps({'sessions': sessions}, cls=DecimalEncoder)
                }
            except Exception as e:
                logger.error(f"Failed to retrieve session list: {e}")
                return error_response(500, 'Failed to retrieve session list')

        # Default GET: return messages for one session
        if not session_id:
            return error_response(400, 'Missing sessionId for chat history request')

        try:
            response = chat_table.query(
                KeyConditionExpression=Key('sessionId').eq(session_id),
                ScanIndexForward=True
            )
            items = response.get('Items', [])
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({'history': items}, cls=DecimalEncoder)
            }
        except Exception as e:
            logger.error(f"Failed to retrieve chat history: {e}")
            return error_response(500, 'Failed to retrieve chat history')

    if method == 'POST':
        if not session_id:
            session_id = str(uuid.uuid4())

        user_message = body.get('message', '').lower()
        timestamp = int(time.time())

        if "developer" in user_message:
            ai_reply = "That's great! Software development is in high demand."
        elif "designer" in user_message:
            ai_reply = "Designers have a unique eye for visuals — it's a creative and growing field."
        elif "help" in user_message:
            ai_reply = "I'm here to guide you. What career interests you?"
        else:
            ai_reply = "Sorry, I didn't understand that. Try asking about a career!"

        try:
            chat_table.put_item(Item={
                'sessionId': session_id,
                'timestamp': timestamp,
                'type': 'user',
                'content': user_message
            })

            chat_table.put_item(Item={
                'sessionId': session_id,
                'timestamp': timestamp + 1,
                'type': 'ai',
                'content': ai_reply
            })

            session_index_table.put_item(
                Item={
                    'sessionId': session_id,
                    'title': user_message[:50] or 'New Session',
                    'createdAt': timestamp
                },
                ConditionExpression='attribute_not_exists(sessionId)'
            )

        except session_index_table.meta.client.exceptions.ConditionalCheckFailedException:
            logger.info(f"Session {session_id} already exists in index. Skipping insert.")
        except Exception as e:
            logger.error(f"Failed to write to DynamoDB: {e}")

        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'reply': f"Career Advisor says: {ai_reply}",
                'sessionId': session_id
            })
        }

    if method == 'DELETE':
        if path.endswith('/sessions'):
            # DELETE /careerchat/sessions: delete all sessions and messages
            try:
                # Delete all messages
                all_messages = chat_table.scan().get('Items', [])
                with chat_table.batch_writer() as batch:
                    for item in all_messages:
                        batch.delete_item(Key={
                            'sessionId': item['sessionId'],
                            'timestamp': item['timestamp']
                        })

                # Delete all sessions
                all_sessions = session_index_table.scan().get('Items', [])
                with session_index_table.batch_writer() as batch:
                    for item in all_sessions:
                        batch.delete_item(Key={'sessionId': item['sessionId']})

                return {
                    'statusCode': 200,
                    'headers': cors_headers(),
                    'body': json.dumps({'message': 'All chat history deleted'})
                }

            except Exception as e:
                logger.error(f"Failed to delete all chat history: {e}")
                return error_response(500, 'Failed to delete all chat history')

        elif path.endswith('/clear-all'):
            # Backward compatibility
            return {
                'statusCode': 301,
                'headers': {
                    **cors_headers(),
                    'Location': '/careerchat/sessions'
                },
                'body': json.dumps({'message': 'Use DELETE /careerchat/sessions instead'})
            }

        # Otherwise, delete a single session by sessionId
        if not session_id:
            return error_response(400, 'Missing sessionId for delete request')

        try:
            messages = chat_table.query(
                KeyConditionExpression=Key('sessionId').eq(session_id)
            ).get('Items', [])

            with chat_table.batch_writer() as batch:
                for item in messages:
                    batch.delete_item(Key={
                        'sessionId': item['sessionId'],
                        'timestamp': item['timestamp']
                    })

            session_index_table.delete_item(Key={'sessionId': session_id})

            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({'message': 'Chat session deleted successfully'})
            }

        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return error_response(500, 'Failed to delete chat history')

    return error_response(405, 'Method not allowed')

def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE',
        'Content-Type': 'application/json'
    }

def error_response(status, message):
    return {
        'statusCode': status,
        'headers': cors_headers(),
        'body': json.dumps({'error': message})
    }
