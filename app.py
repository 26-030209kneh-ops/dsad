import random
import numpy as np
import streamlit as st

# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="Streamlit Tetris",
    page_icon="🎮",
    layout="centered",
)

# CSS 스타일
st.markdown(
    """
    <style>
    .stButton button {
        width: 100%;
        font-weight: bold;
    }

    .game-title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 게임 설정
# =========================================================
BOARD_WIDTH = 10
BOARD_HEIGHT = 20


# =========================================================
# 테트로미노 모양
# =========================================================
SHAPES = {
    "I": [
        [1, 1, 1, 1]
    ],
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


# 블록별 색상
EMOJIS = {
    0: "⬛",  # 빈칸
    1: "🟦",  # I
    2: "🟨",  # O
    3: "🟪",  # T
    4: "🟩",  # S
    5: "🟥",  # Z
    6: "🟧",  # J
    7: "🟫",  # L
}


# =========================================================
# 블록 생성
# =========================================================
def spawn_piece():
    shape_name = random.choice(list(SHAPES.keys()))

    # 원본 SHAPES가 직접 수정되지 않도록 복사
    shape = [row[:] for row in SHAPES[shape_name]]

    return {
        "shape": shape,
        "name": shape_name,
        "x": BOARD_WIDTH // 2 - len(shape[0]) // 2,
        "y": 0,
        "color_id": list(SHAPES.keys()).index(shape_name) + 1,
    }


# =========================================================
# 게임 초기화
# =========================================================
def init_game():
    st.session_state.board = np.zeros(
        (BOARD_HEIGHT, BOARD_WIDTH),
        dtype=int
    )

    st.session_state.score = 0
    st.session_state.level = 1
    st.session_state.game_over = False
    st.session_state.paused = False

    st.session_state.current_piece = spawn_piece()
    st.session_state.next_piece = spawn_piece()


# =========================================================
# 최초 실행 시 게임 초기화
# =========================================================
if "board" not in st.session_state:
    init_game()


# =========================================================
# 충돌 검사
# =========================================================
def check_collision(
    board,
    piece,
    dx=0,
    dy=0,
    rotated_shape=None,
):
    shape = (
        rotated_shape
        if rotated_shape is not None
        else piece["shape"]
    )

    px = piece["x"] + dx
    py = piece["y"] + dy

    for r_idx, row in enumerate(shape):
        for c_idx, value in enumerate(row):

            if value == 0:
                continue

            nx = px + c_idx
            ny = py + r_idx

            # 왼쪽/오른쪽 벽
            if nx < 0 or nx >= BOARD_WIDTH:
                return True

            # 바닥
            if ny >= BOARD_HEIGHT:
                return True

            # 이미 놓여있는 블록과 충돌
            if ny >= 0 and board[ny][nx] != 0:
                return True

    return False


# =========================================================
# 블록 고정 + 줄 제거
# =========================================================
def lock_piece():
    board = st.session_state.board
    piece = st.session_state.current_piece

    # 현재 블록을 보드에 고정
    for r_idx, row in enumerate(piece["shape"]):
        for c_idx, value in enumerate(row):

            if value == 0:
                continue

            ny = piece["y"] + r_idx
            nx = piece["x"] + c_idx

            if (
                0 <= ny < BOARD_HEIGHT
                and 0 <= nx < BOARD_WIDTH
            ):
                board[ny][nx] = piece["color_id"]

    # =====================================================
    # 완성된 줄 찾기
    # =====================================================
    remaining_rows = []
    lines_cleared = 0

    for row in board:
        if np.all(row != 0):
            lines_cleared += 1
        else:
            remaining_rows.append(row)

    # 제거된 줄만큼 위쪽에 빈 줄 추가
    while len(remaining_rows) < BOARD_HEIGHT:
        remaining_rows.insert(
            0,
            np.zeros(BOARD_WIDTH, dtype=int)
        )

    st.session_state.board = np.array(
        remaining_rows,
        dtype=int
    )

    # =====================================================
    # 점수 계산
    # =====================================================
    if lines_cleared > 0:
        st.session_state.score += (
            lines_cleared ** 2
            * 100
            * st.session_state.level
        )

        st.session_state.level = (
            st.session_state.score // 1000
        ) + 1

    # =====================================================
    # 다음 블록 가져오기
    # =====================================================
    st.session_state.current_piece = (
        st.session_state.next_piece
    )

    st.session_state.next_piece = spawn_piece()

    # =====================================================
    # 새 블록이 생성되자마자 충돌하면 게임 오버
    # =====================================================
    if check_collision(
        st.session_state.board,
        st.session_state.current_piece,
        0,
        0,
    ):
        st.session_state.game_over = True


# =========================================================
# 블록 회전
# =========================================================
def rotate_piece():
    piece = st.session_state.current_piece

    shape = piece["shape"]

    # 시계 방향 90도 회전
    rotated = [
        [
            shape[r][c]
            for r in range(len(shape) - 1, -1, -1)
        ]
        for c in range(len(shape[0]))
    ]

    # 회전 후 충돌하지 않는 경우에만 적용
    if not check_collision(
        st.session_state.board,
        piece,
        0,
        0,
        rotated,
    ):
        piece["shape"] = rotated
        return True

    return False


# =========================================================
# 화면 제목
# =========================================================
st.title("🕹️ Streamlit 테트리스 게임")

st.write(
    "버튼을 눌러 블록을 조작하고 "
    "최고 기록을 달성해 보세요!"
)


# =========================================================
# 게임 화면 + 컨트롤 화면
# =========================================================
# ★ 기존 st.col() 오류 수정
col_game, col_ctrl = st.columns([2, 1])


# =========================================================
# 게임판
# =========================================================
with col_game:

    # 현재 보드를 복사
    render_board = st.session_state.board.copy()

    # 현재 움직이는 블록
    piece = st.session_state.current_piece

    # 게임 오버가 아닐 때 현재 블록 표시
    if not st.session_state.game_over:

        for r_idx, row in enumerate(piece["shape"]):
            for c_idx, value in enumerate(row):

                if value == 0:
                    continue

                ny = piece["y"] + r_idx
                nx = piece["x"] + c_idx

                if (
                    0 <= ny < BOARD_HEIGHT
                    and 0 <= nx < BOARD_WIDTH
                ):
                    render_board[ny][nx] = (
                        piece["color_id"]
                    )

    # 보드를 문자열로 변환
    board_lines = []

    for row in render_board:
        line = "".join(
            EMOJIS[int(cell)]
            for cell in row
        )
        board_lines.append(line)

    board_str = "\n".join(board_lines)

    st.text(board_str)


# =========================================================
# 오른쪽 정보 영역
# =========================================================
with col_ctrl:

    st.markdown(
        f"### 📊 점수: {st.session_state.score}"
    )

    st.markdown(
        f"### 🔥 레벨: {st.session_state.level}"
    )

    st.markdown("---")

    # 다음 블록
    st.markdown("### ⏭️ 다음 블록")

    next_piece = st.session_state.next_piece

    next_lines = []

    for row in next_piece["shape"]:

        line = "".join(
            EMOJIS[
                next_piece["color_id"]
                if value
                else 0
            ]
            for value in row
        )

        next_lines.append(line)

    st.text("\n".join(next_lines))

    st.markdown("---")

    # 재시작 버튼
    if st.button(
        "🔄 게임 재시작",
        use_container_width=True,
    ):
        init_game()
        st.rerun()


# =========================================================
# 게임 조작 버튼
# =========================================================
if (
    not st.session_state.game_over
    and not st.session_state.paused
):

    st.markdown("### 🎮 조작")

    c1, c2, c3, c4 = st.columns(4)

    # -----------------------------------------------------
    # 왼쪽
    # -----------------------------------------------------
    with c1:

        if st.button(
            "⬅️ 좌",
            use_container_width=True,
        ):

            piece = st.session_state.current_piece

            if not check_collision(
                st.session_state.board,
                piece,
                -1,
                0,
            ):
                piece["x"] -= 1

            st.rerun()

    # -----------------------------------------------------
    # 회전
    # -----------------------------------------------------
    with c2:

        if st.button(
            "🔄 회전",
            use_container_width=True,
        ):

            rotate_piece()
            st.rerun()

    # -----------------------------------------------------
    # 오른쪽
    # -----------------------------------------------------
    with c3:

        if st.button(
            "➡️ 우",
            use_container_width=True,
        ):

            piece = st.session_state.current_piece

            if not check_collision(
                st.session_state.board,
                piece,
                1,
                0,
            ):
                piece["x"] += 1

            st.rerun()

    # -----------------------------------------------------
    # 아래로
    # -----------------------------------------------------
    with c4:

        if st.button(
            "⬇️ 하강",
            use_container_width=True,
        ):

            piece = st.session_state.current_piece

            # 한 칸 아래로 이동 가능
            if not check_collision(
                st.session_state.board,
                piece,
                0,
                1,
            ):

                piece["y"] += 1

            # 더 내려갈 수 없으면 고정
            else:
                lock_piece()

            st.rerun()


# =========================================================
# 게임 오버 메시지
# =========================================================
if st.session_state.game_over:

    st.error(
        "💥 게임 오버!\n\n"
        "'🔄 게임 재시작' 버튼을 눌러 "
        "다시 시작하세요."
    )
