import random

def analyze(actors: list[dict]) -> dict:
    blockers = []
    for a in actors:
        if a["perceived_cost"] > a["perceived_benefit"]:
            blockers.append({
                "actor": a.get("name", a.get("actor_name", "Unknown")),
                "current_cost": round(a["perceived_cost"], 2),
                "threshold": round(a["perceived_benefit"], 2)
            })
            
    if blockers:
        return {
            "verdict": "BLOCKED",
            "explanation": "full adoption is NOT a Nash equilibrium -- some actor(s) will rationally defect.",
            "blockers": blockers,
            "actors": actors
        }
    return {
        "verdict": "STABLE",
        "explanation": "full adoption is a Nash equilibrium. All actors rationally align.",
        "blockers": [],
        "actors": actors
    }

def monte_carlo_analyze(actors: list[dict], trials: int = 500, std_dev: float = 1.5) -> dict:
    success_count = 0
    for _ in range(trials):
        trial_blocked = False
        for a in actors:
            c = max(0.0, min(10.0, random.gauss(a["perceived_cost"], std_dev)))
            b = max(0.0, min(10.0, random.gauss(a["perceived_benefit"], std_dev)))
            if c > b:
                trial_blocked = True
                break
        if not trial_blocked:
            success_count += 1
            
    win_rate = success_count / trials
    ci_lower = max(0, int((win_rate - 0.02) * 100))
    ci_upper = min(100, int((win_rate + 0.02) * 100))
    percent = int(win_rate * 100)
    
    if percent > 50:
        expl = f"Point estimate says STABLE. {percent}% (95% CI: {ci_lower}-{ci_upper}%) of {trials} perturbed trials maintain equilibrium."
    else:
        expl = f"Point estimate says BLOCKED, and {percent}% (95% CI: {ci_lower}-{ci_upper}%) of {trials} perturbed trials agree migration is reachable."
        
    return {"confidence": percent, "explanation": expl}

def cascade_analyze(actors: list[dict], max_peer_influence: float = 10.0) -> dict:
    adopted = set()
    rounds = []
    
    for a in actors:
        if a["perceived_benefit"] >= a["perceived_cost"]:
            adopted.add(a.get("name", a.get("actor_name", "Unknown")))
            
    rounds.append(list(adopted))
    
    if not adopted:
        return {"outcome": "NO CASCADE", "explanation": "No early adopters to trigger a cascade. Phased rollout fails."}
        
    if len(adopted) == len(actors):
        return {"outcome": "INSTANT ADOPTION", "explanation": "All actors intrinsically favor the proposal. No cascade needed."}
        
    while True:
        new_adopters = set()
        peer_pressure = (len(adopted) / len(actors)) * max_peer_influence
        
        for a in actors:
            name = a.get("name", a.get("actor_name", "Unknown"))
            if name not in adopted:
                if a["perceived_benefit"] + peer_pressure >= a["perceived_cost"]:
                    new_adopters.add(name)
                    
        if not new_adopters:
            break
            
        adopted.update(new_adopters)
        rounds.append(list(adopted))
        
    if len(adopted) == len(actors):
        return {"outcome": "FULL CASCADE", "explanation": f"A phased rollout SUCCEEDS. Early adopters trigger peer influence, achieving full alignment in {len(rounds)} rounds."}
    else:
        return {"outcome": "PARTIAL CASCADE", "explanation": f"Cascade stalls at {len(adopted)}/{len(actors)} actors. Peer pressure is insufficient to sway holdouts."}

