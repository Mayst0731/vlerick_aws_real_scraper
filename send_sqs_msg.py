"""Send ceeb code and url to a queue an trigger lambda function"""
import boto3


def send_message(queue_name):
    """Send message to a queue"""
    # Get the service resource
    sqs = boto3.resource('sqs')
    # Get the queue. This returns an SQS.Queue instance
    queue = sqs.get_queue_by_name(QueueName='Vlerick-startURL')
    # Edit message body
    msg = {"3399_EUR": "https://www.vlerick.com/en/programmes/management-programmes"}
    str_msg = str(msg)
    # Create a new message
    response = queue.send_message(MessageBody=str_msg)
    return
