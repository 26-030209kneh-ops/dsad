import streamlit as st
import random
import time
import streamlit.components.v1 as components

# =========================================================
# 설정
# =========================================================

st.set_page_config(
    page_title="Tetris",
    page_icon="🎮",
    layout="centered"
)

WIDTH = 10
HEIGHT = 20

COLORS = {
    0: "#111827",
    1: "#00E5FF",   # I
    2: "#2979FF",   # J
    3: "#FF9800",   # L
    4: "#FFD600",   # O
    5: "#00E676",   # S
    6: "#D500F9",   # T
    7: "#FF1744",   # Z
}

PIECES = {
    "I": [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]]
    ],

    "O": [
        [[1, 1], [1, 1]]
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
         [0, 1]]
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
         [1, 1]]
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
         [0, 1]]
    ],

    "S": [
        [[0, 1, 1],
         [1, 1, 0]],

        [[1, 0],
         [1, 1],
         [0, 1]]
    ],

    "Z": [
        [[1, 1, 0],
         [0, 1, 1]],

        [[0, 1],
         [1, 1],
         [1, 0]]
    ]
}

PIECE_COLOR = {
    "I": 1,
    "J": 2,
    "L": 3,
    "O": 4,
    "S": 5,
    "T": 6,
    "Z": 7
}


# =========================================================
# 게임 초기화
# =========================================================

def new_game():

    st.session_state.board = [
        [0 for _ in range(WIDTH)]
        for _ in range(HEIGHT)
    ]

    st.session_state.current = random.choice(list(PIECES.keys()))
    st.session_state.next = random.choice(list(PIECES.keys()))
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

def shape():

    rotations = PIECES[st.session_state.current]

    return rotations[
        st.session_state.rotation % len(rotations)
    ]


# =========================================================
# 충돌 검사
# =========================================================

def collision(s, x, y):

    for r, row in enumerate(s):

        for c, value in enumerate(row):

            if not value:
                continue

            bx = x + c
            by = y + r

            if bx < 0 or bx >= WIDTH:
                return True

            if by >= HEIGHT:
                return True

            if by >= 0 and st.session_state.board[by][bx]:
                return True

    return False


# =========================================================
# 이동
# =========================================================

def move(dx, dy):

    nx = st.session_state.x + dx
    ny = st.session_state.y + dy

    if not collision(shape(), nx, ny):

        st.session_state.x = nx
        st.session_state.y = ny

        return True

    return False


# =========================================================
# 회전
# =========================================================

def rotate():

    old_rotation = st.session_state.rotation

    st.session_state.rotation += 1

    if collision(
        shape(),
        st.session_state.x,
        st.session_state.y
    ):

        # 간단한 벽 차기
        for offset in [-1, 1, -2, 2]:

            if not collision(
                shape(),
                st.session_state.x + offset,
                st.session_state.y
            ):

                st.session_state.x += offset
                return

        st.session_state.rotation = old_rotation


# =========================================================
# 블록 고정
# =========================================================

def lock_piece():

    s = shape()
    color = PIECE_COLOR[st.session_state.current]

    for r, row in enumerate(s):

        for c, value in enumerate(row):

            if value:

                bx = st.session_state.x + c
                by = st.session_state.y + r

                if 0 <= by < HEIGHT and 0 <= bx < WIDTH:

                    st.session_state.board[by][bx] = color

    clear_lines()

    st.session_state.current = st.session_state.next
    st.session_state.next = random.choice(
        list(PIECES.keys())
    )

    st.session_state.rotation = 0
    st.session_state.x = 3
    st.session_state.y = 0
    st.session_state.can_hold = True

    if collision(
        shape(),
        st.session_state.x,
        st.session_state.y
    ):

        st.session_state.game_over = True


# =========================================================
# 줄 제거
# =========================================================

def clear_lines():

    remaining = []

    cleared = 0

    for row in st.session_state.board:

        if all(row):
            cleared += 1
        else:
            remaining.append(row)

    while len(remaining) < HEIGHT:

        remaining.insert(
            0,
            [0 for _ in range(WIDTH)]
        )

    st.session_state.board = remaining

    if cleared:

        st.session_state.lines += cleared

        scores = {
            1: 100,
            2: 300,
            3: 500,
            4: 800
        }

        gained = scores.get(cleared, 0)

        gained *= st.session_state.level

        st.session_state.combo += 1

        if st.session_state.combo > 1:
            gained += (
                st.session_state.combo * 50
            )

        st.session_state.score += gained

        st.session_state.level = (
            st.session_state.lines // 10
        ) + 1

    else:

        st.session_state.combo = 0


# =========================================================
# 하드 드롭
# =========================================================

def hard_drop():

    distance = 0

    while move(0, 1):
        distance += 1

    st.session_state.score += distance * 2

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

        temp = st.session_state.hold

        st.session_state.hold = current
        st.session_state.current = temp

    st.session_state.rotation = 0
    st.session_state.x = 3
    st.session_state.y = 0

    st.session_state.can_hold = False


# =========================================================
# Ghost 블록 위치
# =========================================================

def ghost_position():

    gy = st.session_state.y

    while not collision(
        shape(),
        st.session_state.x,
        gy + 1
    ):

        gy += 1

    return gy


# =========================================================
# 보드 HTML
# =========================================================

def board_html():

    board = [
        row[:] for row in st.session_state.board
    ]

    # Ghost
    if not st.session_state.game_over:

        gy = ghost_position()

        ghost_color = PIECE_COLOR[
            st.session_state.current
        ]

        s = shape()

        for r, row in enumerate(s):

            for c, value in enumerate(row):

                if value:

                    bx = st.session_state.x + c
                    by = gy + r

                    if (
                        0 <= bx < WIDTH
                        and 0 <= by < HEIGHT
                        and board[by][bx] == 0
                    ):

                        board[by][bx] = -ghost_color


    # 현재 블록
    if not st.session_state.game_over:

        s = shape()

        color = PIECE_COLOR[
            st.session_state.current
        ]

        for r, row in enumerate(s):

            for c, value in enumerate(row):

                if value:

                    bx = st.session_state.x + c
                    by = st.session_state.y + r

                    if (
                        0 <= bx < WIDTH
                        and 0 <= by < HEIGHT
                    ):

                        board[by][bx] = color


    cells = ""

    for row in board:

        for cell in row:

            if cell == 0:

                cells += """
                <div class="cell empty"></div>
                """

            elif cell < 0:

                cells += """
                <div class="cell ghost"></div>
                """

            else:

                color = COLORS[cell]

                cells += f"""
                <div
                    class="cell block"
                    style="
                        background:{color};
                        box-shadow:
                        inset 0 2px 3px
                        rgba(255,255,255,.5),
                        inset 0 -2px 3px
                        rgba(0,0,0,.35);
                    ">
                </div>
                """

    return f"""
    <div class="board">
        {cells}
    </div>
    """


# =========================================================
# 미리보기 HTML
# =========================================================

def preview_html(piece):

    if piece is None:

        return """
        <div class="preview-empty">
            EMPTY
        </div>
        """

    s = PIECES[piece][0]

    # 4x4 공간
    grid = []

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

                grid.append(
                    f"""
                    <div
                        class="preview-cell"
                        style="background:{color};">
                    </div>
                    """
                )

            else:

                grid.append(
                    """
                    <div class="preview-cell blank"></div>
                    """
                )

    return f"""
    <div class="preview-grid">
        {''.join(grid)}
    </div>
    """


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
        radial-gradient(
            circle at top,
            #172554 0%,
            #020617 45%,
            #020617 100%
        );
    }

    .main-title {
        text-align: center;
        font-size: 46px;
        font-weight: 900;
        color: white;
        margin-top: 10px;
        margin-bottom: 0;
        letter-spacing: 3px;
    }

    .sub-title {
        text-align: center;
        color: #93c5fd;
        margin-bottom: 25px;
    }

    .board {
        width: 300px;
        height: 600px;

        display: grid;
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);

        gap: 2px;

        padding: 5px;

        margin: auto;

        background: #020617;

        border: 3px solid #64748b;

        border-radius: 12px;

        box-shadow:
            0 0 35px
            rgba(59,130,246,.25);
    }

    .cell {
        border-radius: 3px;
    }

    .empty {
        background: #0f172a;
        border:
            1px solid
            rgba(255,255,255,.025);
    }

    .block {
        border-radius: 4px;
    }

    .ghost {
        background: rgba(148,163,184,.12);
        border:
            1px dashed
            rgba(148,163,184,.45);
    }

    .panel-title {
        color: white;
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .stat {
        background: rgba(30,41,59,.9);
        border: 1px solid #334155;
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
        font-weight: 800;
    }

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

        margin-bottom: 20px;

        background: #0f172a;

        border-radius: 10px;
    }

    .preview-cell {
        border-radius: 4px;
    }

    .blank {
        background: transparent;
    }

    .preview-empty {
        color: #64748b;
        background: #0f172a;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }

    .control {
        color: #cbd5e1;
        background: rgba(15,23,42,.95);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px;
        line-height: 1.9;
        font-size: 14px;
    }

    .game-over {
        background: #991b1b;
        color: white;
        text-align: center;
        padding: 12px;
        border-radius: 10px;
        font-size: 22px;
        font-weight: bold;
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
    '<div class="main-title">🎮 TETRIS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">STREAMLIT EDITION</div>',
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

    now = time.time()

    if now - st.session_state.last_drop >= speed:

        if not move(0, 1):

            lock_piece()

        st.session_state.last_drop = now


# =========================================================
# 레이아웃
# =========================================================

left, center, right = st.columns(
    [1, 2, 1]
)


# =========================================================
# 왼쪽
# =========================================================

with left:

    st.markdown(
        '<div class="panel-title">HOLD</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        preview_html(st.session_state.hold),
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="panel-title">📊 SCORE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-name">SCORE</div>
            <div class="stat-value">
                {st.session_state.score:,}
            </div>
        </div>

        <div class="stat">
            <div class="stat-name">LEVEL</div>
            <div class="stat-value">
                {st.session_state.level}
            </div>
        </div>

        <div class="stat">
            <div class="stat-name">LINES</div>
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
            '<div class="game-over">💀 GAME OVER</div>',
            unsafe_allow_html=True
        )

    elif st.session_state.paused:

        st.warning("⏸️ PAUSED")

    # ★ 중요: st.markdown으로 HTML 렌더링
    st.markdown(
        board_html(),
        unsafe_allow_html=True
    )

    st.write("")

    a, b, c = st.columns(3)

    with a:

        if st.button(
            "⬅️",
            use_container_width=True
        ):

            move(-1, 0)
            st.rerun()

    with b:

        if st.button(
            "⬇️",
            use_container_width=True
        ):

            if not move(0, 1):
                lock_piece()

            st.rerun()

    with c:

        if st.button(
            "➡️",
            use_container_width=True
        ):

            move(1, 0)
            st.rerun()

    a, b, c = st.columns(3)

    with a:

        if st.button(
            "🔄 ROTATE",
            use_container_width=True
        ):

            rotate()
            st.rerun()

    with b:

        if st.button(
            "⬇️ DROP",
            use_container_width=True
        ):

            hard_drop()
            st.rerun()

    with c:

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

    st.markdown(
        preview_html(st.session_state.next),
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="panel-title">🎮 CONTROL</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="control">
        ⬅️ ➡️ 이동<br>
        ⬇️ 빠르게 내리기<br>
        🔄 회전<br>
        SPACE → 즉시 내리기<br>
        C → HOLD<br>
        P → 일시정지
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
# 키보드 입력
# =========================================================

components.html(
    """
    <script>

    const doc = window.parent.document;

    if (!window.tetrisKeyboardInstalled) {

        window.tetrisKeyboardInstalled = true;

        doc.addEventListener("keydown", function(e) {

            const key = e.key.toLowerCase();

            if (
                key === "arrowleft" ||
                key === "arrowright" ||
                key === "arrowdown" ||
                key === "arrowup" ||
                key === " "
            ) {
                e.preventDefault();
            }

            const buttons =
                Array.from(
                    doc.querySelectorAll("button")
                );

            function clickButton(text) {

                const button = buttons.find(
                    b => b.innerText.includes(text)
                );

                if (button) {
                    button.click();
                }
            }

            if (key === "arrowleft") {
                clickButton("⬅️");
            }

            if (key === "arrowright") {
                clickButton("➡️");
            }

            if (key === "arrowdown") {
                clickButton("⬇️");
            }

            if (key === "arrowup") {
                clickButton("ROTATE");
            }

            if (key === " ") {
                clickButton("DROP");
            }

            if (key === "c") {
                clickButton("HOLD");
            }

            if (key === "p") {
                clickButton("PAUSE");
            }

        });

    }

    </script>
    """,
    height=0
)


# =========================================================
# 게임 자동 실행
# =========================================================

if (
    not st.session_state.game_over
    and not st.session_state.paused
):

    time.sleep(0.05)
    st.rerun()
