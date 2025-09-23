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
