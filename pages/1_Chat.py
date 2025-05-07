import streamlit as st
import openai
import time

# Chat 페이지 타이틀
st.title("🗨️ Chat with GPT-4.1-mini")

# 🔑 API Key 세션 상태 확인
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# 세션에 저장된 API Key을 기반으로 OpenAI API 설정
if st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # 사용자의 대화와 GPT의 응답을 저장할 리스트
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 사용자 입력
    user_input = st.text_input("Your message:")

    # Send 버튼
    submit_button = st.button("Send")

    if submit_button and user_input:
        # 사용자 메시지 저장
        st.session_state.messages.append({"role": "user", "content": user_input})

        # GPT-4.1-mini에게 응답 요청
        try:
            response = openai.chat_completions.create(
                model="gpt-4.1-mini",
                messages=st.session_state.messages
            )

            assistant_reply = response['choices'][0]['message']['content']

            # GPT의 응답을 세션에 저장
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            st.error(f"Error: {e}")

    # 대화 내용 출력
    if st.session_state.messages:
        for msg in st.session_state.messages:
            if msg['role'] == "user":
                st.write(f"**User:** {msg['content']}")
            elif msg['role'] == "assistant":
                st.write(f"**GPT:** {msg['content']}")

    # Clear 버튼을 눌렀을 때 대화 내용 삭제
    if st.button("Clear"):
        st.session_state.messages = []

else:
    st.info("API Key를 입력하면 대화를 시작할 수 있어요.")
