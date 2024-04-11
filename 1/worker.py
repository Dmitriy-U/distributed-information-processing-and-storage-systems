import zmq
import json

from helpers import get_prime_numbers


context = zmq.Context()

receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:9000")

sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:9100")

print("Worker are ready")

while True:
    range_start, range_end = json.loads(receiver.recv())
    
    result = get_prime_numbers(range_start, range_end)
    print('Has result: ',result)
    sender.send_string(json.dumps(result))
    print('Sended -->')
