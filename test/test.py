from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from PIL import Image
import requests
import asyncio
from dotenv import load_dotenv
from os import environ
from pathlib import Path
from imagehash import average_hash

load_dotenv()
ETHGLOBAL_API_KEY = environ.get("ETHGLOBAL_API_KEY")
API_URL = "http://localhost:8080/api/image"

type Fixtures = dict[str, tuple[bytes, bytes]]


def load_test_fixtures() -> Fixtures:
    print("Loading test fixtures")
    fix = {}
    for infile in Path("test/fixtures/input").iterdir():
        outfile = Path("test/fixtures/output") / infile.with_suffix(".png").name
        print(f"  Loading {infile.name}")
        input = open(infile, "rb").read()
        output = open(outfile, "rb").read()
        fix[infile.name] = (input, output)
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
        input, output = fix[name]
        print(f"  Testing fixture {name}")
        headers = {
            "Authorization": f"Bearer {ETHGLOBAL_API_KEY}",
            "Content-Type": "image/jpeg" if name.endswith(".jpg") else "image/png",
        }
        response = requests.post(API_URL, headers=headers, data=input)
        assert response.status_code == 200
        # There should be no perceptual difference between the expected and actual images
        # The exact file contents may differ due to differences in model execution in
        # different cpu architectures/environments.
        expected = average_hash(Image.open(BytesIO(output)), hash_size=128)
        actual = average_hash(Image.open(BytesIO(response.content)), hash_size=128)
        assert expected - actual == 0


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
