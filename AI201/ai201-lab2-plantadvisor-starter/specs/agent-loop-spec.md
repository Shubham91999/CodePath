# Spec: `run_agent()`

**File:** `agent.py`
**Status:** Partially pre-filled — complete the two blank fields before implementing

---

## Purpose

Orchestrate a single conversational turn for the Plant Advisor agent. Given a user message and the conversation history, call the LLM with available tools, execute any tool calls the LLM requests, and return the final text response.

This is the core of what makes Plant Advisor an *agent* rather than a simple chatbot: the ability to decide which tools to call, use their results to inform its response, and loop until it has everything it needs.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_message` | `str` | The user's current message |
| `history` | `list` | Gradio conversation history — list of `[user_msg, assistant_msg]` pairs |

**Output:** `str`

The agent's final text response for this turn. Should never be empty — if something goes wrong, return a user-readable fallback message.

---

## Design Decisions

*Read `specs/system-design.md` (especially the "How the Groq Tool Calling API Works" section) before reviewing these. Complete the two blank fields before writing any code.*

---

### Messages list structure

The messages list must start with the system prompt, then replay the conversation
history, then add the new user message. Gradio history is a list of `[user, assistant]`
pairs — convert each pair to two API-format dicts:

```python
messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for user_msg, assistant_msg in history:
    messages.append({"role": "user", "content": user_msg})
    if assistant_msg:
        messages.append({"role": "assistant", "content": assistant_msg})

messages.append({"role": "user", "content": user_message})
```

---

### Initial LLM call

Pass the model, the messages list, the tool definitions, and `tool_choice="auto"`
so the LLM can decide whether to call a tool or respond directly:

```python
response = client.chat.completions.create(
    model=LLM_MODEL,
    messages=messages,
    tools=TOOL_DEFINITIONS,
    tool_choice="auto",
)
```

---

### Detecting tool calls in the response

The response object has a `choices` list. Index 0 gives the assistant message.
Check its `tool_calls` attribute — if it's truthy, the LLM wants to call tools:

```python
assistant_message = response.choices[0].message

if not assistant_message.tool_calls:
    # No tool calls — LLM has a final answer
    ...
```

---

### Appending the assistant message

When there are tool calls, append the full assistant message object to `messages`
**before** appending any tool results. The API requires this ordering — a tool
result message must immediately follow the assistant message that requested it:

```python
messages.append(assistant_message)  # must come first
```

---

### Executing and appending tool results

For each tool call, extract the name and arguments, call `dispatch_tool()`, and
append the result as a `"tool"` role message. The `tool_call_id` links this result
back to the specific tool call that requested it:

```python
for tool_call in assistant_message.tool_calls:
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)
    tool_result = dispatch_tool(tool_name, tool_args)

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": tool_result,
    })
```

---

### Loop termination conditions

*The loop should stop when: (a) the LLM returns a response with no tool calls, OR (b) the MAX_TOOL_ROUNDS limit is reached. Describe how you will detect each condition and what you will return in each case.*

```
The tool-calling loop runs inside `for _ in range(MAX_TOOL_ROUNDS)` — this bounds it
so it can never spin forever.

(a) No tool calls — the normal exit. After each LLM call, inspect
    `response.choices[0].message.tool_calls`. If it is falsy (None or empty list),
    the LLM has produced its final answer: return `message.content` (falling back to a
    readable default if content is somehow empty/None).

(b) MAX_TOOL_ROUNDS reached — the safety exit. If every round is consumed and the LLM
    is STILL requesting tools, the for-loop ends. At that point make one final LLM call
    with tools disabled (tool_choice="none") so the model is forced to answer in text
    rather than request another tool. Return that content, or a user-readable fallback
    if even that is empty.

The entire turn is wrapped in try/except: a malformed tool-argument JSON, a None content,
or an API/network error returns a friendly fallback string instead of crashing the UI.
Output is guaranteed non-empty in every path.
```

---

### Extracting the final text response

*Once the loop exits because there are no more tool calls, how do you extract the text content from the response object? What field holds the string you should return?*

```
The text lives in `response.choices[0].message.content` (a string).

Access path: the response has a `choices` list → index [0] is the top choice →
`.message` is the assistant message → `.content` is the text to return.

Caveat: `content` is `None` whenever the assistant message carried only tool_calls and
no text. Since I only read content on the no-tool-calls exit path, it should be a string
there — but I still guard with `content or "<fallback>"` so the function can never return
None or "".
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Trace of a working agent turn (what tools were called and in what order):**

```
Query: "How should I care for my calathea?"
Round 1 tool call: lookup_plant({"plant_name": "calathea"}) → found: True
Round 2 tool call: (none — LLM had enough context after the plant lookup and answered)
Final response: Practical calathea care (water every 1–2 weeks, keep soil moist,
               use filtered water, high humidity), grounded in the lookup result.

Note: a season-specific query like "How often should I water my snake plant in winter?"
DOES call both tools in one turn — lookup_plant({"plant_name": "snake plant"}) then
get_seasonal_conditions({"season": "winter"}) — because the question needs both the
plant data and the seasonal adjustment to answer.
```

**What happens when you ask about a plant that isn't in the database?**

```
Asked "How do I care for my bonsai tree?" — the LLM calls lookup_plant({"plant_name":
"bonsai tree"}), which returns {"found": False, ...} with the not-found message. The
agent reads that message and degrades gracefully: it tells the user the plant isn't in
the database, notes that bonsai is a technique rather than a single species, and offers
general guidance — exactly the behavior the not-found message was written to produce.
```

**One thing about the tool call API that surprised you:**

```
The `arguments` field is a raw JSON STRING the model generates, so it can be malformed
or unexpected — not a guaranteed dict. Two real cases appeared in testing:
  1. For a no-argument call, llama-3.3 sent arguments = "null", and json.loads("null")
     returns Python None — which then crashed dispatch_tool's tool_args.get(). Fix: in
     run_agent, normalize empty/"null"/non-dict parses to {} before dispatching.
  2. Occasionally the model emitted a malformed "<function=lookup_plant={...}</function>"
     blob instead of a structured tool_call, which Groq rejects with tool_use_failed (400).
     This is intermittent (succeeds on retry) and is caught by the try/except fallback.
Lesson: never trust tool-call arguments to be clean — validate before dispatching.
```
