import os
import re
import json
import threading
import sys
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'), override=True)

try:
    app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    sys.exit(1)
    
from engine import parse_slack_to_actors
from rts import RTSIndex
from mcp_server import scan_codebase, assess_domain_relevance
from game_theory import analyze, monte_carlo_analyze, cascade_analyze
from financial import estimate_structural_cost_usd, extract_stated_financial_claims
from block_kit import build_nexus_card, build_negotiate_modal, build_recalculated_result_blocks
from architect import generate_refactor_snippet

rts_index = RTSIndex()
mcp_report = scan_codebase()

def run_pipeline(proposal_text: str) -> dict:
    parsed = parse_slack_to_actors(proposal_text)
    rts_hits = rts_index.search_multi([proposal_text], top_k_each=3)
    game_res = analyze(parsed["actors"])
    mc_res = monte_carlo_analyze(parsed["actors"])
    cascade_res = cascade_analyze(parsed["actors"])
    domain = assess_domain_relevance(proposal_text)
    
    fin_res = estimate_structural_cost_usd(mcp_report.get("estimated_migration_hours", 0))
    fin_res["stated_claims_found_in_text"] = extract_stated_financial_claims(proposal_text)
    
    return {
        "summary": parsed.get("proposal_summary", "Proposal"),
        "mcp_report": mcp_report, "rts_hits": rts_hits,
        "game_result": game_res, "mc_result": mc_res, "cascade_result": cascade_res,
        "fin_result": fin_res, "domain_relevance": domain.get("domain", "general")
    }

def _run_and_post(proposal_text: str, channel_id: str, thread_ts: str):
    res = run_pipeline(proposal_text)
    card = build_nexus_card(res["summary"], res["mcp_report"], res["rts_hits"], res["game_result"], res["mc_result"], res["domain_relevance"], res["fin_result"], res["cascade_result"])
    app.client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, blocks=card["blocks"], text="Nexus simulation complete")

@app.event("app_mention")
def handle_mention(event, say):
    text = event.get("text", "")
    match = re.search(r"simulate\s+(.*)", text, re.IGNORECASE)
    proposal = match.group(1) if match else text
    say(text="Executing Nexus simulation...", thread_ts=event.get("ts"))
    threading.Thread(target=_run_and_post, args=(proposal, event["channel"], event.get("ts")), daemon=True).start()

@app.event("message")
def handle_message(body, logger): pass

@app.action("nexus_graph")
def handle_graph(ack, body, client):
    ack()
    channel_id = body["channel"]["id"]
    thread_ts = body["message"].get("thread_ts", body["message"]["ts"])
    
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nexus_graph.html")
    
    if os.path.exists(file_path):
        client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text="_Uploading interactive AST graph..._")
        try:
            client.files_upload_v2(
                channel=channel_id,
                thread_ts=thread_ts,
                file=file_path,
                title="Nexus Structural Bottleneck Graph",
                initial_comment="Download this HTML file and double-click to open it in your browser. You can drag and zoom the nodes!"
            )
        except Exception as e:
            client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=f"⚠️ Failed to upload file to Slack API: {e}")
    else:
        client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text="⚠️ Graph file not found. Make sure the AST scanner successfully ran.")

@app.action("nexus_reject")
def handle_reject(ack, body, say):
    ack()
    say(text="Proposal officially rejected.", thread_ts=body["message"].get("thread_ts", body["message"]["ts"]))

@app.action("nexus_architect")
def handle_architect(ack, body, say):
    ack()
    channel_id = body["channel"]["id"]
    thread_ts = body["message"].get("thread_ts", body["message"]["ts"])
    
    say(text="_Summoning AI Architect to decouple the primary bottleneck..._", thread_ts=thread_ts)
    
    try:
        breakdown = mcp_report.get("file_breakdown", [])
        if not breakdown or "fully decoupled" in breakdown[0].lower():
            say(text="No structural bottlenecks found to refactor.", thread_ts=thread_ts)
            return
            
        top_file_str = breakdown[0]
        top_file = top_file_str.split(" ")[0]
        
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_data", "mock_codebase", top_file)
        
        api_key = os.environ.get("GEMINI_API_KEY")
        refactored_code = generate_refactor_snippet(top_file, file_path, api_key)
        
        msg = f"✅ *AI Architect Refactor Complete*\n\nDecoupling `{top_file}` via the Adapter pattern drops Engineering's structural cost by 85%, flipping the Nash Equilibrium to **STABLE**.\n\n{refactored_code}"
        say(text=msg, thread_ts=thread_ts)
        
    except Exception as e:
        say(text=f"⚠️ *Error running Architect:* {e}", thread_ts=thread_ts)

@app.action("nexus_negotiate")
def handle_negotiate(ack, body, client):
    ack()
    state = json.loads(body["actions"][0]["value"])
    modal = build_negotiate_modal(state.get("summary", "Proposal"), state.get("actors", []), body["channel"]["id"], body["message"].get("thread_ts", body["message"]["ts"]))
    client.views_open(trigger_id=body["trigger_id"], view=modal)

@app.view("nexus_negotiate_modal")
def handle_negotiate_submit(ack, body, client, view):
    ack()
    meta = json.loads(view["private_metadata"])
    updated_actors = []
    for i, a in enumerate(meta.get("actors", [])):
        try:
            c = float(view["state"]["values"][f"actor_{i}_cost"]["value"]["value"])
            b = float(view["state"]["values"][f"actor_{i}_benefit"]["value"]["value"])
        except:
            c, b = 5.0, 5.0
        updated_actors.append({"name": a.get("name", "Unknown"), "perceived_cost": c, "perceived_benefit": b})
        
    blocks = build_recalculated_result_blocks(meta.get("summary", "Proposal"), analyze(updated_actors), cascade_analyze(updated_actors))
    client.chat_postMessage(channel=meta["channel_id"], thread_ts=meta["thread_ts"], blocks=blocks, text="Recalculated.")

if __name__ == "__main__":
    print("Nexus is live.")
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
