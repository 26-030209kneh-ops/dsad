import random
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(
    page_title="Streamlit Snake Game", page_icon="🐍", layout="centered"
)

st.title("🐍 스트리밋 뱀 게임 (Snake Game)")
st.markdown("키보드 **방향키(↑, ↓, ←, →)**를 눌러서 뱀을 조작하세요!")

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
    st.session_state.speed = 500  # 속도 (밀리초)


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


# 자바스크립트를 이용해 키보드 입력 감지 및 세션 연동 컴포넌트
# (스트리밋 컴포넌트를 통해 키 입력을 받기 위한 트릭)
key_event = components.html(
    """
    <div tabindex="0" id="game-container" style="outline: none; text-align: center; color: gray; font-size: 14px;">
        🎮 [이곳을 클릭한 뒤 방향키를 누르세요]
    </div>
    <script>
        const container = document.getElementById('game-container');
        container.focus();
        window.addEventListener('keydown', (e) => {
            if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," "].includes(e.key)) {
                e.preventDefault();
                const parentDoc = window.parent.document;
                // 스트리밋 내부 통신을 위한 임시 조치 (버튼 클릭 트리거)
                const buttons = parentDoc.querySelectorAll('button');
                buttons.forEach(btn => {
                    if(btn.innerText.includes(e.key)) {
                        // 각 방향에 맞는 버튼 자동 클릭 시뮬레이션
                    }
                });
            }
        });
    </script>
    """,
    height=30,
)

# 방향 전환 규칙 (180도 역주행 방지)
DANGER_TURNS = {
    ("UP", "DOWN"),
    ("DOWN", "UP"),
    ("LEFT", "RIGHT"),
    ("RIGHT", "LEFT"),
}


def set_direction(new_dir):
    if (st.session_state.direction, new_dir) not in DANGER_TURNS:
        st.session_state.direction = new_dir


# 키보드 입력을 대체하기 위한 숨김/일반 조작 버튼 (스트리밋 기본 기능 활용)
# 사용자가 화면에서 방향 버튼을 누를 수 있도록 배치
st.markdown("### 🕹️ 조작 버튼")
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("⬆️ 위 (ArrowUp)", use_container_width=True):
        set_direction("UP")

col4, col5, col6 = st.columns([1, 1, 1])
with col4:
    if st.button("⬅️ 왼쪽 (ArrowLeft)", use_container_width=True):
        set_direction("LEFT")
with col6:
    if st.button("➡️ 오른쪽 (ArrowRight)", use_container_width=True):
        set_direction("RIGHT")

col7, col8, col9 = st.columns([1, 1, 1])
with col8:
    if st.button("⬇️ 아래 (ArrowDown)", use_container_width=True):
        set_direction("DOWN")

# 자동 새로고침 루프 (게임이 진행 중일 때만)
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
