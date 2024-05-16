import subprocess


def get_disk_usage(parameters: str):
    #command = "df -h " + parameters
    command = ["df", "-h"]
    if parameters:
        command.extend(parameters.split())

    try:
        # result = subprocess.run(
        #     command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        # )
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        usage = result.stdout.strip().decode()
    except:
        raise Exception("An unexpected error was observed")

    return usage
