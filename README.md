# MovieNetR

An interactive movie-recommendation network built from Reddit discussions and
IMDb title data. The pipeline extracts movie entities, normalizes titles, and
connects films that appear in the same recommendation threads.

## Interactive graph

The repository includes a static, WebGL-powered graph explorer. To preview it
locally, run:

```powershell
python -m http.server 8000
```

Then visit `http://localhost:8000`. Opening `index.html` directly will not work
because browsers block local `fetch` requests for the GEXF file.

To publish it, push the repository to GitHub and select **Settings → Pages →
Deploy from a branch**, then choose the repository's main branch and root
folder. The graph file is approximately 37 MB, so the first visit can take a
moment on slower connections.
