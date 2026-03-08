from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple


NodeDict = Dict[str, Any]
GraphDict = Dict[str, Any]

DEFAULT_STYLE: Dict[str, Any] = {
    "node_radius": 20,
    "node_fill": "#4da6ff",
    "node_outline": "#1f3b5b",
    "node_outline_width": 2,
    "node_text_color": "#ffffff",
    "node_font": ("Arial", 10, "bold"),
    "edge_color": "#9aa4b2",
    "edge_width": 2,
    "path_color": "#22c55e",
    "path_width": 4,
    "selected_color": "#f59e0b",
    "visited_color": "#8b5cf6",
    "canvas_bg": "#111827",
}


def merge_style(style: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    merged = DEFAULT_STYLE.copy()
    if style:
        merged.update(style)
    return merged


def clear_graph(canvas) -> None:
    canvas.delete("all")


def set_canvas_background(canvas, style: Optional[Dict[str, Any]] = None) -> None:
    s = merge_style(style)
    try:
        canvas.configure(bg=s["canvas_bg"], highlightthickness=0)
    except Exception:
        pass


def get_node_center(node: NodeDict) -> Tuple[int, int]:
    return int(node["x"]), int(node["y"])


def _resolve_node(graph: GraphDict, node_ref: Any) -> Optional[NodeDict]:
    if isinstance(node_ref, dict):
        return node_ref

    nodes = graph.get("nodes", {})
    if isinstance(nodes, dict):
        return nodes.get(node_ref)

    if isinstance(nodes, list):
        for node in nodes:
            if node.get("id") == node_ref:
                return node

    return None


def _iter_nodes(graph: GraphDict) -> List[NodeDict]:
    nodes = graph.get("nodes", {})
    if isinstance(nodes, dict):
        return list(nodes.values())
    if isinstance(nodes, list):
        return nodes
    return []


def _iter_edges(graph: GraphDict) -> List[Tuple[Any, Any]]:
    edges = graph.get("edges", [])
    normalized: List[Tuple[Any, Any]] = []

    for edge in edges:
        if isinstance(edge, (tuple, list)) and len(edge) >= 2:
            normalized.append((edge[0], edge[1]))
        elif isinstance(edge, dict):
            a = edge.get("from") or edge.get("a") or edge.get("start")
            b = edge.get("to") or edge.get("b") or edge.get("end")
            if a is not None and b is not None:
                normalized.append((a, b))

    return normalized


def draw_node(
    canvas,
    node: NodeDict,
    style: Optional[Dict[str, Any]] = None,
    *,
    fill: Optional[str] = None,
    outline: Optional[str] = None,
    tags: Iterable[str] = (),
):
    s = merge_style(style)
    x, y = get_node_center(node)
    r = int(s["node_radius"])

    canvas.create_oval(
        x - r, y - r, x + r, y + r,
        fill=fill or s["node_fill"],
        outline=outline or s["node_outline"],
        width=s["node_outline_width"],
        tags=tuple(tags),
    )

    label = str(node.get("label", node.get("id", "")))
    canvas.create_text(
        x, y,
        text=label,
        fill=s["node_text_color"],
        font=s["node_font"],
        tags=tuple(tags),
    )


def draw_edge(
    canvas,
    node_a: NodeDict,
    node_b: NodeDict,
    style: Optional[Dict[str, Any]] = None,
    *,
    color: Optional[str] = None,
    width: Optional[int] = None,
    tags: Iterable[str] = (),
):
    s = merge_style(style)
    ax, ay = get_node_center(node_a)
    bx, by = get_node_center(node_b)

    canvas.create_line(
        ax, ay, bx, by,
        fill=color or s["edge_color"],
        width=width or s["edge_width"],
        tags=tuple(tags),
    )


def draw_graph(canvas, graph: GraphDict, style: Optional[Dict[str, Any]] = None, *, clear_first: bool = True) -> None:
    s = merge_style(style)

    if clear_first:
        clear_graph(canvas)

    set_canvas_background(canvas, s)

    for a_ref, b_ref in _iter_edges(graph):
        node_a = _resolve_node(graph, a_ref)
        node_b = _resolve_node(graph, b_ref)
        if node_a and node_b:
            draw_edge(canvas, node_a, node_b, s, tags=("edge",))

    for node in _iter_nodes(graph):
        draw_node(canvas, node, s, tags=("node",))


def highlight_node(
    canvas,
    node: NodeDict,
    style: Optional[Dict[str, Any]] = None,
    *,
    color: Optional[str] = None,
    ring_width: int = 4,
    expand: int = 7,
    tags: Iterable[str] = (),
):
    s = merge_style(style)
    x, y = get_node_center(node)
    r = int(s["node_radius"]) + expand

    canvas.create_oval(
        x - r, y - r, x + r, y + r,
        outline=color or s["selected_color"],
        width=ring_width,
        tags=tuple(tags),
    )


def highlight_selected_node(canvas, graph: GraphDict, node_ref: Any, style: Optional[Dict[str, Any]] = None) -> None:
    node = _resolve_node(graph, node_ref)
    if node:
        highlight_node(canvas, node, style, color=merge_style(style)["selected_color"], tags=("selected",))


def highlight_visited_nodes(canvas, graph: GraphDict, node_refs: Iterable[Any], style: Optional[Dict[str, Any]] = None) -> None:
    s = merge_style(style)
    for node_ref in node_refs:
        node = _resolve_node(graph, node_ref)
        if node:
            highlight_node(canvas, node, s, color=s["visited_color"], ring_width=3, expand=4, tags=("visited",))


def highlight_path(canvas, graph: GraphDict, path: Iterable[Any], style: Optional[Dict[str, Any]] = None) -> None:
    s = merge_style(style)
    resolved_nodes: List[NodeDict] = []

    for item in path:
        node = _resolve_node(graph, item)
        if node:
            resolved_nodes.append(node)

    for i in range(len(resolved_nodes) - 1):
        draw_edge(
            canvas,
            resolved_nodes[i],
            resolved_nodes[i + 1],
            s,
            color=s["path_color"],
            width=s["path_width"],
            tags=("path",),
        )

    for node in resolved_nodes:
        highlight_node(canvas, node, s, color=s["path_color"], ring_width=3, expand=3, tags=("path-node",))


def redraw_graph_with_path(
    canvas,
    graph: GraphDict,
    path: Optional[Iterable[Any]] = None,
    style: Optional[Dict[str, Any]] = None,
    *,
    selected_node: Optional[Any] = None,
    visited_nodes: Optional[Iterable[Any]] = None,
) -> None:
    draw_graph(canvas, graph, style, clear_first=True)

    if path:
        highlight_path(canvas, graph, path, style)

    if visited_nodes:
        highlight_visited_nodes(canvas, graph, visited_nodes, style)

    if selected_node is not None:
        highlight_selected_node(canvas, graph, selected_node, style)