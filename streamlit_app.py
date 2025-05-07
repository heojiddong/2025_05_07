import streamlit as st
import openai

st.set_page_config(page_title="과제 1 - GPT API 테스트", page_icon="🤖")
st.title("🤖 GPT-4 Chat - 과제 1")

# API Key 입력
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("OpenAI API 키를 입력하세요", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_key

# 메시지 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 키가 있으면 대화 시작
if st.session_state.api_key:
    client = openai.OpenAI(api_key=st.session_state.api_key)

    # 사용자 질문 입력창
    user_input = st.text_input("질문을 입력하세요:")

    if st.button("보내기") and user_input:
        # 질문 저장 및 출력
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.write(f"**🙋‍♂️ You:** {user_input}")

        # 응답 요청
        with st.spinner("GPT의 답변을 기다리는 중..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                )
                reply = response.choices[0].message.content
                st.write(f"**🤖 GPT:** {reply}")
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"에러 발생: {e}")
else:
    st.info("API 키를 입력하세요.")
