import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import requests

# 1. Cấu hình & Khởi tạo 
st.set_page_config(page_title="Smart Suggestion System", layout="wide", page_icon="🌟")
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
if 'theme' not in st.session_state: st.session_state.theme = 'dark'
if 'user' not in st.session_state: st.session_state.user = None

BACKEND_URL = "http://localhost:8000"

# 2. Ngôn ngữ
text = {
    'vi': {
        'title': " ENTERTAINMENT", 'sub': "Gợi ý điểm vui chơi • Group T04",
        'input_header': "####  Hôm nay bạn muốn trải nghiệm điều gì?",
        'input_label': "Chia sẻ tâm tư của bạn...", 'btn_send': " Gửi tâm tư",
        'loading': " AI đang kết nối Backend...", 'settings': "Cài đặt hệ thống"
    },
    'en': {
        'title': " ENTERTAINMENT", 'sub': "Suggest places • Group T04",
        'input_header': "####  What's on your mind?",
        'input_label': "Share your thoughts...", 'btn_send': " Send request",
        'loading': " Connecting to Backend...", 'settings': "System Settings"
    }
}
L = text[st.session_state.lang]

# 3. CSS 
st.markdown("<style>.stButton>button { width: 100%; border-radius: 12px; border: 1px solid #ff4b4b; color: #ff4b4b; }</style>", unsafe_allow_html=True)

# 4. Thanh điều hướng & Login 
nav_col, setting_col = st.columns([4, 1])
with setting_col:
    with st.popover("⚙️ " + L['settings']):
        if not st.session_state.user:
            email = st.text_input("Firebase Email")
            if st.button("Đăng nhập"):
                st.session_state.user = email
                st.rerun()
        else:
            st.write(f"Chào, **{st.session_state.user}**")
            if st.button("Đăng xuất"): st.session_state.user = None; st.rerun()

# 5. Nội dung chính
st.title(L['title'])
st.caption(L['sub'])
st.markdown("---")

col_left, col_right = st.columns([1.3, 1], gap="large")

with col_left:
    with st.container(border=True):
        st.markdown(L['input_header'])
        u_input = st.text_area(L['input_label'], height=130)
        if st.button(L['btn_send']):
            if st.session_state.user:
                with st.status(L['loading']):
                    res = requests.post(f"{BACKEND_URL}/suggestions", json={"user_id": st.session_state.user, "message": u_input})
                    if res.status_code == 200:
                        st.success(res.json()['result'])
                        time.sleep(1)
                        st.rerun()
                    else: st.error("Lỗi kết nối Backend!")
            else: st.warning("Vui lòng đăng nhập trước!")

    map_data = pd.DataFrame({'lat': [10.776, 10.802, 10.785], 'lon': [106.701, 106.695, 106.690]})
    st.pydeck_chart(pdk.Deck(layers=[pdk.Layer("ScatterplotLayer", map_data, get_position='[lon, lat]', get_color='[255, 75, 75]', get_radius=200)], initial_view_state=pdk.ViewState(latitude=10.788, longitude=106.695, zoom=12)))

with col_right:
    st.subheader("🕒 Lịch sử trải nghiệm (Firestore)") # Yêu cầu 3.5 [cite: 78, 100]
    if st.session_state.user:
        history_res = requests.get(f"{BACKEND_URL}/history/{st.session_state.user}")
        if history_res.status_code == 200:
            for item in history_res.json()['history']:
                with st.expander(f"Bạn đã hỏi: {item['user_input'][:20]}..."):
                    st.write(item['ai_output'])
                    st.caption(f"Lưu lúc: {item['timestamp']}")
    else: st.info("Đăng nhập để xem lịch sử")