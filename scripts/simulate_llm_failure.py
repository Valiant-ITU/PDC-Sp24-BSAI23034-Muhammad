import argparse
import time

import httpx


def _call_generate(base_url: str, prompt: str) -> None:
    started = time.time()
    try:
        response = httpx.post(
            f"{base_url}/generate",
            json={"prompt": prompt},
            timeout=5.0,
        )
        elapsed = time.time() - started
        student_id = response.headers.get("X-Student-ID", "missing")
        print(
            f"{response.status_code} in {elapsed:.2f}s X-Student-ID={student_id} -> "
            f"{response.json()}"
        )
    except Exception as exc:
        elapsed = time.time() - started
        print(f"error in {elapsed:.2f}s -> {exc}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--calls", type=int, default=6)
    args = parser.parse_args()

    for i in range(args.calls):
        _call_generate(args.base_url, f"demo-{i}")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
