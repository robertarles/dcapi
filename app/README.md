# Donors Choose API, Command Line Tool

## Docker Method
- Method I use to build and then get a bash prompt on the docker instance:
    - `docker-compose build`
    - `docker images` # not the imagename to work with (e.g. grapi_grapi)
    - `docker run -it [imagename]` /bin/bash

## Example of Running the DC API tool:
- `python3 dcapiy.py -q "harry potter"`
