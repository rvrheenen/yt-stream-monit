import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import requests
import json
import time


def main():
    while True:
        check_stream()
        time.sleep(5)


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

    time_tag = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if return_code > 0:
        print(f"[{time_tag}] [ERROR] Stream is down!!!!")
        res = post_message_to_slack(f"[{time_tag}] Stream is down!")
        if not res["ok"]:
            print("FAILED TO SEND TO SLACK!!!!")
            print("REASON: ", res["error"])
    else:
        print(f"[{time_tag}] [OK] Stream is still up")


def post_message_to_slack(text, blocks=None):
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
