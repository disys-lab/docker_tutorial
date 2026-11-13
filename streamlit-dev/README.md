# streamlit-dev

The Streamlit material for IEM 4723, Lectures 16 to 18.

Every example runs the **same base image**, `ghcr.io/disys-lab/streamlit-base`,
and simply overrides the command in its own `docker-compose.yml`. Nothing here
has to be built; the image is pulled.

| Folder       | What it is                                 | Open                  |
|--------------|--------------------------------------------|-----------------------|
| `lecture16/` | Text, tables, metrics, the built-in charts | http://localhost:8503 |
| `lecture17/` | Widgets, layout, session state, forms      | http://localhost:8504 |
| `lecture18/` | The warehouse dashboard, with MySQL and Redis | http://localhost:8505 |

They use different published ports, so they can all run at once.

## Running an example

```bash
cd lecture16        # or lecture17, or lecture18
docker compose up -d
```

Then open the port from the table above.

Lectures 16 and 17 read the warehouse CSVs directly and need no database, so
each is a single service. Lecture 18 also starts MySQL and Redis:

```bash
cd lecture18
docker compose up -d
```

Its database starts empty. The page offers a **Load the warehouse data** button,
which loads the CSVs into MySQL and the item data into Redis. A **Reload the
data** control in the sidebar rebuilds everything from scratch.

You can also load it from the command line if you prefer:

```bash
docker compose exec streamlit python app/seed.py
```

## How the examples share an image

Each `docker-compose.yml` pulls the same image and overrides `command`:

```yaml
services:
  streamlit:
    image: ghcr.io/disys-lab/streamlit-base:latest
    command: >
      streamlit run app/basics.py
        --server.port 8501
        --server.address 0.0.0.0
        --server.headless true
```

To add an example, make a folder, drop the script in its `app/`, copy a compose
file, and change the script name and the published port.

## The base image

Source is in `base/`. It is Python 3.12 with `streamlit`, `pandas`, `pymysql`
and `redis` preinstalled, and no application code. Rebuild and publish with:

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
    -t ghcr.io/disys-lab/streamlit-base:latest base --push
```

The `--platform` flag matters: it builds for both Intel and Apple Silicon, so
the image works on every student machine rather than only the one that built it.

## Editing while it runs

Each `app/` folder is mounted into its container, so edits on your machine take
effect immediately. Save the file and the browser offers a rerun. You only need
to touch the image if you add a Python package.

## Ports

Chosen so nothing in this repo collides:

| | Here | Elsewhere |
|---|---|---|
| Lecture 16 | 8503 | 8501 (`networking`) |
| Lecture 17 | 8504 | |
| Lecture 18 | 8505 | |
| MySQL | 3307 | 3306 (`mysql-dev`) |
| Redis | 6381 | 6380 (`redis-dev`) |

Inside the compose network the services keep their standard ports, so the
Lecture 18 dashboard connects to `mysql:3306` and `redis:6379` by service name. The
published numbers only matter from your machine.

## Stopping

```bash
docker compose down          # in whichever folder you started
```

The dashboard's `mysql-data` and `redis-data` volumes survive, so the seeded
database is still there next time. `docker compose down -v` throws that away.
