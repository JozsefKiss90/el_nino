import cytoscape, { type Core } from "cytoscape";
import { useEffect, useRef } from "react";
import type { GraphData } from "../data/types";

// GraphView — the React-native cytoscape render block (the same renderer the Stage-2 console and
// frontend/index.html use). Pure presentation: it draws whatever {nodes, edges} it's handed.

const PALETTE = [
  "#27e0e0", "#7ad27a", "#e0a127", "#c77adf", "#5a9ee0", "#e07a7a",
  "#9fe0c1", "#e0d27a", "#7a8fe0", "#e07ac1", "#7ae0a1", "#b0b0b0",
];
const colorMap: Record<string, string> = {};
function colorFor(label: string): string {
  if (!(label in colorMap)) colorMap[label] = PALETTE[Object.keys(colorMap).length % PALETTE.length];
  return colorMap[label];
}

interface Props {
  graph: GraphData;
  focus?: string;
  height?: number;
  onNodeClick?: (id: string, name: string) => void;
}

export function GraphView({ graph, focus, height, onNodeClick }: Props) {
  const elRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const clickRef = useRef(onNodeClick);
  clickRef.current = onNodeClick;

  // init once
  useEffect(() => {
    if (!elRef.current) return;
    const cy = cytoscape({
      container: elRef.current,
      style: [
        {
          selector: "node",
          style: {
            "background-color": "data(color)", label: "data(id)", color: "#cfe9f2",
            "font-size": "7px", "text-valign": "center", "text-halign": "center",
            "text-margin-y": -9, width: 16, height: 16, "border-width": 1, "border-color": "#0a0f14",
          },
        },
        { selector: "node.focus", style: { "border-width": 3, "border-color": "#fff", width: 22, height: 22 } },
        {
          selector: "edge",
          style: {
            width: 1, "line-color": "#2a4a57", "target-arrow-color": "#2a4a57",
            "target-arrow-shape": "triangle", "curve-style": "bezier", "arrow-scale": 0.6,
            label: "data(type)", "font-size": "5px", color: "#567", "text-rotation": "autorotate",
          },
        },
      ],
      layout: { name: "cose", animate: false },
      wheelSensitivity: 0.25,
    });
    cy.on("tap", "node", (ev) => clickRef.current?.(ev.target.id(), ev.target.data("name")));
    cyRef.current = cy;
    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, []);

  // re-render on graph/focus change
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.elements().remove();
    const seen = new Set<string>();
    const eles: cytoscape.ElementDefinition[] = [];
    for (const n of graph.nodes) {
      if (n.id && !seen.has(n.id)) {
        seen.add(n.id);
        eles.push({
          data: { id: n.id, label: n.label, name: n.name || n.id, color: colorFor(n.label) },
          classes: n.id === focus ? "focus" : "",
        });
      }
    }
    for (const e of graph.edges) {
      if (e.source && e.target && seen.has(e.source) && seen.has(e.target)) {
        eles.push({ data: { id: `${e.source}|${e.type}|${e.target}`, source: e.source, target: e.target, type: e.type } });
      }
    }
    cy.add(eles);
    cy.layout({ name: "cose", animate: false, nodeRepulsion: 8000, idealEdgeLength: 60 } as cytoscape.LayoutOptions).run();
    cy.fit(undefined, 25);
  }, [graph, focus]);

  return <div ref={elRef} className="minigraph" style={height ? { height } : undefined} />;
}
