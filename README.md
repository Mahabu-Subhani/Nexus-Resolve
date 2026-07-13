# Nexus 

**Solving organizational gridlock with game theory, AST codebase scanning, and generative AI.**

Nexus is a Slack-native resolution engine. It treats corporate friction (like Sales wanting a fast launch and Engineering wanting to avoid risk) not as a communication problem, but as a strict mathematical coordination game. 

Instead of just summarizing arguments, Nexus calculates the actual political and technical friction and mathematically proves the best path forward.

## Core Features

* **Game Theory Engine:** Uses Gemini 3.1 Flash-Lite to parse unstructured Slack arguments into a strict payoff matrix.
* **Mathematical Proofs:** Runs 500 Monte Carlo perturbations to calculate stable Nash Equilibria and Granovetter threshold models to test if a phased rollout will trigger a cascade effect.
* **Secure Static Analysis:** Uses Python's native `ast` module to read the codebase securely. It maps module dependencies with `networkx` and visualizes structural bottlenecks with interactive `pyvis` graphs.
* **AI Architect:** Automatically generates safe code rewrites for the bottleneck using the Adapter design pattern.

## Tech Stack

* **Language:** Python
* **Platform:** Slack Bolt API
* **AI:** Google Gemini 3.1 Flash-Lite
* **Math & Algorithms:** NetworkX, AST, Monte Carlo Simulations

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Mahabu-Subhani/Nexus-Resolve.git](https://github.com/Mahabu-Subhani/Nexus-Resolve)
   cd nexus-temporal-simulation
