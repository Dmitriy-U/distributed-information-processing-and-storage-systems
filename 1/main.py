import zmq
import json

from helpers import get_ranges_by_number_of_workers


context = zmq.Context()

sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:5557")

sink = context.socket(zmq.PUSH)
sink.connect("tcp://localhost:5558")

prime_range_start = int(input("Input minimum digit of searching prime digits range start: "))
prime_range_end = int(input("Input minimum digit of searching prime digits range end: "))
number_of_workers = int(input("Input the number of workers: "))

tasks = get_ranges_by_number_of_workers(number_of_workers, prime_range_start, prime_range_end)

print("Press Enter when the workers are ready:")
_ = input()
print("Sending tasks to workers...")

sink.send(b'0')

for task in tasks:
    print(task)
    sender.send_string(json.dumps(task))

# TODO: Finish it (receive result)
