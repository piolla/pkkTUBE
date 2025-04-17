import sys
import asyncio
import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

HISTORY_DIR = "chat_histories"
os.makedirs(HISTORY_DIR, exist_ok=True)

# -------------------------
# 💾 대화 기록 파일 입출력
# -------------------------
def get_today_filename():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(HISTORY_DIR, f"chat_{today}.json")

def save_chat_history(history):
    with open(get_today_filename(), "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_chat_history(filename=None):
    try:
        file = filename or get_today_filename()
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return []

def list_chat_history_files():
    return sorted([f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")])

def reset_chat_history():
    st.session_state.chat_history = []
    save_chat_history([])

# -------------------------
# MCP 서버 설정 함수
# -------------------------
async def setup_mcp_servers():
    servers = []
    with open('pkkTube.json', 'r') as f:
        config = json.load(f)

    for server_name, server_config in config.get('pkkServers', {}).items():
        mcp_server = MCPServerStdio(
            params={
                "command": server_config.get("command"),
                "args": server_config.get("args", [])
            },
            cache_tools_list=True
        )
        await mcp_server.connect()
        servers.append(mcp_server)

    return servers

# -------------------------
# Agent 설정 함수
# -------------------------
async def setup_agent(selected_model):
    mcp_servers = await setup_mcp_servers()
    agent = Agent(
        name='Assistant',
        instructions="You are a helpful assistant. Always maintain memory of the conversation history and remember the user's name is john young.",
        model=selected_model,
        mcp_servers=mcp_servers
    )
    return agent, mcp_servers

# -------------------------
# 메시지 처리 함수
# -------------------------
async def process_user_message(selected_model):
    agent, mcp_servers = await setup_agent(selected_model)
    messages = st.session_state.chat_history

    result = Runner.run_streamed(agent, input=messages)

    response_text = ""
    placeholder = st.empty()

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            response_text += event.data.delta or ""
            with placeholder.container():
                with st.chat_message("assistant"):
                    st.markdown(response_text)

        elif event.type == "run_item_stream_event":
            item = event.item
            if item.type == "tool_call_item":
                tool_name = item.raw_item.name
                st.toast(f"\U0001F6E0 도구 사용: `{tool_name}`")

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response_text
    })
    save_chat_history(st.session_state.chat_history)

    for server in mcp_servers:
        await server.__aexit__(None, None, None)

# -------------------------
# Streamlit UI 메인
# -------------------------
def main():
    st.set_page_config(page_title="\U0001F3A5 유튜브 분석 에이전트", page_icon="\U0001F916")

    # 사이드바: 모델 선택, 히스토리 선택
    st.sidebar.header("설정")
    selected_model = st.sidebar.selectbox("OpenAI 모델 선택", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"])

    history_files = list_chat_history_files()
    selected_file = st.sidebar.selectbox("대화 일자 선택", history_files[::-1])

    if st.sidebar.button("선택한 기록 불러오기"):
        st.session_state.chat_history = load_chat_history(os.path.join(HISTORY_DIR, selected_file))

    if st.sidebar.button("\U0001F6AB 대화 초기화"):
        reset_chat_history()
        st.rerun()

    # 대화 기록 초기화 (최초 실행 시)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = load_chat_history()

    st.title("\U0001F3A5 유튜브 콘텐츠 분석 & 대화 에이전트")
    st.caption("예: '이 영상 자막 알려줘', '채널 최근 영상 요약해줘', 'exit' 입력 시 종료")

    # 대화 기록 출력
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # 사용자 입력
    user_input = st.chat_input("메시지를 입력하세요")
    if user_input:
        if user_input.lower().strip() in ["exit", "종료", "quit"]:
            st.warning("세션을 종료합니다. 다음 실행 시 대화는 초기화됩니다.")
            reset_chat_history()
            st.rerun()

        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        asyncio.run(process_user_message(selected_model))

if __name__ == "__main__":
    main()
