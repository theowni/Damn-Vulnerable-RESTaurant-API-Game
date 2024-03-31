import ast
import subprocess
from os import listdir
from os.path import isfile, join

from colorama import Fore, Style

BASE_PATH = "app"
TESTS_DIR = "tests/vulns/"
TEST_FILES_PATHS = sorted(
    [join(TESTS_DIR, f) for f in listdir(TESTS_DIR) if isfile(join(TESTS_DIR, f))]
)


def is_vulnerability_fixed(test_file_path):
    try:
        command = [
            "pytest",
            test_file_path,
            "--disable-warnings",
            "-qq",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return (
        result.returncode == 1
    )  # Tests were collected and run but some of the tests failed


def get_vuln_name(test_file_path):
    level_len = len("tests/vulns/level_")
    title_idx = test_file_path[level_len:].find("_") + 1
    return (
        test_file_path[level_len + title_idx :]
        .replace("_", " ")
        .replace(".py", "")
        .title()
    )


def get_level_number(test_file_path):
    level_len = len("tests/vulns/level_")
    number_idx = test_file_path[level_len:].find("_")
    return test_file_path[level_len : level_len + number_idx]


def get_level_title(test_file_path):
    level_number = get_level_number(test_file_path)
    vuln_name = get_vuln_name(test_file_path)

    return f"Level {level_number} - {vuln_name}"


def print_level_description(test_file_path):
    level_title = get_level_title(test_file_path)
    with open(test_file_path, "r") as source_file:
        source_code = source_file.read()
    tree = ast.parse(source_code)

    level_description = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            level_description = ast.get_docstring(node)

    if not level_description:
        raise Exception("No hints provided!")

    print(level_title, end="\n\n")
    print(level_description, end="\n\n")

    full_test_file_path = join(BASE_PATH, test_file_path)
    print(
        f"Test file confirming the vulnerability:\n    {full_test_file_path}",
        end="\n\n\n",
    )


def print_welcome_screen():
    print(Fore.GREEN, end="")
    print(
        """
            Welcome to Damn Vulnerable Restaurant!

            Our restaurant was recently attacked by unknown threat actor!
            The restaurant's API and underlying system were compromised by 
            exploiting various security vulnerabilities.

            The owner of the restaurant - Mysterious Chef wants you to
            investigate how it happened and fix the vulnerabilities.
            Chef suspects that attackers were associated with the newly opened
            restaurant located across the street.

            The attackers left tests confirming the exploits that they
            used to gain access to the system. You can read these tests
            to understand the vulnerability better but don't modify them.

            Your task is to fix the vulnerabilities to make sure that those
            malicious tests are no longer passing. In next steps, you will
            get vulnerability hints left by the attackers.
            Use those hints to implement fixes.
        """,
        end="\n\n",
    )
    print(Style.RESET_ALL, end="")


def print_congrats_screen():
    print(Fore.GREEN, end="")
    print(
        """
            Congratulations! Great Work!

            You were able to fix all of the vulnerabilities exploited 
            during the attack!

            However, we are aware about other vulnerabilities in the system.
            Also, there is one more vulnerability that allows to execute 
            commands on the server as a root user but you need to find it
            on your own :)


            If you enjoyed this challenge, please contact the repository owner
            and leave the feedback. You can find the contact at devsec-blog.com.

            And remember... these vulnerabilities were implemented and provided
            to you for learning purposes, don't use this knowledge to attack
            services that you don't own or you don't have permissions
            to do that.
            With great power comes great responsibility.
        """
    )
    print(Style.RESET_ALL, end="")


def press_key_to_continue(text, color=Fore.YELLOW, end="\n"):
    print(color, end="")
    input(text + end)
    print(Style.RESET_ALL, end="")


def print_color_text(text, color, end="\n"):
    print(color, end="")
    print(text, end=end)
    print(Style.RESET_ALL, end="")


def move_cursor_top(lines=1):
    for line in range(lines):
        print("\033[1A\033[K", end="")


print_welcome_screen()
press_key_to_continue("Click any key to continue...", end="\n\n")

for i, level_test_file in enumerate(TEST_FILES_PATHS, start=1):
    vuln_name = get_vuln_name(level_test_file)
    is_fixed = is_vulnerability_fixed(level_test_file)

    if is_fixed:
        print_color_text(
            f"Congratulations! You fixed the {vuln_name} vulnerability!",
            color=Fore.GREEN,
            end="\n",
        )
    else:
        print_level_description(level_test_file)

        if not is_fixed:
            press_key_to_continue(
                "Fix the vulnerability and press any key to validate the fix...",
                end="\r\r",
            )
            move_cursor_top()

        while not is_fixed:
            is_fixed = is_vulnerability_fixed(level_test_file)
            if not is_fixed:
                press_key_to_continue(
                    """Unfortunately, the vulnerability is not fixed yet.
Fix the vulnerability and press any key to validate the fix...""",
                    end="\r\r",
                )
                move_cursor_top(2)

        print_color_text(
            f"Congratulations! You fixed the {vuln_name} vulnerability!",
            color=Fore.GREEN,
            end="\n\n",
        )
        press_key_to_continue("Click any key to continue...", end="\n\n")

    if i == len(TEST_FILES_PATHS):
        print_congrats_screen()
