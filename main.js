import Graph from "https://esm.sh/graphology@0.26.0";
import Sigma from "https://esm.sh/sigma@3.0.2";
import { parse } from "https://esm.sh/graphology-gexf@0.13.2/browser";

let renderer = null;

// Load external GEXF file
fetch("./network/movie_graph.gexf")
  .then((res) => res.text())
  .then((gexf) => {
    // Parse GEXF string
    const graph = parse(Graph, gexf);

    // Basic node styling
    graph.forEachNode((node) => {
      graph.setNodeAttribute(node, "size", 3);
      graph.setNodeAttribute(node, "color", "#4aa3df");
    });

    // Make edges light (very important for readability)
    graph.forEachEdge((edge) => {
      graph.setEdgeAttribute(edge, "color", "rgba(0,0,0,0.05)");
    });

    // Retrieve DOM elements
    const container = document.getElementById("sigma-container");
    const zoomInBtn = document.getElementById("zoom-in");
    const zoomOutBtn = document.getElementById("zoom-out");
    const zoomResetBtn = document.getElementById("zoom-reset");
    const toggleEdgesBtn = document.getElementById("toggle-edges");
    const labelsThresholdRange = document.getElementById("labels-threshold");

    // Instantiate Sigma renderer
    renderer = new Sigma(graph, container, {
  minCameraRatio: 0.001,   // zoom waaaay in
  maxCameraRatio: 20,      // zoom waaaay out
  labelRenderedSizeThreshold: 8,
});

    const camera = renderer.getCamera();

    // Bind zoom buttons
    zoomInBtn.addEventListener("click", () => {
      camera.animatedZoom({ duration: 600 });
    });

    zoomOutBtn.addEventListener("click", () => {
      camera.animatedUnzoom({ duration: 600 });
    });

    zoomResetBtn.addEventListener("click", () => {
      camera.animatedReset({ duration: 600 });
    });

    let edgesVisible = true;

    toggleEdgesBtn.addEventListener("click", () => {
      edgesVisible = !edgesVisible;

      graph.forEachEdge((edge) => {
        graph.setEdgeAttribute(edge, "hidden", !edgesVisible);
      });

      toggleEdgesBtn.textContent = `Edges: ${edgesVisible ? "On" : "Off"}`;
      toggleEdgesBtn.setAttribute("aria-pressed", String(!edgesVisible));
      renderer.refresh();
    });

    // Bind label threshold slider
    labelsThresholdRange.value =
      renderer.getSetting("labelRenderedSizeThreshold");

    labelsThresholdRange.addEventListener("input", () => {
      renderer.setSetting(
        "labelRenderedSizeThreshold",
        Number(labelsThresholdRange.value)
      );
    });
  });

// Cleanup hook (optional, mirrors example)
export default function destroy() {
  if (renderer) renderer.kill();
}
