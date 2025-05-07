import streamlit as st
import openai
import time

# 첫 번째 페이지 제목
st.title("🤖 GPT-4.1-mini Chat - 과제 1")

# 🔑 API Key 입력 및 세션에 저장
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_key

# API Key 입력 후 진행
if st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # 대화 내용 저장
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 사용자 메시지 입력 받기
    user_input = st.text_input("Your question:")

    # 사용자가 메시지를 보내면
    if user_input:
        # 사용자 메시지 전송
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 전체 대화 내용을 전달하여 더 자연스러운 대화 유도
        conversation = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]

        # 모델에 메시지 전송 (최신 API 사용)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # 올바른 모델 이름
                messages=conversation,  # 메시지 목록으로 대화 전달
                max_tokens=150,  # 토큰 수 제한
                n=1,  # 한 번에 하나의 응답을 받기
                stop=None,  # 종료 조건 (옵션)
                temperature=0.7  # 창의성 정도 (옵션)
            )

            assistant_response = response['choices'][0]['message']['content']  # 응답에서 내용 추출

            # 챗봇의 응답을 대화 내용에 추가
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        except Exception as e:
            st.error(f"Error: {e}")

    # 대화 내용 표시
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.write(f"**You**: {message['content']}")
        else:
            st.write(f"**Assistant**: {message['content']}")

else:
    st.info("Please enter your OpenAI API key to start chatting.")
