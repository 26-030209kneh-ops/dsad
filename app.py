import random
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# 페이지 설정
st.set_page_config(
    page_title="Streamlit Snake Game", page_icon="🐍", layout="centered"
)

st.title("🐍 스트리밋 뱀 게임 (Snake Game)")
st.markdown("아래 방향 버튼을 눌러 뱀을 조작하고 **사과(🍎)**를 먹어 길어지세요!")

# 게임판 크기 설정
WIDTH = 15
HEIGHT = 15

# 세션 상태 초기화 (게임 데이터 유지)
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
    st.session_state.speed = 400  # 밀리초(ms) 단위 이동 속도 (낮을수록 빠름)


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


# 게임이 진행 중일 때 자동 새로고침 루프 실행
if not st.session_state.game_over:
    st_autorefresh(
        interval=st.session_state.speed, limit=None, key="snake_loop"
    )

    # 머리 이동 좌표 계산
    head = list(st.session_state.snake[0])
    if st.session_state.direction == "UP":
        head[1] -= 1
    elif st.session_state.direction == "DOWN":
        head[1] += 1
    elif st.session_state.direction == "LEFT":
        head[0] -= 1
    elif st.session_state.direction == "RIGHT":
        head[0] += 1

    # 벽 충돌 체크
    if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
        st.session_state.game_over = True
    # 자기 몸 충돌 체크
    elif head in st.session_state.snake:
        st.session_state.game_over = True
    else:
        st.session_state.snake.insert(0, head)
        # 사과 먹기 체크
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

# 점수판 표시
col_s1, col_s2 = st.columns(2)
col_s1.metric("현재 점수", st.session_state.score)
col_s2.metric("최고 기록", st.session_state.high_score)

# 방향 전환 함수 (180도 역주행 방지)
DANGER_TURNS = {
    ("UP", "DOWN"),
    ("DOWN", "UP"),
    ("LEFT", "RIGHT"),
    ("RIGHT", "LEFT"),
}


def set_direction(new_dir):
    if (st.session_state.direction, new_dir) not in DANGER_TURNS:
        st.session_state.direction = new_dir


# 조작 버튼 UI
st.markdown("### 🕹️ 조작 패널")
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("⬆️ 위로", use_container_width=True):
        set_direction("UP")

col4, col5, col6 = st.columns([1, 1, 1])
with col4:
    if st.button("⬅️ 왼쪽", use_container_width=True):
        set_direction("LEFT")
with col6:
    if st.button("➡️ 오른쪽", use_container_width=True):
        set_direction("RIGHT")

col7, col8, col9 = st.columns([1, 1, 1])
with col8:
    if st.button("⬇️ 아래로", use_container_width=True):
        set_direction("DOWN")

# 게임 보드판 렌더링 (이모지 활용)
board = [["⬜" for _ in range(WIDTH)] for _ in range(HEIGHT)]

# 사과 위치 표시
ax, ay = st.session_state.apple
if 0 <= ax < WIDTH and 0 <= ay < HEIGHT:
    board[ay][ax] = "🍎"

# 뱀 위치 표시 (머리는 파란색/초록색 구분을 위해 다르게 줄 수도 있음)
for i, segment in enumerate(st.session_state.snake):
    sx, sy = segment
    if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
        if i == 0:
            board[sy][sx] = "🟢"  # 뱀 머리
        else:
            board[sy][sx] = "🟩"  # 뱀 몸통

# 화면에 보드 출력
board_str = "\n".join(["".join(row) for row in board])
st.markdown(
    f"<div style='text-align: center; font-size: 24px; line-height: 1.2;'>{board_str.replace('\n', '<br>')}</div>",
    unsafe_allow_html=True,
)

# 게임 오버 화면 처리
if st.session_state.game_over:
    st.error("💀 게임 오버! 벽이나 몸에 부딪혔습니다.")
    if st.button("🔄 다시 시작하기", use_container_width=True):
        reset_game()
        st.rerun()
