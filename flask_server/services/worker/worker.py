#!/usr/bin/env python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')

def getWinner(game_status):
    keys = list(game_status)
    values = list(game_status.values())

    if values[0] == values[1]:
        return "draw"
    
    if values[0] == "rock" and values[1] == "scissors":
        return keys[0]
    elif values[0] == "paper" and values[1] == "rock":
        return keys[0]
    elif values[0] == "scissors" and values[1] == "paper":
        return keys[0]
    else:
        return keys[1]

def on_request(ch, method, props, body):
    decoded_body = body.decode('utf-8')
    
    json_acceptable_string = decoded_body.replace("'", "\"")
    data = json.loads(json_acceptable_string)
    
    print("received data: {}, calculating...".format(data))
    response = getWinner(data)
    print("sending back data: {}".format(response))

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()