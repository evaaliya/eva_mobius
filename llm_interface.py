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
