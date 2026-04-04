# remove-bg

An image background removal api using [withoutbg](https://github.com/withoutbg/withoutbg)
([model weights](https://huggingface.co/withoutbg/focus/tree/main)).

## Development

Ensure git lfs hooks are installed:

```sh
git lfs install
```

Create a `.env` file with the following:
```
ETHGLOBAL_API_KEY=api_key_here
```

Then run one of the following:

```sh
# Using docker compose
docker compose up --build

# Using docker
docker build . -t remove-bg
docker container run -it -p 8080:8080 -e ETHGLOBAL_API_KEY=api_key_here remove-bg

# Using fastapi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi run src/main.py --port 8080
```

## Testing

Ensure that the server is running on port 8080.

Follow the instructions to setup venv & install dependencies, then run:

```sh
python test/test.py
```
