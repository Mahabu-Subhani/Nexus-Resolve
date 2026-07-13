import ast
import hashlib
import json
import os
import networkx as nx
from pyvis.network import Network

CODEBASE_DIR = os.path.join(os.path.dirname(__file__), "seed_data", "mock_codebase")
CACHE_FILE = os.path.join(os.path.dirname(__file__), ".mcp_scan_cache.json")

HOURS_PER_STRIPE_REFERENCE = 2.5
MIGRATION_BASE_OVERHEAD_HOURS = 40
CENTRALITY_COORDINATION_HOURS = 60

CODEBASE_DOMAIN = "payments_billing"
CODEBASE_DOMAIN_KEYWORDS = {"stripe", "payment", "payments", "billing", "checkout", "charge", "subscriptions"}

def assess_domain_relevance(proposal_text: str) -> dict:
    text = (proposal_text or "").lower()
    matched = sorted(kw for kw in CODEBASE_DOMAIN_KEYWORDS if kw in text)
    return {"domain": CODEBASE_DOMAIN, "matched_keywords": matched, "relevant": bool(matched)}

def _file_hash(filepath: str) -> str:
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

class _ScanVisitor(ast.NodeVisitor):
    LOCAL_PACKAGES = {"billing", "checkout", "webhooks", "admin", "stripe_client", "billing_core", "subscriptions"}

    def __init__(self):
        self.stripe_references = []
        self.local_imports = set()

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "stripe" or alias.name.startswith("stripe."):
                self.stripe_references.append(f"import {alias.name}")
            top = alias.name.split(".")[0]
            if top in self.LOCAL_PACKAGES:
                self.local_imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            if node.module.startswith("stripe"):
                self.stripe_references.append(f"from {node.module} import ...")
            top = node.module.split(".")[0]
            if top in self.LOCAL_PACKAGES:
                self.local_imports.add(node.module)
        self.generic_visit(node)

def _scan_file(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return {"stripe_count": 0, "local_imports": []}

    visitor = _ScanVisitor()
    visitor.visit(tree)
    return {"stripe_count": len(visitor.stripe_references), "local_imports": sorted(visitor.local_imports)}

def scan_codebase(codebase_dir: str = CODEBASE_DIR) -> dict:
    per_file_results = {}
    for root, _, files in os.walk(codebase_dir):
        for fname in files:
            if fname.endswith(".py") and fname != "__init__.py":
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, codebase_dir)
                module_name = rel.replace(os.sep, ".").removesuffix(".py")
                per_file_results[rel] = {"module": module_name, **_scan_file(fpath)}

    total_refs = sum(r["stripe_count"] for r in per_file_results.values())

    dep_graph = nx.DiGraph()
    module_to_rel = {r["module"]: rel for rel, r in per_file_results.items()}
    for rel, r in per_file_results.items():
        dep_graph.add_node(r["module"])
        for imported_module in r["local_imports"]:
            dep_graph.add_node(imported_module)
            dep_graph.add_edge(r["module"], imported_module)

    if len(dep_graph) > 1:
        # Undirected guarantees billing_core registers as a massive central bridge
        centrality = nx.betweenness_centrality(dep_graph.to_undirected())
    else:
        centrality = {}

    central_files = sorted(
        ({"file": module_to_rel[mod], "module": mod, "centrality": round(score, 4)}
         for mod, score in centrality.items() if mod in module_to_rel and score > 0),
        key=lambda x: -x["centrality"]
    )
    
    file_breakdown = []
    if not central_files:
        file_breakdown.append("Codebase is fully decoupled or too small to measure structural risk.")
    else:
        for cf in central_files:
            file_breakdown.append(f"{cf['file']} — Structural Risk Score: {cf['centrality']}")

    # --- PyVis Interactive Graph Generation ---
    try:
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
        net.add_node("stripe", label="stripe (SDK)", title="External Dependency", color="#e6a822", size=40)
        for node in dep_graph.nodes():
            score = centrality.get(node, 0)
            color = "#ff4d4d" if score > 0 else "#4d94ff"
            size = 20 + (score * 50)
            net.add_node(node, label=node, title=f"Centrality: {score:.4f}", color=color, size=size)
        for u, v in dep_graph.edges():
            net.add_edge(u, v, color="#aaaaaa")
        for rel, r in per_file_results.items():
            if r["stripe_count"] > 0:
                net.add_edge(r["module"], "stripe", color="#e6a822", title=f"{r['stripe_count']} references")
        net.write_html(os.path.join(os.path.dirname(__file__), "nexus_graph.html"))
    except Exception:
        pass

    stripe_hours = total_refs * HOURS_PER_STRIPE_REFERENCE
    centrality_hours = sum(cf["centrality"] for cf in central_files) * CENTRALITY_COORDINATION_HOURS
    est_hours = round(MIGRATION_BASE_OVERHEAD_HOURS + stripe_hours + centrality_hours, 1)

    return {
        "file_breakdown": file_breakdown,
        "estimated_migration_hours": est_hours,
        "dependency_graph": {"edges": list(dep_graph.edges())}
    }
