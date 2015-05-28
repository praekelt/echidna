import sys
import json

import pika


struct = {'content_type': 'post'}
connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='echidna',
                         type='fanout')
message = ' '.join(sys.argv[1:]) or json.dumps(struct)

channel.basic_publish(exchange='echidna',
                      routing_key='',
                      body=message)
print " [x] Sent %r" % (message,)
connection.close()
