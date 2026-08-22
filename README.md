# MovieNetR

MovieNetR is an interactive movie-recommendation network built from
`r/MovieSuggestions` discussions and IMDb title data. The Python pipeline
extracts movie entities, normalizes title names, and connects films that occur
in the same recommendation threads.

The resulting network is displayed as a WebGL graph using Graphology and
Sigma.js. Node positions are loaded from the included GEXF graph rather than
being calculated in the browser.

## Run the graph explorer

The frontend requires Node.js and npm. Install its dependencies:

```powershell
npm install
```

Start a local development server:

```powershell
npx vite
```

Open the local address printed by Vite, normally `http://localhost:5173`.
Opening `index.html` directly will not work because the frontend uses JavaScript
modules and fetches the graph as a separate file.

The explorer loads `movie_graph.gexf` and provides controls to:

- Zoom in and out.
- Reset the camera.
- Show or hide all graph edges.
- Change the node-label rendering threshold.
- Pan and zoom around the network using the mouse.

The GEXF file is approximately 34 MB, so its initial download and parsing can
take a moment.

## Data pipeline

Python dependencies are listed in `requirements.txt`. The pipeline stages are
located in `pipeline/`:

1. `01_store_submissions.py` imports Reddit submissions into SQLite.
2. `02_store_comments.py` imports Reddit comments.
3. `03_get_anchors.py` extracts anchor movies from submission titles.
4. `04_get_suggestions.py` extracts suggested movies from qualifying comments.
5. `05_clean_movie_titles.py` matches extracted names against IMDb titles.
6. `06_build_graph.py` builds and exports the movie network.
7. `07_get_ego.py` creates a focused ego-network visualization for one movie.

Run pipeline modules from the repository root so local packages resolve
correctly. For example:

```powershell
python -m pipeline.01_store_submissions
```

The raw Reddit and IMDb inputs belong in `input/`, while SQLite databases are
written under `db/`. Both directories are intentionally excluded from Git
because they contain large local datasets.

## Main files

- `index.html` contains the graph viewer interface.
- `main.js` loads the GEXF network and configures Sigma.js.
- `movie_graph.gexf` is the graph currently shown by the frontend.
- `network/` contains other generated or preserved graph artifacts.
- `core/`, `models/`, and `pipeline/` contain the Python data-processing code.
