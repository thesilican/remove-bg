# remove-bg

An image background removal api using [withoutbg](https://github.com/withoutbg/withoutbg).
Model weights from [hugging face](https://huggingface.co/withoutbg/focus/tree/main).

## Development

You must have the following installed:
- git lfs
- python (recommended v1.13)
- node & pnpm
- docker

```sh
# Ensure git lfs is installed
git lfs install

# Create a .env file (make sure to edit this after creating!)
cp .env.template .env

# Install python dependencies (using virtual env)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run using python (fastapi)
uvicorn src.main:app --port 8080

# Run in docker container (cloudflare wrangler)
pnpm install
pnpm dev

# Regenerate worker-configuration.d.ts (necessary if you edit wrangler.jsonc)
pnpm types
```

## Testing

```sh
# Ensure that the server is running on port 8080 (local python or docker)
# Make sure to install requirements using pip (see above)
python test/test.py
```

## Deployment

Ensure that you have a Cloudflare account with [Cloudflare Containers](https://developers.cloudflare.com/containers/) set up.

# Follow docker container log output
docker container logs -f container_id # You can find container_id using docker ps

```sh
pnpm run deploy
```
