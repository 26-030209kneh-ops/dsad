import streamlit as st
import random
import time

# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="Tetris",
    page_icon="🎮",
    layout="centered"
)

# =========================================================
# 게임 설정
# =========================================================

WIDTH = 10
HEIGHT = 20

COLORS = {
    0: "#111827",
    1: "#00E5FF",  # I
    2: "#2979FF",  # J
    3: "#FF9800",  # L
    4: "#FFD600",  # O
    5: "#00E676",  # S
    6: "#D500F9",  # T
    7: "#FF1744",  # Z
}

PIECES = {
    "I": [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]],
    ],

    "O": [
        [[1, 1],
         [1, 1]],
    ],

    "T": [
        [[0, 1, 0],
         [1, 1, 1]],

        [[1, 0],
         [1, 1],
         [1, 0]],

        [[1, 1, 1],
         [0, 1, 0]],

        [[0, 1],
         [1, 1],
         [0, 1]],
    ],

    "J": [
        [[1, 0, 0],
         [1, 1, 1]],

        [[1, 1],
         [1, 0],
         [1, 0]],

        [[1, 1, 1],
         [0, 0, 1]],

        [[0, 1],
         [0, 1],
         [1, 1]],
    ],

    "L": [
        [[0, 0, 1],
         [1, 1, 1]],

        [[1, 0],
         [1, 0],
         [1, 1]],

        [[1, 1, 1],
         [1, 0, 0]],

        [[1, 1],
         [0, 1],
         [0, 1]],
    ],

    "S": [
        [[0, 1, 1],
         [1, 1, 0]],

        [[1, 0],
         [1, 1],
         [0, 1]],
    ],

    "Z": [
        [[1, 1, 0],
         [0, 1, 1]],

        [[0, 1],
         [1, 1],
         [1, 0]],
    ],
}

PIECE_COLOR = {
    "I": 1,
    "J": 2,
    "L": 3,
    "O": 4,
    "S": 5,
    "T": 6,
    "Z": 7,
}


# =========================================================
# 게임 초기화
# =========================================================

def new_game():

    st.session_state.board = [
        [0 for _ in range(WIDTH)]
        for _ in range(HEIGHT)
    ]

    pieces = list(PIECES.keys())

    st.session_state.current = random.choice(pieces)
    st.session_state.next = random.choice(pieces)
    st.session_state.hold = None

    st.session_state.rotation = 0

    st.session_state.x = 3
    st.session_state.y = 0

    st.session_state.score = 0
    st.session_state.lines = 0
    st.session_state.level = 1
    st.session_state.combo = 0

    st.session_state.can_hold = True
    st.session_state.game_over = False
    st.session_state.paused = False

    st.session_state.last_drop = time.time()


if "board" not in st.session_state:
    new_game()


# =========================================================
# 현재 블록 모양
# =========================================================

def get_shape():

    rotations = PIECES[st.session_state.current]

    index = (
        st.session_state.rotation
        % len(rotations)
    )

    return rotations[index]


# =========================================================
# 충돌 검사
# =========================================================

def collision(s, x, y):

    for row_index, row in enumerate(s):

        for col_index, value in enumerate(row):

            if value == 0:
                continue

            board_x = x + col_index
            board_y = y + row_index

            if board_x < 0:
                return True

            if board_x >= WIDTH:
                return True

            if board_y >= HEIGHT:
                return True

            if (
                board_y >= 0
                and st.session_state.board[board_y][board_x] != 0
            ):
                return True

    return False


# =========================================================
# 블록 이동
# =========================================================

def move(dx, dy):

    new_x = st.session_state.x + dx
    new_y = st.session_state.y + dy

    if not collision(
        get_shape(),
        new_x,
        new_y
    ):

        st.session_state.x = new_x
        st.session_state.y = new_y

        return True

    return False


# =========================================================
# 회전
# =========================================================

def rotate():

    old_rotation = st.session_state.rotation

    st.session_state.rotation += 1

    s = get_shape()

    if not collision(
        s,
        st.session_state.x,
        st.session_state.y
    ):
        return

    # 벽에 붙어 있을 때 위치 조정
    for offset in [-1, 1, -2, 2]:

        if not collision(
            s,
            st.session_state.x + offset,
            st.session_state.y
        ):

            st.session_state.x += offset
            return

    st.session_state.rotation = old_rotation


# =========================================================
# 줄 삭제
# =========================================================

def clear_lines():

    new_board = []
    cleared = 0

    for row in st.session_state.board:

        if all(cell != 0 for cell in row):
            cleared += 1
        else:
            new_board.append(row)

    while len(new_board) < HEIGHT:

        new_board.insert(
            0,
            [0 for _ in range(WIDTH)]
        )

    st.session_state.board = new_board

    if cleared > 0:

        score_table = {
            1: 100,
            2: 300,
            3: 500,
            4: 800
        }

        gained = score_table.get(cleared, 0)

        gained *= st.session_state.level

        st.session_state.combo += 1

        if st.session_state.combo > 1:

            gained += (
                st.session_state.combo * 50
            )

        st.session_state.score += gained
        st.session_state.lines += cleared

        st.session_state.level = (
            st.session_state.lines // 10
        ) + 1

    else:

        st.session_state.combo = 0


# =========================================================
# 블록 고정
# =========================================================

def lock_piece():

    s = get_shape()

    color = PIECE_COLOR[
        st.session_state.current
    ]

    for row_index, row in enumerate(s):

        for col_index, value in enumerate(row):

            if value == 0:
                continue

            board_x = (
                st.session_state.x
                + col_index
            )

            board_y = (
                st.session_state.y
                + row_index
            )

            if (
                0 <= board_x < WIDTH
                and 0 <= board_y < HEIGHT
            ):

                st.session_state.board[
                    board_y
                ][
                    board_x
                ] = color

    clear_lines()

    st.session_state.current = (
        st.session_state.next
    )

    st.session_state.next = random.choice(
        list(PIECES.keys())
    )

    st.session_state.rotation = 0
    st.session_state.x = 3
    st.session_state.y = 0

    st.session_state.can_hold = True

    if collision(
        get_shape(),
        st.session_state.x,
        st.session_state.y
    ):

        st.session_state.game_over = True


# =========================================================
# 하드 드롭
# =========================================================

def hard_drop():

    distance = 0

    while move(0, 1):
        distance += 1

    st.session_state.score += (
        distance * 2
    )

    lock_piece()


# =========================================================
# HOLD
# =========================================================

def hold_piece():

    if not st.session_state.can_hold:
        return

    current = st.session_state.current

    if st.session_state.hold is None:

        st.session_state.hold = current

        st.session_state.current = (
            st.session_state.next
        )

        st.session_state.next = random.choice(
            list(PIECES.keys())
        )

    else:

        old_hold = st.session_state.hold

        st.session_state.hold = current
        st.session_state.current = old_hold

    st.session_state.rotation = 0
    st.session_state.x = 3
    st.session_state.y = 0

    st.session_state.can_hold = False


# =========================================================
# Ghost 블록 위치
# =========================================================

def get_ghost_y():

    ghost_y = st.session_state.y

    while not collision(
        get_shape(),
        st.session_state.x,
        ghost_y + 1
    ):

        ghost_y += 1

    return ghost_y


# =========================================================
# 보드 HTML 생성
# =========================================================

def create_board_html():

    board = [
        row[:] for row in st.session_state.board
    ]

    # -------------------------
    # Ghost
    # -------------------------

    if not st.session_state.game_over:

        ghost_y = get_ghost_y()

        s = get_shape()

        for r, row in enumerate(s):

            for c, value in enumerate(row):

                if value:

                    x = (
                        st.session_state.x
                        + c
                    )

                    y = ghost_y + r

                    if (
                        0 <= x < WIDTH
                        and 0 <= y < HEIGHT
                        and board[y][x] == 0
                    ):

                        board[y][x] = -1


    # -------------------------
    # 현재 블록
    # -------------------------

    if not st.session_state.game_over:

        s = get_shape()

        color = PIECE_COLOR[
            st.session_state.current
        ]

        for r, row in enumerate(s):

            for c, value in enumerate(row):

                if value:

                    x = (
                        st.session_state.x
                        + c
                    )

                    y = (
                        st.session_state.y
                        + r
                    )

                    if (
                        0 <= x < WIDTH
                        and 0 <= y < HEIGHT
                    ):

                        board[y][x] = color


    # -------------------------
    # 셀 생성
    # -------------------------

    cells = []

    for row in board:

        for cell in row:

            if cell == 0:

                cells.append(
                    '<div class="cell empty"></div>'
                )

            elif cell == -1:

                cells.append(
                    '<div class="cell ghost"></div>'
                )

            else:

                color = COLORS[cell]

                cells.append(
                    f'''
                    <div
                        class="cell block"
                        style="
                            background:{color};
                        "
                    ></div>
                    '''
                )


    # ★ 중요
    # HTML을 한 줄 구조로 만들어
    # Streamlit이 코드처럼 해석할 가능성을 제거

    return (
        '<div class="tetris-board">'
        + ''.join(cells)
        + '</div>'
    )


# =========================================================
# 미리보기 HTML
# =========================================================

def create_preview_html(piece):

    if piece is None:

        return (
            '<div class="preview-empty">'
            'EMPTY'
            '</div>'
        )

    s = PIECES[piece][0]

    cells = []

    for r in range(4):

        for c in range(4):

            value = 0

            if (
                r < len(s)
                and c < len(s[0])
            ):

                value = s[r][c]

            if value:

                color = COLORS[
                    PIECE_COLOR[piece]
                ]

                cells.append(
                    f'''
                    <div
                        class="preview-cell"
                        style="
                            background:{color};
                        "
                    ></div>
                    '''
                )

            else:

                cells.append(
                    '<div class="preview-cell blank"></div>'
                )

    return (
        '<div class="preview-grid">'
        + ''.join(cells)
        + '</div>'
    )


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
<style>

html, body {
    background: #020617;
}

.stApp {
    background:
        radial-gradient(
            circle at top,
            #172554 0%,
            #020617 55%,
            #020617 100%
        );
}

/* 제목 */

.game-title {
    text-align: center;
    color: white;
    font-size: 46px;
    font-weight: 900;
    letter-spacing: 4px;
    margin-top: 10px;
}

.game-subtitle {
    text-align: center;
    color: #60a5fa;
    margin-bottom: 25px;
}

/* 보드 */

.tetris-board {
    width: 300px;
    height: 600px;

    display: grid;

    grid-template-columns:
        repeat(10, 1fr);

    grid-template-rows:
        repeat(20, 1fr);

    gap: 2px;

    padding: 5px;

    margin: auto;

    background: #020617;

    border: 3px solid #64748b;

    border-radius: 12px;

    box-sizing: border-box;

    box-shadow:
        0 0 35px
        rgba(59,130,246,.3);
}

.cell {
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    border-radius: 3px;
}

.cell.empty {
    background: #0f172a;
    border:
        1px solid
        rgba(255,255,255,.025);
}

.cell.block {
    border-radius: 4px;

    box-shadow:
        inset 0 2px 3px
        rgba(255,255,255,.5),

        inset 0 -2px 3px
        rgba(0,0,0,.35);
}

.cell.ghost {
    background:
        rgba(148,163,184,.10);

    border:
        1px dashed
        rgba(148,163,184,.4);
}

/* 패널 */

.panel-title {
    color: white;
    font-size: 21px;
    font-weight: 800;
    margin-bottom: 10px;
}

/* 점수 */

.stat-box {
    background:
        rgba(30,41,59,.9);

    border:
        1px solid #334155;

    border-radius: 10px;

    padding: 10px;

    text-align: center;

    margin-bottom: 8px;
}

.stat-name {
    color: #94a3b8;
    font-size: 12px;
}

.stat-value {
    color: white;
    font-size: 25px;
    font-weight: 900;
}

/* 미리보기 */

.preview-grid {
    width: 112px;
    height: 112px;

    display: grid;

    grid-template-columns:
        repeat(4, 25px);

    grid-template-rows:
        repeat(4, 25px);

    gap: 3px;

    padding: 5px;

    box-sizing: border-box;

    background: #0f172a;

    border-radius: 10px;

    margin-bottom: 20px;
}

.preview-cell {
    border-radius: 4px;

    box-shadow:
        inset 0 2px 3px
        rgba(255,255,255,.4),

        inset 0 -2px 3px
        rgba(0,0,0,.3);
}

.preview-cell.blank {
    background: transparent;
    box-shadow: none;
}

.preview-empty {
    width: 112px;
    height: 112px;

    display: flex;
    align-items: center;
    justify-content: center;

    color: #64748b;

    background: #0f172a;

    border-radius: 10px;

    margin-bottom: 20px;
}

/* 조작 설명 */

.control-box {
    background:
        rgba(15,23,42,.95);

    color: #cbd5e1;

    border:
        1px solid #334155;

    border-radius: 10px;

    padding: 14px;

    line-height: 1.9;

    font-size: 14px;
}

/* 게임오버 */

.game-over {
    background: #991b1b;

    color: white;

    text-align: center;

    padding: 12px;

    border-radius: 10px;

    font-size: 22px;

    font-weight: 900;

    margin-bottom: 12px;
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# 제목
# =========================================================

st.markdown(
    '<div class="game-title">🎮 TETRIS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="game-subtitle">STREAMLIT EDITION</div>',
    unsafe_allow_html=True
)


# =========================================================
# 자동 낙하
# =========================================================

if (
    not st.session_state.game_over
    and not st.session_state.paused
):

    speed = max(
        0.08,
        0.8 - (
            st.session_state.level - 1
        ) * 0.06
    )

    current_time = time.time()

    if (
        current_time
        - st.session_state.last_drop
        >= speed
    ):

        if not move(0, 1):

            lock_piece()

        st.session_state.last_drop = current_time


# =========================================================
# 레이아웃
# =========================================================

left, center, right = st.columns(
    [1, 2, 1],
    gap="medium"
)


# =========================================================
# 왼쪽
# =========================================================

with left:

    st.markdown(
        '<div class="panel-title">HOLD</div>',
        unsafe_allow_html=True
    )

    # ★ st.html 사용
    st.html(
        create_preview_html(
            st.session_state.hold
        )
    )

    st.markdown(
        '<div class="panel-title">📊 SCORE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="stat-box">
            <div class="stat-name">
                SCORE
            </div>

            <div class="stat-value">
                {st.session_state.score:,}
            </div>
        </div>

        <div class="stat-box">
            <div class="stat-name">
                LEVEL
            </div>

            <div class="stat-value">
                {st.session_state.level}
            </div>
        </div>

        <div class="stat-box">
            <div class="stat-name">
                LINES
            </div>

            <div class="stat-value">
                {st.session_state.lines}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 중앙
# =========================================================

with center:

    if st.session_state.game_over:

        st.markdown(
            '<div class="game-over">'
            '💀 GAME OVER'
            '</div>',
            unsafe_allow_html=True
        )

    elif st.session_state.paused:

        st.warning("⏸️ 게임 일시정지")

    # ★★★ 핵심 ★★★
    # 보드를 st.html()로 직접 렌더링

    st.html(
        create_board_html()
    )

    st.write("")

    # 이동 버튼

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "⬅️",
            use_container_width=True
        ):

            move(-1, 0)
            st.rerun()

    with col2:

        if st.button(
            "⬇️",
            use_container_width=True
        ):

            if not move(0, 1):
                lock_piece()

            st.rerun()

    with col3:

        if st.button(
            "➡️",
            use_container_width=True
        ):

            move(1, 0)
            st.rerun()


    # 액션 버튼

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "🔄 ROTATE",
            use_container_width=True
        ):

            rotate()
            st.rerun()

    with col2:

        if st.button(
            "⬇️ DROP",
            use_container_width=True
        ):

            hard_drop()
            st.rerun()

    with col3:

        if st.button(
            "📦 HOLD",
            use_container_width=True
        ):

            hold_piece()
            st.rerun()


# =========================================================
# 오른쪽
# =========================================================

with right:

    st.markdown(
        '<div class="panel-title">NEXT</div>',
        unsafe_allow_html=True
    )

    # ★ st.html 사용

    st.html(
        create_preview_html(
            st.session_state.next
        )
    )

    st.markdown(
        '<div class="panel-title">🎮 CONTROL</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="control-box">
            ⬅️ ➡️ &nbsp; 이동<br>
            ⬇️ &nbsp; 빠르게 내리기<br>
            🔄 &nbsp; 회전<br>
            SPACE &nbsp; 즉시 내리기<br>
            C &nbsp; HOLD<br>
            P &nbsp; 일시정지
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    if st.button(
        "⏸️ PAUSE / RESUME",
        use_container_width=True
    ):

        st.session_state.paused = (
            not st.session_state.paused
        )

        st.rerun()

    if st.button(
        "🔄 NEW GAME",
        use_container_width=True
    ):

        new_game()
        st.rerun()


# =========================================================
# 콤보
# =========================================================

if st.session_state.combo > 1:

    st.success(
        f"🔥 COMBO x{st.session_state.combo}"
    )


# =========================================================
# 키보드 안내
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748b;
        margin-top:20px;
        font-size:13px;
    ">
        키보드 조작은 아래 버튼을 이용하거나
        방향키를 사용할 수 있습니다.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 자동 새로고침
# =========================================================

if (
    not st.session_state.game_over
    and not st.session_state.paused
):

    time.sleep(0.08)
    st.rerun()
