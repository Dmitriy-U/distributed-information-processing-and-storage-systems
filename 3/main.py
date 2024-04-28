from helpers import Command, handle_command, parse_args, run_storage

 
if __name__ == "__main__":
    args = parse_args()
    command = args[0]

    if command == Command.RUN.value:
        run_storage()
    else:
        handle_command(*args)
