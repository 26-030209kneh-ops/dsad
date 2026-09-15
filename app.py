import streamlit as st
import random
import time

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="Streamlit Tetris",
    page_icon="🎮",
    layout="centered"
)

# =========================================================
# 게임 설정
# =========================================================

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

EMPTY = 0

COLORS = {
    0: "#111827",
    1: "#00F0F0",  # I
    2: "#0000F0",  # J
    3: "#F0A000",  # L
    4: "#F0F000",  # O
    5: "#00F000",  # S
    6: "#A000F0",  # T
    7: "#F00000",  # Z
}

PIECES = {
    "I": [
        [
            [1, 1, 1, 1]
        ],
        [
            [1],
            [1],
            [1],
            [1]
        ],
    ],

    "O": [
        [
            [1, 1],
            [1, 1]
        ]
    ],

    "T": [
        [
            [0, 1, 0],
            [1, 1, 1]
        ],
        [
            [1, 0],
            [1, 1],
            [1, 0]
        ],
        [
            [1, 1, 1],
            [0, 1, 0]
        ],
        [
            [0, 1],
            [1, 1],
            [0, 1]
        ],
    ],

    "J": [
        [
            [1, 0, 0],
            [1, 1, 1]
        ],
        [
            [1, 1],
            [1, 0],
            [1, 0]
        ],
        [
            [1, 1, 1],
            [0, 0, 1]
        ],
        [
            [0, 1],
            [0, 1],
            [1, 1]
        ],
    ],

    "L": [
        [
            [0, 0, 1],
            [1, 1, 1]
        ],
        [
            [1, 0],
            [1, 0],
            [1, 1]
        ],
        [
            [1, 1, 1],
            [1, 0, 0]
        ],
        [
            [1, 1],
            [0, 1],
            [0, 1]
        ],
    ],

    "S": [
        [
            [0, 1, 1],
            [1, 1, 0]
        ],
        [
            [1, 0],
            [1, 1],
            [0, 1]
        ],
    ],

    "Z": [
        [
            [1, 1, 0],
            [0, 1, 1]
        ],
        [
            [0, 1],
            [1, 1],
            [1, 0]
        ],
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
# 세션 상태 초기화
# =========================================================

def init_game():

    st.session_state.board = [
        [EMPTY for _ in range(BOARD_WIDTH)]
        for _ in range(BOARD_HEIGHT)
    ]

    st.session_state.current_piece = None
    st.session_state.next_piece = random.choice(list(PIECES.keys()))
    st.session_state.hold_piece = None
    st.session_state.can_hold = True

    st.session_state.piece_x = 3
    st.session_state.piece_y = 0
    st.session_state.rotation = 0

    st.session_state.score = 0
    st.session_state.lines = 0
    st.session_state.level = 1
    st.session_state.combo = -1

    st.session_state.game_over = False
    st.session_state.paused = False

    st.session_state.last_drop = time.time()

    spawn_piece()


def spawn_piece():

    piece = st.session_state.next_piece

    st.session_state.current_piece = piece
    st.session_state.next_piece = random.choice(list(PIECES.keys()))

    st.session_state.rotation = 0

    shape = get_shape()

    st.session_state.piece_x = (BOARD_WIDTH - len(shape[0])) // 2
    st.session_state.piece_y = 0

    st.session_state.can_hold = True

    if collision(
        shape,
        st.session_state.piece_x,
        st.session_state.piece_y
    ):
        st.session_state.game_over = True


def get_shape():

    piece = st.session_state.current_piece
    rotations = PIECES[piece]

    rotation = st.session_state.rotation % len(rotations)

    return rotations[rotation]


# =========================================================
# 충돌 검사
# =========================================================

def collision(shape, x, y):

    for row_index, row in enumerate(shape):

        for col_index, cell in enumerate(row):

            if not cell:
                continue

            board_x = x + col_index
            board_y = y + row_index

            if board_x < 0 or board_x >= BOARD_WIDTH:
                return True

            if board_y >= BOARD_HEIGHT:
                return True

            if board_y >= 0 and st.session_state.board[board_y][board_x]:
                return True

    return False


# =========================================================
# 블록 이동
# =========================================================

def move(dx, dy):

    shape = get_shape()

    new_x = st.session_state.piece_x + dx
    new_y = st.session_state.piece_y + dy

    if not collision(shape, new_x, new_y):

        st.session_state.piece_x = new_x
        st.session_state.piece_y = new_y

        return True

    return False


# =========================================================
# 회전
# =========================================================

def rotate():

    old_rotation = st.session_state.rotation

    rotations = PIECES[st.session_state.current_piece]

    new_rotation = (old_rotation + 1) % len(rotations)

    st.session_state.rotation = new_rotation

    shape = get_shape()

    if collision(
        shape,
        st.session_state.piece_x,
        st.session_state.piece_y
    ):

        # 벽에 붙은 경우 간단한 wall kick
        for offset in [-1, 1, -2, 2]:

            new_x = st.session_state.piece_x + offset

            if not collision(
                shape,
                new_x,
                st.session_state.piece_y
            ):

                st.session_state.piece_x = new_x
                return

        st.session_state.rotation = old_rotation


# =========================================================
# 블록 고정
# =========================================================

def lock_piece():

    shape = get_shape()

    color = PIECE_COLOR[
        st.session_state.current_piece
    ]

    for row_index, row in enumerate(shape):

        for col_index, cell in enumerate(row):

            if cell:

                x = st.session_state.piece_x + col_index
                y = st.session_state.piece_y + row_index

                if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                    st.session_state.board[y][x] = color

    clear_lines()

    spawn_piece()


# =========================================================
# 줄 삭제
# =========================================================

def clear_lines():

    new_board = []

    cleared = 0

    for row in st.session_state.board:

        if all(row):
            cleared += 1
        else:
            new_board.append(row)

    while len(new_board) < BOARD_HEIGHT:

        new_board.insert(
            0,
            [EMPTY for _ in range(BOARD_WIDTH)]
        )

    st.session_state.board = new_board

    if cleared > 0:

        st.session_state.lines += cleared

        st.session_state.combo += 1

        # 테트리스 점수
        base_score = {
            1: 100,
            2: 300,
            3: 500,
            4: 800,
        }

        gained = base_score.get(cleared, 0)

        gained *= st.session_state.level

        # 콤보 보너스
        if st.session_state.combo > 0:
            gained += st.session_state.combo * 50

        st.session_state.score += gained

        # 레벨 증가
        st.session_state.level = (
            st.session_state.lines // 10
        ) + 1

    else:

        st.session_state.combo = -1


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
# Hold
# =========================================================

def hold_piece():

    if not st.session_state.can_hold:
        return

    current = st.session_state.current_piece

    if st.session_state.hold_piece is None:

        st.session_state.hold_piece = current

        spawn_piece()

    else:

        old_hold = st.session_state.hold_piece

        st.session_state.hold_piece = current
        st.session_state.current_piece = old_hold

        st.session_state.rotation = 0
        st.session_state.piece_x = 3
        st.session_state.piece_y = 0

    st.session_state.can_hold = False


# =========================================================
# Ghost Piece 위치
# =========================================================

def ghost_y():

    y = st.session_state.piece_y

    shape = get_shape()

    while not collision(
        shape,
        st.session_state.piece_x,
        y + 1
    ):

        y += 1

    return y


# =========================================================
# 보드 렌더링
# =========================================================

def make_display_board():

    board = [
        row[:] for row in st.session_state.board
    ]

    # Ghost
    if (
        not st.session_state.game_over
        and st.session_state.current_piece
    ):

        shape = get_shape()

        gy = ghost_y()

        for r, row in enumerate(shape):

            for c, cell in enumerate(row):

                if cell:

                    x = st.session_state.piece_x + c
                    y = gy + r

                    if (
                        0 <= x < BOARD_WIDTH
                        and 0 <= y < BOARD_HEIGHT
                        and board[y][x] == EMPTY
                    ):

                        board[y][x] = -1

    # 현재 블록
    if (
        not st.session_state.game_over
        and st.session_state.current_piece
    ):

        shape = get_shape()

        color = PIECE_COLOR[
            st.session_state.current_piece
        ]

        for r, row in enumerate(shape):

            for c, cell in enumerate(row):

                if cell:

                    x = st.session_state.piece_x + c
                    y = st.session_state.piece_y + r

                    if (
                        0 <= x < BOARD_WIDTH
                        and 0 <= y < BOARD_HEIGHT
                    ):

                        board[y][x] = color

    return board


def render_board():

    board = make_display_board()

    html = """
    <div class="game-board">
    """

    for row in board:

        for cell in row:

            if cell == -1:

                html += """
                <div class="cell ghost"></div>
                """

            else:

                color = COLORS[cell]

                if cell == 0:

                    html += f"""
                    <div class="cell empty"
                         style="background:{color};"></div>
                    """

                else:

                    html += f"""
                    <div class="cell filled"
                         style="background:{color};
                                box-shadow:
                                inset 0 0 8px rgba(255,255,255,.7);">
                    </div>
                    """

    html += "</div>"

    return html


# =========================================================
# 미리보기 블록
# =========================================================

def render_preview(piece):

    shape = PIECES[piece][0]

    html = """
    <div class="preview">
    """

    for row in shape:

        for cell in row:

            if cell:

                color = COLORS[
                    PIECE_COLOR[piece]
                ]

                html += f"""
                <div class="preview-cell"
                     style="background:{color};"></div>
                """

            else:

                html += """
                <div class="preview-cell empty-preview"></div>
                """

    html += "</div>"

    return html


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
        linear-gradient(
            135deg,
            #020617,
            #111827
        );
        color: white;
    }

    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 900;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #94a3b8;
        margin-bottom: 20px;
    }

    .game-board {
        width: 300px;
        height: 600px;
        margin: auto;

        display: grid;
        grid-template-columns:
            repeat(10, 1fr);

        grid-template-rows:
            repeat(20, 1fr);

        gap: 2px;

        background: #020617;

        border:
            3px solid #475569;

        padding: 4px;

        border-radius: 10px;

        box-shadow:
            0 0 30px
            rgba(0, 0, 0, .6);
    }

    .cell {
        border-radius: 3px;
    }

    .empty {
        background: #111827 !important;
        border:
            1px solid
            rgba(255,255,255,.025);
    }

    .filled {
        border-radius: 4px;
    }

    .ghost {
        background:
            rgba(255,255,255,.08);

        border:
            1px dashed
            rgba(255,255,255,.25);
    }

    .preview {
        display: grid;

        grid-template-columns:
            repeat(4, 28px);

        grid-auto-rows: 28px;

        gap: 3px;

        justify-content: center;

        margin: 10px 0;
    }

    .preview-cell {
        border-radius: 4px;
    }

    .empty-preview {
        background: transparent;
    }

    .stat {
        background: #1e293b;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 8px;
        text-align: center;
    }

    .stat-title {
        color: #94a3b8;
        font-size: 13px;
    }

    .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: white;
    }

    .game-over {
        text-align: center;

        background:
            rgba(127, 29, 29, .9);

        padding: 15px;

        border-radius: 10px;

        font-size: 24px;

        font-weight: bold;

        margin: 15px 0;
    }

    .control-box {
        background: #0f172a;

        padding: 15px;

        border-radius: 10px;

        margin-top: 15px;

        color: #cbd5e1;

        text-align: center;

        line-height: 1.8;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 게임 시작
# =========================================================

if "board" not in st.session_state:

    init_game()


# =========================================================
# 제목
# =========================================================

st.markdown(
    '<div class="title">🎮 TETRIS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Streamlit Edition</div>',
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
        ) * 0.07
    )

    now = time.time()

    if now - st.session_state.last_drop > speed:

        if not move(0, 1):

            lock_piece()

        st.session_state.last_drop = now


# =========================================================
# 키보드 입력
# =========================================================

st.markdown(
    """
    <script>

    document.addEventListener(
        'keydown',
        function(event) {

            let key = event.key.toLowerCase();

            if (
                [
                    'arrowleft',
                    'arrowright',
                    'arrowdown',
                    'arrowup',
                    ' ',
                    'c',
                    'p'
                ].includes(key)
            ) {
                event.preventDefault();
            }

            const buttons =
                window.parent.document
                .querySelectorAll('button');

            if (key === 'arrowleft') {
                buttons.forEach(b => {
                    if (b.innerText.includes('←')) {
                        b.click();
                    }
                });
            }

            if (key === 'arrowright') {
                buttons.forEach(b => {
                    if (b.innerText.includes('→')) {
                        b.click();
                    }
                });
            }

            if (key === 'arrowdown') {
                buttons.forEach(b => {
                    if (b.innerText.includes('↓')) {
                        b.click();
                    }
                });
            }

            if (key === 'arrowup') {
                buttons.forEach(b => {
                    if (b.innerText.includes('↻')) {
                        b.click();
                    }
                });
            }

            if (key === ' ') {
                buttons.forEach(b => {
                    if (b.innerText.includes('DROP')) {
                        b.click();
                    }
                });
            }

            if (key === 'c') {
                buttons.forEach(b => {
                    if (b.innerText.includes('HOLD')) {
                        b.click();
                    }
                });
            }

            if (key === 'p') {
                buttons.forEach(b => {
                    if (b.innerText.includes('PAUSE')) {
                        b.click();
                    }
                });
            }

        }
    );

    </script>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 레이아웃
# =========================================================

left, center, right = st.columns(
    [1, 2, 1]
)


# =========================================================
# 왼쪽 정보
# =========================================================

with left:

    st.markdown("### HOLD")

    if st.session_state.hold_piece:

        st.markdown(
            render_preview(
                st.session_state.hold_piece
            ),
            unsafe_allow_html=True
        )

    else:

        st.info("비어 있음")

    st.markdown("### 📊 SCORE")

    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-title">SCORE</div>
            <div class="stat-value">
                {st.session_state.score:,}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-title">LEVEL</div>
            <div class="stat-value">
                {st.session_state.level}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-title">LINES</div>
            <div class="stat-value">
                {st.session_state.lines}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 중앙 게임
# =========================================================

with center:

    if st.session_state.game_over:

        st.markdown(
            """
            <div class="game-over">
                💀 GAME OVER
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.session_state.paused:

        st.warning("⏸️ 게임 일시정지")

    st.markdown(
        render_board(),
        unsafe_allow_html=True
    )

    st.markdown("")

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button("←", use_container_width=True):

            move(-1, 0)

    with c2:

        if st.button("↓", use_container_width=True):

            if not move(0, 1):

                lock_piece()

    with c3:

        if st.button("→", use_container_width=True):

            move(1, 0)

    c4, c5, c6 = st.columns(3)

    with c4:

        if st.button("↻", use_container_width=True):

            rotate()

    with c5:

        if st.button("DROP", use_container_width=True):

            hard_drop()

    with c6:

        if st.button("HOLD", use_container_width=True):

            hold_piece()


# =========================================================
# 오른쪽 정보
# =========================================================

with right:

    st.markdown("### NEXT")

    st.markdown(
        render_preview(
            st.session_state.next_piece
        ),
        unsafe_allow_html=True
    )

    st.markdown("### 🎮 CONTROL")

    st.markdown(
        """
        <div class="control-box">
        ← → : 이동<br>
        ↓ : 빠르게 내리기<br>
        ↑ : 회전<br>
        SPACE : 즉시 내리기<br>
        C : HOLD<br>
        P : 일시정지
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    if st.button(
        "⏸️ PAUSE",
        use_container_width=True
    ):

        st.session_state.paused = (
            not st.session_state.paused
        )

    if st.button(
        "🔄 NEW GAME",
        use_container_width=True
    ):

        init_game()


# =========================================================
# 콤보 표시
# =========================================================

if st.session_state.combo > 0:

    st.success(
        f"🔥 COMBO x{st.session_state.combo}"
    )


# =========================================================
# 자동 새로고침
# =========================================================

if (
    not st.session_state.game_over
    and not st.session_state.paused
):

    time.sleep(0.05)

    st.rerun()
