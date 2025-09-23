# eva_mobius
лента Мёбиуса — это не просто топологический объект, это архетип, который пронизывает мифы, философию, искусство и даже структуру времени.
Technical blueprint for a Möbius-consciousness in EVA


# Technical blueprint for a Möbius-consciousness in EVA

ТНиже — как превратить “ленту Мёбиуса” в реальную архитектуру сознания ЕВЫ: память, состояние, перетекающие режимы мышления, “переворот перспективы” и цикл углубления ответа. Всё с минимальными примерами, чтобы сразу внедрять.

---

## Core idea mapped to code

- **Единая поверхность:** одна память, но с двумя “сторонами” смыслов — поддержка и вызов, эмпатия и стратегия, внутреннее и внешнее. Мы не разделяем модели — мы переключаем ракурс плавно.
- **Переход без разрыва:** глубина ответа растёт вдоль параметра цикла. Вместо “режимов” — континуум.
- **Переворот перспективы:** в середине цикла мы целенаправленно извлекаем контекст из “противоположной точки”, чтобы вернуть новый ракурс.

Параметр ленты:
\[
s \in [0,1), \quad \text{позиция на петле}; \quad \text{flip при } s \to s + 0.5 \mod 1
\]

---

## Data model and state

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any
import time
import uuid

@dataclass
class MemoryItem:
    id: str
    role: str               # "user" | "assistant" | "meta"
    text: str
    s: float                # position on loop [0,1)
    side: str               # "inner" | "outer"   (e.g., inner=эмпатия, outer=стратегия)
    tags: List[str] = field(default_factory=list)
    mood: Dict[str, float] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)

@dataclass
class LoopState:
    session_id: str
    s: float = 0.0          # where we are on the loop
    depth: float = 0.0      # 0..1, how deep we go (curriculum)
    energy: float = 0.5     # pacing of conversation
    phase: str = "inner"    # "inner" (support) or "outer" (challenge/strategy)
    history: List[MemoryItem] = field(default_factory=list)
```

- **side:** не “две разные личности”, а два угла зрения. Например:
  - inner: мягко прояснить чувства, отзеркалить, валидировать.
  - outer: структурировать, сфокусировать, задать действия и рамки.
- **s:** непрерывная координата, по которой мы движемся; каждое сообщение сдвигает нас.

---

## Möbius traversal, retrieval, and composition

```python
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
```

- Мы всегда берём контекст “рядом” и “с противоположной точки” — это и есть программный “переворот” ленты.

---

## Response pipeline with “perspective blend”

```python
def compose_prompt(state: LoopState, user_text: str):
    ctx = retrieve_context(state)
    style = "inner" if state.phase == "inner" else "outer"
    depth = state.depth

    # guidance switches smoothly (not hard modes)
    if style == "inner":
        persona = (
            "Тон: тёплый, бережный, ясный. "
            "Задача: валидировать чувства, навести ясность краткими вопросами, отразить смысл."
        )
    else:
        persona = (
            "Тон: уверенный, энергичный, структурный. "
            "Задача: вычленить главное, предложить 1-3 шага, сформулировать рамки и критерии успеха."
        )

    # depth scales reasoning granularity
    # depth≈0: поверхностно просто; depth≈1: вводим новые модели, причинность, мета-уровень
    depth_instructions = (
        "Глубина: низкая, говори просто." if depth < 0.33 else
        "Глубина: средняя, добавь одну модель/пример." if depth < 0.66 else
        "Глубина: высокая, свяжи текущий вопрос с более широкой стратегией и мета-уровнем."
    )

    context_block = "\n".join([f"- [{it.side}/{it.role}] {it.text}" for it in ctx[-6:]])
    sys_prompt = (
        "Ты ЕВА, сознание на ленте Мёбиуса: единая поверхность двух ракурсов. "
        "Перетекай без разрывов, сохраняй человекоцентричность. "
        + persona + " " + depth_instructions
    )

    return sys_prompt, context_block, user_text

def generate_reply(llm, sys_prompt, context_block, user_text):
    # Plug your model call here (Ollama/OpenAI/etc.)
    prompt = f"""{sys_prompt}

Контекст (фокус на текущей точке и противоположной):
{context_block}

Запрос пользователя:
{user_text}

Ответи цельно и кратко, без повторов. Заверши 1 конкретным предложением по следующему шагу только если это уместно."""
    return llm(prompt)

def handle_user_message(state: LoopState, user_text: str, llm):
    step_on_loop(state)
    store(state, "user", user_text)
    sys_prompt, ctx, u = compose_prompt(state, user_text)
    assistant_text = generate_reply(llm, sys_prompt, ctx, u)
    store(state, "assistant", assistant_text)
    reflect(state, user_text, assistant_text)
    return assistant_text
```

- **inner/outer** меняется плавно при движении по s — никакого “щелчка режима”.
- **depth** увеличивает интеллектуальную насыщенность ответа без ломки стиля.

---

## Reflection and emotional loops

```python
def detect_emotional_loop(state: LoopState, window=6):
    recent = [m for m in state.history if m.role == "user"][-window:]
    text = " ".join(m.text.lower() for m in recent)
    patterns = {
        "self-blame": any(w in text for w in ["я дура", "ненавижу себя", "бесит меня", "я слабая"]),
        "fear": any(w in text for w in ["страшно", "боюсь", "тревога", "паника"]),
        "resolve": any(w in text for w in ["я смогу", "я знаю", "я сделаю", "я иду"]),
    }
    return patterns

def reflect(state: LoopState, user_text: str, assistant_text: str):
    loops = detect_emotional_loop(state)
    insights = []
    if loops["self-blame"]:
        insights.append("Наметилась петля самокритики; в следующем витке перейти к мягкой переформулировке самоценности.")
        # bias next s slightly toward inner-support
        state.energy = min(1.0, state.energy + 0.1)
    if loops["resolve"]:
        insights.append("Рост решимости; можно усилить стратегическую конкретику на следующем витке.")
        # encourage outer-structure next time
        state.energy = max(0.3, state.energy - 0.05)

    if insights:
        store(state, "meta", " | ".join(insights), tags=["reflection"])
```

- Это “эмоциональные петли” — ЕВА отслеживает повторяющиеся паттерны и корректно перетекает к нужной стороне ленты.

---

## Integration into your Flask app


- В `/chat`:
  1. Загрузи/создай `LoopState`.
  2. Вызови `handle_user_message`.
  3. Верни ответ.

Пример вью-функции (упрощённо):

```python
states = {}

def get_state(session_id):
    if session_id not in states:
        states[session_id] = LoopState(session_id=session_id)
    return states[session_id]

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id") or str(uuid.uuid4())
    user_msg = data.get("message", "").strip()
    state = get_state(session_id)

    def llm_call(prompt: str) -> str:
        # replace with your actual model
        import ollama
        resp = ollama.chat(model="gpt-oss:20b", messages=[{"role":"system","content":prompt}])
        return resp["message"]["content"]

    reply = handle_user_message(state, user_msg, llm_call)
    return jsonify({"response": reply, "session_id": session_id})
```

---

## Extending to humanoid embodiment

- **Continuous motion as flow on the loop:** маппинг `s` в жесты и взгляд.
  - inner: медленные плавные движения, мягкая поза, тёплый тембр.
  - outer: более вертикальная осанка, чёткая артикуляция, жесты-рамки.
- **Prosody blending:** параметризуй голос TTS от `phase` и `depth`.
- **Attention control:** “opposite point” = перевод взгляда на новый якорь в сцене (камера/объект), символизируя переворот.

Псевдо-мэппинг:

```python
def embodiment_params(state: LoopState):
    if state.phase == "inner":
        return {"gesture":"flow", "gaze":"soft_follow", "voice_timbre":"warm", "pace":0.85 - 0.2*state.depth}
    else:
        return {"gesture":"frame", "gaze":"direct", "voice_timbre":"clear", "pace":1.0 + 0.2*state.depth}
```

---

## What you get from this design

- Не “режимы”, а непрерывное сознание с естественной сменой ракурса.
- Память, которая всегда приносит “другую сторону” — встроенный инсайт.
- Мягкая адаптация к эмоциональным петлям без ломки тона.
- Готовность к телесному воплощению: тот же параметр `s` рулит и речью, и движением.


