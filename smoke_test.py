"""Verify readiness AND the deployed build, not merely an old healthy instance."""

import argparse
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def check(url, expected_version, attempts=30, interval=10):
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(url.rstrip("/") + "/health", timeout=10) as response:
                assert json.load(response) == {"status": "ok"}, "Unexpected health response"
            with urlopen(url.rstrip("/") + "/version", timeout=10) as response:
                actual = json.load(response).get("version")
            if actual != expected_version:
                raise AssertionError(f"Expected build {expected_version}, received {actual}")
            print(f"PASS: {url} is healthy and running build {expected_version}")
            return
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, AssertionError) as error:
            print(f"Attempt {attempt}/{attempts}: {error}", flush=True)
            if attempt < attempts:
                time.sleep(interval)
    raise SystemExit("FAIL: expected build did not become healthy")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--attempts", type=int, default=30)
    parser.add_argument("--interval", type=float, default=10)
    args = parser.parse_args()
    if args.attempts < 1 or args.interval < 0:
        parser.error("attempts must be positive; interval must be nonnegative")
    check(args.url, args.expected_version, args.attempts, args.interval)
