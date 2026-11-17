"""A chatbot that can read the warehouse data, and draw it.

Run it from inside streamlit-dev/lecture19:

    docker compose up -d

Then open http://localhost:8507, put your key and endpoint in the sidebar,
and ask something like "which carrier shipped the most orders?".

Two columns. The chat is on the left, the chart on the right. The model
never touches the data itself. It asks the MCP server for numbers, and this
file draws them with the same chart calls we used in Lectures 16 to 18.
"""
import json

import streamlit as st
from openai import OpenAI

import mcp_client

st.set_page_config(page_title="Warehouse Chat", layout="wide")

INSTRUCTIONS = """You answer questions about a warehouse.

You cannot see the data, so use the tools every time. Call columns first if
you are unsure of a name, then call summarize. Never give a number you did
not get from a tool.

You do not draw anything. The chart is drawn from your summarize call, so
call it whenever a chart is wanted, even if the same numbers already came up
earlier in this conversation. Talking about a chart does not make one.

Say what the rows show in one or two sentences. Do not list them back, as
the user can already see them.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chart" not in st.session_state:
    st.session_state.chart = None


with st.sidebar:
    st.title("IEM 4723: LLM API Endpoint Credentials")
    base_url = st.text_input("Endpoint", value="https://api-cypress-ai.disyslab.dev/v1")
    api_key = st.text_input("Key", type="password")
    model = st.selectbox("Choose Your Model",("qwen3-coder-next","qwen3.6-35b-nonthink")) #st.text_input("Model", value="qwen3-coder-next")

    st.divider()
    use_tools = st.checkbox("Let the model use the tools", value=True)
    st.caption("Turn this off to see what the model says when it cannot "
               "read the data.")

    if st.button("Clear the chat"):
        st.session_state.messages = []
        st.session_state.chart = None

if not api_key:
    st.info("Put your key in the sidebar to start.")
    st.stop()

client = OpenAI(base_url=base_url, api_key=api_key)


# This one goes at the top level and not inside a column. Streamlit pins it to
# the bottom of the page when you call it out here. Called inside the column it
# is drawn where it sits, which puts it above everything this run adds below.
question = st.chat_input("Ask about the warehouse data")

left, right = st.columns(2)

with left:
    st.subheader("Chat")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with left:
        with st.chat_message("user"):
            st.markdown(question)

    # Everything the model gets to see this turn.
    conversation = [{"role": "system", "content": INSTRUCTIONS}]
    for message in st.session_state.messages:
        conversation.append({"role": message["role"],
                             "content": message["content"]})

    answer = ""
    try:
        tools = None
        if use_tools:
            tools = mcp_client.list_tools()

        # The model does not run anything. It asks for a tool and stops, and
        # it is this file that goes and runs it and asks again. One question
        # usually takes two turns, because it looks up the column names
        # before it summarises anything. Four is plenty.
        for turn in range(10):
            if tools:
                reply = client.chat.completions.create(
                    model=model, messages=conversation, tools=tools)
            else:
                reply = client.chat.completions.create(
                    model=model, messages=conversation)

            sent_back = reply.choices[0].message

            # Nothing more it wants, so this is the answer.
            if not sent_back.tool_calls:
                answer = sent_back.content or ""
                break

            # Write down what it asked for, every call, or the next request
            # is rejected for having a question with no answer.
            asked_for = []
            for call in sent_back.tool_calls:
                asked_for.append({
                    "id": call.id,
                    "type": "function",
                    "function": {"name": call.function.name,
                                 "arguments": call.function.arguments},
                })
            conversation.append({"role": "assistant", "tool_calls": asked_for})

            for call in sent_back.tool_calls:
                arguments = json.loads(call.function.arguments)

                with left:
                    with st.chat_message("assistant"):
                        st.caption(f"Calling {call.function.name}")
                        st.code(json.dumps(arguments, indent=2),
                                language="json")

                with st.spinner(f"Running {call.function.name}..."):
                    tool_output = mcp_client.call_tool(call.function.name,
                                                       arguments)

                conversation.append({"role": "tool", "tool_call_id": call.id,
                                     "content": tool_output})

                # Keep it for the right hand column, if there is anything
                # to draw. columns and list_datasets have no rows.
                result = json.loads(tool_output)
                if "rows" in result:
                    st.session_state.chart = {
                        "called": call.function.name,
                        "arguments": arguments,
                        "result": result,
                    }
        else:
            answer = ("I ran out of turns talking to the AI model. "
                      "Try asking a simpler question.")

    except Exception as problem:
        with left:
            st.error(f"That did not work: {problem}")
        st.stop()

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with left:
        with st.chat_message("assistant"):
            st.markdown(answer)


with right:
    st.subheader("Chart")

    if st.session_state.chart is None:
        st.info("Ask a question and whatever the model looks up turns up here.")
    else:
        drawing = st.session_state.chart
        result = drawing["result"]

        st.caption("The model asked for this:")
        st.code(f"{drawing['called']}({json.dumps(drawing['arguments'])})",
                language="python")

        if result["chart"] == "line":
            st.line_chart(result["rows"], x=result["x"], y=result["y"])
        else:
            st.bar_chart(result["rows"], x=result["x"], y=result["y"])

        with st.expander("Show the rows behind this"):
            st.dataframe(result["rows"], width="stretch", hide_index=True)
