#!/usr/bin/env bash
set -euo pipefail
# Launch full stack with services and run e2e tests
docker compose --profile api --profile frontend --profile pg --profile weaviate --profile redis up -d --build
# run e2e test container
docker compose --profile e2e run --rm e2e
