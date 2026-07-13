def build_nexus_card(summary, mcp_report, rts_hits, game_result, mc_result, domain_relevance, financial_result, cascade_result):
    edges_count = len(mcp_report.get("dependency_graph", {}).get("edges", []))
    
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": "Nexus Temporal Simulation", "emoji": True}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Proposal:* {summary}\n_{domain_relevance}_"}},
        {"type": "divider"}
    ]

    friction_text = f"*{edges_count} real dependency edges.*\n"
    for item in mcp_report.get("file_breakdown", []):
        friction_text += f"• {item}\n"
        
    fin_res = financial_result or {}
    cost_str = f"${fin_res.get('estimated_structural_cost_usd', 0):,.2f}"
    friction_text += f"\n*Estimated Structural Cost:* {cost_str} _(@ ${fin_res.get('hourly_rate_assumption_usd', 0)}/hr)_"
    
    if fin_res.get("stated_claims_found_in_text"):
        claims = ", ".join(fin_res["stated_claims_found_in_text"])
        friction_text += f"\n*Stated Claims in Text:* {claims}"

    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": f" *Codebase Friction:*\n{friction_text}"},
        "accessory": {"type": "button", "text": {"type": "plain_text", "text": "View Dependency Graph"}, "value": "view_graph", "action_id": "nexus_graph"}
    })

    context_text = ""
    for hit in (rts_hits or []):
        score = hit.get('score', hit.get('relevance_score', 'N/A'))
        context_text += f"• *#{hit.get('channel', 'general')}* (rel {score}): {hit.get('text', '')}\n"
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f" *Context:*\n{context_text or '_No relevant context._'}"}})
    blocks.append({"type": "divider"})

    verdict = game_result.get("verdict", "UNKNOWN")
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f" *Simultaneous Verdict:*\n*{verdict}*: {game_result.get('explanation', '')}"}})

    blockers = game_result.get("blockers", [])
    if blockers:
        b_text = "\n".join([f"• {b.get('actor', 'Unknown')} (Current: {b.get('current_cost', 0)} → Need < {b.get('threshold', 0)})" for b in blockers])
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f"*Blockers:*\n{b_text}"}})

    cascade_outcome = cascade_result.get("outcome", "UNKNOWN")
    cascade_emoji = "🌊" if cascade_outcome == "FULL CASCADE" else "🛑"
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f" *Cascade Dynamics (Phased Rollout)* {cascade_emoji}\n*{cascade_outcome}*: {cascade_result.get('explanation', '')}"}})
    
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": f" *Confidence (Monte Carlo):*\n{mc_result.get('explanation', '')}"}]})

    blocks.append({
        "type": "actions",
        "elements": [
            {"type": "button", "text": {"type": "plain_text", "text": "✨ AI Architect", "emoji": True}, "style": "primary", "value": "refactor", "action_id": "nexus_architect"},
            {"type": "button", "text": {"type": "plain_text", "text": "Negotiate", "emoji": True}, "value": '{"summary": "' + summary.replace('"', '\\"') + '", "actors": ' + __import__('json').dumps(game_result.get('actors', [])) + '}', "action_id": "nexus_negotiate"},
            {"type": "button", "text": {"type": "plain_text", "text": "Reject", "emoji": True}, "style": "danger", "value": "reject", "action_id": "nexus_reject"}
        ]
    })
    return {"blocks": blocks}

def build_negotiate_modal(summary, actors, channel_id, thread_ts):
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": f"Adjust perceived costs/benefits for:\n*{summary}*"}}, {"type": "divider"}]
    for i, actor in enumerate(actors):
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f"*{actor.get('name', actor.get('actor_name', 'Unknown'))}*"}})
        blocks.append({"type": "input", "block_id": f"actor_{i}_cost", "element": {"type": "plain_text_input", "action_id": "value", "initial_value": str(actor.get("perceived_cost", 5.0))}, "label": {"type": "plain_text", "text": "Cost (0-10)"}})
        blocks.append({"type": "input", "block_id": f"actor_{i}_benefit", "element": {"type": "plain_text_input", "action_id": "value", "initial_value": str(actor.get("perceived_benefit", 5.0))}, "label": {"type": "plain_text", "text": "Benefit (0-10)"}})
        blocks.append({"type": "divider"})
    return {
        "type": "modal", "callback_id": "nexus_negotiate_modal",
        "private_metadata": __import__('json').dumps({"summary": summary, "actors": actors, "channel_id": channel_id, "thread_ts": thread_ts}),
        "title": {"type": "plain_text", "text": "Negotiate Incentives"},
        "submit": {"type": "plain_text", "text": "Recalculate"}, "close": {"type": "plain_text", "text": "Cancel"}, "blocks": blocks
    }

def build_recalculated_result_blocks(summary, game_result, cascade_result):
    return [
        {"type": "header", "text": {"type": "plain_text", "text": "Nexus Recalculation", "emoji": True}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*New Simultaneous Verdict:* {game_result.get('verdict', 'UNKNOWN')}: {game_result.get('explanation', '')}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*New Cascade Verdict:*\n*{cascade_result.get('outcome', 'UNKNOWN')}*: {cascade_result.get('explanation', '')}"}}
    ]
