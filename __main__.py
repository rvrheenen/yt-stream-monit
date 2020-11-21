import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import requests
import json
import time
from typing import List, Tuple


def main():
    fail_limit, sleep_time = get_runtime_vars()
    results = [0] * int(fail_limit)
    while True:
        return_code = check_stream()
        results = process_results(results, return_code)

        time.sleep(sleep_time)


def get_runtime_vars() -> Tuple[int, int]:
    fail_limit = int(os.getenv("AMOUNT_OF_FAILS_BEFORE_NOTIFICATION"))
    if fail_limit == None:
        fail_limit = 1

    sleep_time = int(os.getenv("SLEEP_TIME"))
    if sleep_time == None:
        sleep_time = 5

    return fail_limit, sleep_time


def check_stream():
    # path of this script
    script_path = Path(os.path.abspath(__file__))
    script_folder_path = script_path.parent

    check_stream_script = f'{script_folder_path.joinpath(("check_stream.sh"))} -y {os.getenv("YOUTUBE_URL")}'

    encode_process = subprocess.Popen(
        check_stream_script,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )

    stdout, stderr = encode_process.communicate()

    return_code = encode_process.returncode

    return return_code


def process_results(results: List[int], return_code: int) -> List[int]:
    results.append(return_code)
    results = results[1:]

    time_tag = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if all(results):
        print(f"[{time_tag}] [ERROR] Stream is down!!!!")
        res = post_message_to_slack(f"[{time_tag}] Stream is down!")
        if not res["ok"]:
            print("  FAILED TO SEND TO SLACK!!!!")
            print("  REASON: ", res["error"])
        else:
            print("  SENT TO SLACK!")
    elif any(results) and results[-1]:
        fails = len(results) - results.count(0)
        print(
            f"[{time_tag}] [WARNING] {fails}/{len(results)} of recent checks failed."
        )
    else:
        print(f"[{time_tag}] [OK] Stream is still up")

    return results


def post_message_to_slack(text: str, blocks: List = None):
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': os.getenv("SLACK_TOKEN"),
        'channel': os.getenv("SLACK_CHANNEL"),
        'text': text,
        'icon_url': os.getenv("SLACK_ICON_URL"),
        'username': os.getenv("SLACK_USER_NAME"),
        'blocks': json.dumps(blocks) if blocks else None
    }).json()


if __name__ == "__main__":
    load_dotenv()
    for var in ["YOUTUBE_URL", "SLACK_TOKEN", "SLACK_CHANNEL", "SLACK_USER_NAME"]:
        if os.getenv(var) == None:
            print(f"env var {var} not set")
            exit()
    main()
