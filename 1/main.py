import zmq
import json

from helpers import get_ranges_by_number_of_workers


context = zmq.Context()

sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:9000")

receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:9100")

prime_range_start = int(input("Input minimum digit of searching prime digits range start: "))
prime_range_end = int(input("Input minimum digit of searching prime digits range end: "))
number_of_workers = int(input("Input the number of workers: "))

tasks = get_ranges_by_number_of_workers(number_of_workers, prime_range_start, prime_range_end)

print("Press Enter when the workers are ready:")
_ = input()
print("Sending tasks to workers...")

for task in tasks:
    sender.send_string(json.dumps(task))

print("Receiving results from workers...")

result = []
for task in tasks:
    reseived_task_result: list = json.loads(receiver.recv())
    result = result + reseived_task_result

result = sorted(result)

sender.close()
receiver.close()

print('Result: ', result)
print('Finish')
