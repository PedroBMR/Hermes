from pathlib import Path

import pyttsx3
import requests
import yaml

CONFIG_PATH = Path(__file__).with_name("config.yaml")


def load_config():
    """Load configuration values from config.yaml."""
    with CONFIG_PATH.open() as fh:
        return yaml.safe_load(fh)


def push_to_talk():
    """Simple push-to-talk simulation using console input."""
    input("Press Enter and start typing your idea (Ctrl+C to quit)...\n")
    return input("Idea: ")


def send_idea(cfg, text):
    server = cfg["server"].rstrip("/")
    headers = {
        "X-Token": cfg["token"],
        "X-Device-Id": cfg["device_id"],
    }
    payload = {"user": cfg["device_id"], "title": text[:30], "body": text}
    resp = requests.post(f"{server}/ideas", json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    expected_source = f"caduceu_{cfg['device_id']}"
    if data.get("source") != expected_source:
        raise ValueError(f"Unexpected source {data.get('source')}")
    return data


def ask_and_speak(cfg):
    server = cfg["server"].rstrip("/")
    headers = {
        "X-Token": cfg["token"],
        "X-Device-Id": cfg["device_id"],
    }
    prompt = input("Prompt to ask the server (leave empty to skip): ")
    if not prompt:
        return
    resp = requests.post(f"{server}/ask", json={"prompt": prompt}, headers=headers, timeout=30)
    resp.raise_for_status()
    answer = resp.json().get("response", "")
    if not answer:
        return
    engine = pyttsx3.init()
    engine.say(answer)
    engine.runAndWait()


def main():
    cfg = load_config()
    while True:
        try:
            text = push_to_talk()
            if not text.strip():
                continue
            send_idea(cfg, text)
            ask_and_speak(cfg)
        except KeyboardInterrupt:
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
