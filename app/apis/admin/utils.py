import subprocess


def get_disk_usage(parameters: str):
    command = ["df", "-h"]  # Start with the base command
    if parameters:  # If additional parameters are provided, add them to the command list
        command.extend(parameters.split())

    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode != 0:  # Check if the command execution was successful
            raise Exception("An error occurred: " + result.stderr.decode())

        usage = result.stdout.strip().decode()
    except Exception as e:
        raise Exception("An unexpected error was observed: " + str(e))

    return usage
