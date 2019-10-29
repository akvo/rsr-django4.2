#!/bin/bash

# To discard previously collected responses, and create a new canonical copy of
# the expected responses, use the --collect flag.
docker-compose exec web ./scripts/docker/dev/run-as-user.sh bash -c 'SLOW_TESTS=1 ./scripts/docker/dev/run-slow-tests.sh'
