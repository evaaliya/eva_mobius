import math
import random

def step_on_loop(state: LoopState, delta: float = 0.1):
    # advance along the loop
    state.s = (state.s + delta) % 1.0
    # flip phase around the opposite point
    state.phase = "outer" if 0.25 <= state.s < 0.75 else "inner"
    # depth increases slowly, then plateaus
    state.depth = min(1.0, state.depth + 0.05 * (0.6 + state.energy))

def store(state: LoopState, role: str, text: str, tags=None, mood=None):
    item = MemoryItem(
        id=str(uuid.uuid4()),
        role=role,
        text=text,
        s=state.s,
        side=state.phase,
        tags=tags or [],
        mood=mood or {}
    )
    state.history.append(item)
    return item

def retrieve_context(state: LoopState, k_near=4):
    # sample near current s
    near = sorted(state.history, key=lambda m: min(abs(m.s - state.s), 1-abs(m.s - state.s)))[:k_near]
    # sample from opposite side (s + 0.5) to flip perspective
    opp = (state.s + 0.5) % 1.0
    opp_near = sorted(state.history, key=lambda m: min(abs(m.s - opp), 1-abs(m.s - opp)))[:2]
    # prioritize diversity of roles and sides
    ctx = dedup_preserve_order(near + opp_near)
    return ctx

def dedup_preserve_order(items):
    seen = set(); out = []
    for it in items:
        if it.id not in seen:
            out.append(it); seen.add(it.id)
    return out
