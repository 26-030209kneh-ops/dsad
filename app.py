import random
import time
import numpy as np
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="Streamlit Tetris", page_icon="🎮", layout="centered")

# CSS 스타일링 (게임판 시인성 향상)
st.markdown(
    """
    <style>
    .stButton button {
        width: 100%;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 게임 설정 상수
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# 테트로미노 모양과 색상 정의 (0: 빈칸, 1~7: 블록 종류)
SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [
        [1, 1],
        [1, 1],
    ],
    "T": [
        [0, 1, 0],
        [1, 1, 1],
    ],
    "S": [
        [0, 1, 1],
        [1, 1, 0],
    ],
    "Z": [
        [1, 1, 0],
        [0, 1, 1],
    ],
    "J": [
        [1, 0, 0],
        [1, 1, 1],
    ],
    "L": [
        [0, 0, 1],
        [1, 1, 1],
    ],
}

EMOJIS = {
    0: "⬛",  # 빈 칸
    1: "🟦",  # I
    2: "🟨",  # O
    3: "🟪",  # T
    4: "🟩",  # S
    5: "🟥",  # Z
    6: "🟧",  # J
    7: "🟫",  # L
}


# 세션 상태 초기화
def init_game():
    st.session_state.board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
    st.session_state.score = 0
    st.session_state.level = 1
    st.session_state.game_over = False
    st.session_state.paused = False
    st.session_state.current_piece = spawn_piece()
    st.session_state.next_piece = spawn_piece()


def spawn_piece():
    shape_name = random.choice(list(SHAPES.keys()))
    return {
        "shape": SHAPES[shape_name],
        "name": shape_name,
        "x": BOARD_WIDTH // 2 - len(SHAPES[shape_name][0]) // 2,
        "y": 0,
        "color_id": list(SHAPES.keys()).index(shape_name) + 1,
    }


if "board" not in st.session_state:
    init_game()


# 충돌 검사 함수
def check_collision(board, piece, dx, dy, rotated_shape=None):
    shape = rotated_shape if rotated_shape is not None else piece["shape"]
    px = piece["x"] + dx
    py = piece["y"] + dy

    for r_idx, row in enumerate(shape):
        for c_idx, val in enumerate(row):
            if val:
                nx = px + c_idx
                ny = py + r_idx
                if (
                    nx < 0
                    or nx >= BOARD_WIDTH
                    or ny >= BOARD_HEIGHT
                    or (ny >= 0 and board[ny][nx] != 0)
                ):
                    return True
    return False


# 블록 고정 및 줄 제거
def lock_piece():
    board = st.session_state.board
    piece = st.session_state.current_piece
    for r_idx, row in enumerate(piece["shape"]):
        for c_idx, val in enumerate(row):
            if val:
                ny = piece["y"] + r_idx
                nx = piece["x"] + c_idx
                if ny >= 0:
                    board[ny][nx] = piece["color_id"]

    # 줄 완성 체크 및 제거
    lines_cleared = 0
    new_board = []
    for row in board:
        if all(row != 0):
            lines_cleared += 1
        else:
            new_board.append(row)

    for _ in range(lines_cleared):
        new_board.insert(0, np.zeros(BOARD_WIDTH, dtype=int))

    st.session_state.board = np.array(new_board)

    # 점수 계산 및 레벨 업
    if lines_cleared > 0:
        st.session_state.score += (lines_cleared**2) * 100 * st.session_state.level
        st.session_state.level = st.session_state.score // 1000 + 1

    # 다음 블록 가져오기
    st.session_state.current_piece = st.session_state.next_piece
    st.session_state.next_piece = spawn_piece()

    # 게임 오버 체크
    if check_collision(
        st.session_state.board, st.session_state.current_piece, 0, 0
    ):
        st.session_state.game_over = True


# UI 레이아웃 구성
st.title("🕹️ Streamlit 테트리스 게임")
st.write("버튼을 눌러 블록을 조작하고 최고 기록을 달성해 보세요!")

col_game, col_ctrl = st.col([2, 1])

with col_game:
    # 화면에 렌더링할 보드 복사
    render_board = st.session_state.board.copy()
    p = st.session_state.current_piece
    if not st.session_state.game_over:
        for r_idx, row in enumerate(p["shape"]):
            for c_idx, val in enumerate(row):
                if val:
                    ny = p["y"] + r_idx
                    nx = p["x"] + c_idx
                    if 0 <= ny < BOARD_HEIGHT and 0 <= nx < BOARD_WIDTH:
                        render_board[ny][nx] = p["color_id"]

    # 보드 출력 (이모지 활용)
    board_str = "\n".join(
        ["".join([EMOJIS[cell] for cell in row]) for row in render_board]
    )
    st.text(board_str)

with col_ctrl:
    st.markdown(f"### 📊 점수: {st.session_state.score}")
    st.markdown(f"### 🔥 레벨: {st.session_state.level}")

    st.markdown("---")
    st.markdown("### ⏭️ 다음 블록")
    next_p = st.session_state.next_piece
    next_str = "\n".join(
        [
            "".join([EMOJIS[next_p["color_id"] if val else 0] for val in row])
            for row in next_p["shape"]
        ]
    )
    st.text(next_str)

    st.markdown("---")
    if st.button("🔄 게임 재시작"):
        init_game()
        st.rerun()

# 컨트롤러 버튼 (좌, 우, 회전, 하강)
if not st.session_state.game_over and not st.session_state.paused:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("⬅️ 좌") and not check_collision(
            st.session_state.board, st.session_state.current_piece, -1, 0
        ):
            st.session_state.current_piece["x"] -= 1
            st.rerun()
    with c2:
        if st.button("🔄 회전"):
            rotated = [
                [
                    st.session_state.current_piece["shape"][r][c]
                    for r in range(
                        len(st.session_state.current_piece["shape"]) - 1, -1, -1
                    )
                ]
                for c in range(len(st.session_state.current_piece["shape"][0]))
            ]
            if not check_collision(
                st.session_state.board,
                st.session_state.current_piece,
                0,
                0,
                rotated,
            ):
                st.session_state.current_piece["shape"] = rotated
                st.rerun()
    with c3:
        if st.button("➡️ 우") and not check_collision(
            st.session_state.board, st.session_state.current_piece, 1, 0
        ):
            st.session_state.current_piece["x"] += 1
            st.rerun()
    with c4:
        if st.button("⬇️ 하강"):
            if not check_collision(
                st.session_state.board, st.session_state.current_piece, 0, 1
            ):
                st.session_state.current_piece["y"] += 1
            else:
                lock_piece()
            st.rerun()

if st.session_state.game_over:
    st.error("💥 게임 오버! 다시 시작하려면 '게임 재시작' 버튼을 누르세요.")
