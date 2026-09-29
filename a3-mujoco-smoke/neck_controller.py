import argparse
import pathlib
import time
import urllib.request


URL = (
    "http://127.0.0.1:50080/channel/"
    "%2Fsim%2Fa3%2Fneck_joint_command/"
    "pb%3Aaimrt.protocols.sensor.JointCommandArray"
)
PERIOD_SECONDS = 0.02


def post(payload: bytes) -> None:
    request = urllib.request.Request(
        URL,
        data=payload,
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=1) as response:
        if response.status != 200:
            raise RuntimeError(f"unexpected HTTP status: {response.status}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Hold the A3 MuJoCo neck smoke-test target.")
    parser.add_argument(
        "--duration",
        type=float,
        default=20.0,
        help="seconds to hold; use 0 to run until interrupted",
    )
    args = parser.parse_args()
    if args.duration < 0:
        parser.error("--duration must be non-negative")

    base_path = pathlib.Path(__file__).resolve().parent
    command = (base_path / "neck-command.json").read_bytes()
    release = (base_path / "neck-release.json").read_bytes()
    deadline = None if args.duration == 0 else time.monotonic() + args.duration

    try:
        while deadline is None or time.monotonic() < deadline:
            started_at = time.monotonic()
            post(command)
            time.sleep(max(0.0, PERIOD_SECONDS - (time.monotonic() - started_at)))
    finally:
        for _ in range(3):
            post(release)


if __name__ == "__main__":
    main()
