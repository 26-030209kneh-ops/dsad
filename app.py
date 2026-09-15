import random
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# 페이지 설정
st.set_page_config(
    page_title="Streamlit Snake Game", page_icon="🐍", layout="centered"
)

st.title("🐍 키보드 방향키 뱀 게임")
st.markdown(
    "👉 **주의:** 게임 화면 아래의 빈 공간을 마우스로 **한 번 클릭**한 뒤, 키보드 **방향키**를 누르세요!"
)

# 게임판 크기 설정
WIDTH = 15
HEIGHT = 15

# 세션 상태 초기화
if "snake" not in st.session_state:
    st.session_state.snake = [[7, 7], [7, 8], [7, 9]]
    st.session_state.direction = "UP"
    st.session_state.apple = [
        random.randint(0, WIDTH - 1),
        random.randint(0, HEIGHT - 1),
    ]
    st.session_state.score = 0
    st.session_state.high_score = 0
    st.session_state.game_over = False
    st.session_state.speed = 500  # 속도 설정 (밀리초)

# URL 쿼리 스트링을 통해 자바스크립트와 파이썬 통신
query_params = st.query_params
if "key" in query_params:
    pressed_key = query_params["key"]
    current_dir = st.session_state.direction
    DANGER_TURNS = {
        ("UP", "DOWN"),
        ("DOWN", "UP"),
        ("LEFT", "RIGHT"),
        ("RIGHT", "LEFT"),
    }

    new_dir = current_dir
    if pressed_key == "ArrowUp" and current_dir != "DOWN":
        new_dir = "UP"
    elif pressed_key == "ArrowDown" and current_dir != "UP":
        new_dir = "DOWN"
    elif pressed_key == "ArrowLeft" and current_dir != "RIGHT":
        new_dir = "LEFT"
    elif pressed_key == "ArrowRight" and current_dir != "LEFT":
        new_dir = "RIGHT"

    st.session_state.direction = new_dir


# 게임 리셋 함수
def reset_game():
    st.session_state.snake = [[7, 7], [7, 8], [7, 9]]
    st.session_state.direction = "UP"
    st.session_state.apple = [
        random.randint(0, WIDTH - 1),
        random.randint(0, HEIGHT - 1),
    ]
    if st.session_state.score > st.session_state.high_score:
        st.session_state.high_score = st.session_state.score
    st.session_state.score = 0
    st.session_state.game_over = False


# 자바스크립트로 키보드 방향키 입력 감지 컴포넌트
components.html(
    """
    <div tabindex="0" id="keyboard-listener" style="width: 100%; height: 40px; background-color: #f0f2f6; display: flex; align-items: center; justify-content: center; border-radius: 5px; outline: none; font-weight: bold; color: #333; cursor: pointer;">
        🎮 [이 박스를 클릭하고 방향키를 누르세요]
    </div>
    <script>
        const box = document.getElementById('keyboard-listener');
        box.focus();
        
        window.addEventListener('keydown', (e) => {
            if(["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) {
                e.preventDefault(); // 화면 스크롤 방지
                // 스트리밋 주소창(Query Parameter)을 조작하여 파이썬으로 키값 전달
                const url = new URL(window.parent.location.href);
                url.searchParams.set('key', e.key);
                window.parent.history.replaceState({}, '', url);
                
                // 페이지 강제 새로고침 트리거를 위한 이벤트 전파
                const event = new Event('popstate');
                window.parent.dispatchEvent(event);
            }
        });
    </script>
    """,
    height=50,
)

# 자동 새로고침 루프 (게임 진행 중)
if not st.session_state.game_over:
    st_autorefresh(
        interval=st.session_state.speed, limit=None, key="snake_loop"
    )

    head = list(st.session_state.snake[0])
    if st.session_state.direction == "UP":
        head[1] -= 1
    elif st.session_state.direction == "DOWN":
        head[1] += 1
    elif st.session_state.direction == "LEFT":
        head[0] -= 1
    elif st.session_state.direction == "RIGHT":
        head[0] += 1

    # 충돌 체크
    if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
        st.session_state.game_over = True
    elif head in st.session_state.snake:
        st.session_state.game_over = True
    else:
        st.session_state.snake.insert(0, head)
        if head == st.session_state.apple:
            st.session_state.score += 10
            while True:
                new_apple = [
                    random.randint(0, WIDTH - 1),
                    random.randint(0, HEIGHT - 1),
                ]
                if new_apple not in st.session_state.snake:
                    st.session_state.apple = new_apple
                    break
        else:
            st.session_state.snake.pop()

# 점수판
col_s1, col_s2 = st.columns(2)
col_s1.metric("현재 점수", st.session_state.score)
col_s2.metric("최고 기록", st.session_state.high_score)

# 보드 렌더링
board = [["⬜" for _ in range(WIDTH)] for _ in range(HEIGHT)]
ax, ay = st.session_state.apple
board[ay][ax] = "🍎"

for i, segment in enumerate(st.session_state.snake):
    sx, sy = segment
    if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
        board[sy][sx] = "🟢" if i == 0 else "🟩"

board_str = "\n".join(["".join(row) for row in board])
st.markdown(
    f"<div style='text-align: center; font-size: 24px; line-height: 1.2;'>{board_str.replace('\n', '<br>')}</div>",
    unsafe_allow_html=True,
)

# 게임 오버 처리
if st.session_state.game_over:
    st.error("💀 게임 오버! 벽이나 몸에 부딪혔습니다.")
    if st.button("🔄 다시 시작하기", use_container_width=True):
        reset_game()
        st.rerun()
