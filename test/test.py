from concurrent.futures import ThreadPoolExecutor
import requests
import asyncio
from dotenv import load_dotenv
from os import environ
from pathlib import Path

load_dotenv()
ETHGLOBAL_API_KEY = environ.get("ETHGLOBAL_API_KEY")
API_URL = "http://localhost:8080/api/image"

type Fixtures = dict[str, tuple[bytes, list[bytes]]]


def load_test_fixtures() -> Fixtures:
    print("Loading test fixtures")
    fix = {}
    for file in Path("test/fixtures/input").glob("*"):
        print(f"  Loading {file.name}")
        input = open(file, "rb").read()
        output = [
            open(f, "rb").read()
            for f in Path("test/fixtures/output").glob(f"{file.stem}-*")
        ]
        fix[file.name] = (input, output)
    return fix


def test_auth():
    print("Running auth test")
    # No auth header
    response = requests.post(API_URL)
    assert response.status_code == 401

    # Invalid auth header
    headers = {"Authorization": "Bearer notavalidtoken"}
    response = requests.post(API_URL, headers=headers)
    assert response.status_code == 401


def test_image_output(fix: Fixtures):
    print("Running image output test")
    for name in fix:
        input, outputs = fix[name]
        print(f"  Testing fixture {name}")
        headers = {
            "Authorization": f"Bearer {ETHGLOBAL_API_KEY}",
            "Content-Type": "image/png",
        }
        response = requests.post(API_URL, headers=headers, data=input)
        assert response.status_code == 200
        # Differences in cpu architecture can cause the model to output slightly
        # different image files (e.g. running in docker vs local machine).
        # As long as the output image looks reasonable it is acceptable.
        # If this assertion is failing, please create a new output image fixture:
        with open(f"out.png", "wb") as f:
            f.write(response.content)
        assert any(response.content == img for img in outputs)


async def test_stress(fix: Fixtures):
    def post_image(idx: int):
        print(f"  Sending request #{idx} to {API_URL}")
        headers = {
            "Authorization": f"Bearer {ETHGLOBAL_API_KEY}",
            "Content-Type": "image/png",
        }
        response = requests.post(API_URL, headers=headers, data=fix["kartik.png"][0])
        assert response.status_code == 200
        print(f"  Finished request #{idx}")

    COUNT = 20
    print(f"Running stress test with {COUNT} concurrent requests (may take a minute)")
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=COUNT)
    tasks = [loop.run_in_executor(executor, post_image, i) for i in range(COUNT)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    fix = load_test_fixtures()
    test_auth()
    test_image_output(fix)
    asyncio.run(test_stress(fix))
    print("All tests passed!")
