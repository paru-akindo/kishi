import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import copy

# --- 定数定義 ---
CELL_SIZE = 40
ROWS = 11
COLS = 9

# セルの状態（例）
EMPTY = 0
CAT = 1
CHICK = 2
COW = 3

# Matplotlib 用の色マップ
COLOR_MAP = {
    EMPTY: "white",
    CAT: "orange",
    CHICK: "yellow",
    COW: "brown"
}

# --- 盤面クラス ---
class Board:
    def __init__(self, rows=ROWS, cols=COLS):
        self.rows = rows
        self.cols = cols
        self.grid = [[EMPTY for _ in range(cols)] for _ in range(rows)]
    
    def copy(self):
        new_board = Board(self.rows, self.cols)
        new_board.grid = copy.deepcopy(self.grid)
        return new_board

    def slide_row(self, row_index, direction):
        """指定した行を左右にスライドする."""
        if direction == "left":
            self.grid[row_index] = self.grid[row_index][1:] + [self.grid[row_index][0]]
        elif direction == "right":
            self.grid[row_index] = [self.grid[row_index][-1]] + self.grid[row_index][:-1]

    def apply_gravity(self):
        """各列ごとに、下に空きがあれば上のブロックを落下させる."""
        for col in range(self.cols):
            for row in range(self.rows - 2, -1, -1):
                if self.grid[row][col] != EMPTY:
                    current_row = row
                    while current_row + 1 < self.rows and self.grid[current_row + 1][col] == EMPTY:
                        self.grid[current_row + 1][col] = self.grid[current_row][col]
                        self.grid[current_row][col] = EMPTY
                        current_row += 1

    def add_new_row(self, new_row):
        """上端の行を削除して、下端に新行を追加する."""
        self.grid.pop(0)
        self.grid.append(new_row.copy())
        self.apply_gravity()

    def clear_filled_rows(self):
        """各行が全て埋まっていればその行をクリアする."""
        rows_cleared = 0
        for i in range(self.rows):
            if all(cell != EMPTY for cell in self.grid[i]):
                self.grid[i] = [EMPTY for _ in range(self.cols)]
                rows_cleared += 1
        if rows_cleared > 0:
            self.apply_gravity()
        return rows_cleared

    def get_empty_count(self):
        """盤面全体の EMPTY セル数を数える（評価用）"""
        count = 0
        for row in self.grid:
            count += sum(1 for cell in row if cell == EMPTY)
        return count

    def game_over(self):
        """最上行にブロックがあるならゲームオーバーとする."""
        return any(cell != EMPTY for cell in self.grid[0])

# --- 補助関数 ---
def generate_new_row():
    """新しい行をランダムに生成する。"""
    return [random.choice([CAT, CHICK, COW]) for _ in range(COLS)]

def evaluate_board(board):
    """
    単純な評価関数：盤面内の EMPTY セル数を返す。
    空きセルが多い状態を高得点として評価する。
    """
    return board.get_empty_count()

def simulate_turn(board, new_row):
    """新行追加、重力適用、行クリアを１ターンで実行する."""
    board.add_new_row(new_row)
    cleared = board.clear_filled_rows()
    return cleared

def get_optimal_move(board, new_row):
    """
    各行の左右スライドを試し、新行追加後の盤面状態を評価して、
    最も評価値（空セル数）が高い動きを返す。
    """
    best_score = -float('inf')
    best_move = None
    for row in range(board.rows):
        for direction in ['left', 'right']:
            temp_board = board.copy()
            temp_board.slide_row(row, direction)
            temp_board.add_new_row(new_row)
            temp_board.clear_filled_rows()
            score = evaluate_board(temp_board)
            if score > best_score:
                best_score = score
                best_move = (row, direction)
    return best_move, best_score

def draw_board(board):
    """Matplotlib を使って盤面を描画する."""
    fig, ax = plt.subplots(figsize=(COLS, ROWS))
    ax.set_xlim(0, COLS * CELL_SIZE)
    ax.set_ylim(0, ROWS * CELL_SIZE)
    ax.invert_yaxis()  # 左上が (0,0) となるように
    for i in range(ROWS):
        for j in range(COLS):
            x = j * CELL_SIZE
            y = i * CELL_SIZE
            cell = board.grid[i][j]
            rect = patches.Rectangle((x, y), CELL_SIZE, CELL_SIZE,
                                     linewidth=1, edgecolor='black', 
                                     facecolor=COLOR_MAP.get(cell, "white"))
            ax.add_patch(rect)
            if cell != EMPTY:
                if cell == CAT:
                    text = "Cat"
                elif cell == CHICK:
                    text = "Chick"
                elif cell == COW:
                    text = "Cow"
                ax.text(x + CELL_SIZE/2, y + CELL_SIZE/2, text,
                        ha='center', va='center', fontsize=8)
    ax.set_xticks([])
    ax.set_yticks([])
    return fig

def draw_new_row(new_row):
    """新行のプレビューを描画する."""
    fig, ax = plt.subplots(figsize=(COLS, 1))
    ax.set_xlim(0, COLS * CELL_SIZE)
    ax.set_ylim(0, CELL_SIZE)
    ax.invert_yaxis()
    for j in range(COLS):
        x = j * CELL_SIZE
        rect = patches.Rectangle((x, 0), CELL_SIZE, CELL_SIZE,
                                 linewidth=1, edgecolor='black', 
                                 facecolor=COLOR_MAP.get(new_row[j], "white"))
        ax.add_patch(rect)
        if new_row[j] != EMPTY:
            if new_row[j] == CAT:
                text = "Cat"
            elif new_row[j] == CHICK:
                text = "Chick"
            elif new_row[j] == COW:
                text = "Cow"
            ax.text(x + CELL_SIZE/2, CELL_SIZE/2, text,
                    ha='center', va='center', fontsize=8)
    ax.set_xticks([])
    ax.set_yticks([])
    # 上部に黄色い線を表示
    ax.axhline(0, color='yellow', linewidth=3)
    return fig

def parse_board_input(input_str):
    """
    ユーザーが入力した盤面文字列を、11×9の2次元リストに変換する。
    例:
      "0 0 0 0 0 0 0 0 0\n1 0 2 0 3 0 0 1 0\n..."
    """
    lines = input_str.strip().splitlines()
    if len(lines) != ROWS:
        raise ValueError(f"行数は必ず {ROWS} 行でなければなりません。入力行数: {len(lines)}")
    
    board_data = []
    for line in lines:
        parts = line.split()
        if len(parts) != COLS:
            raise ValueError(f"各行は必ず {COLS} 個の数値でなければなりません。")
        row = [int(value) for value in parts]
        board_data.append(row)
    return board_data

# --- Streamlit セッション状態の管理 ---
if 'board' not in st.session_state:
    st.session_state.board = Board()
if 'new_row' not in st.session_state:
    st.session_state.new_row = generate_new_row()
if 'selected_row' not in st.session_state:
    st.session_state.selected_row = None
if 'message' not in st.session_state:
    st.session_state.message = "操作してください。"

st.title("Haru Cats シミュレーション＆最適解探索 (Streamlit版)")

# 盤面描画
st.subheader("盤面")
fig_board = draw_board(st.session_state.board)
st.pyplot(fig_board)

# 新行プレビュー描画
st.subheader("次ターンに追加される行")
fig_new_row = draw_new_row(st.session_state.new_row)
st.pyplot(fig_new_row)

# 入力されたメッセージの表示
st.write(st.session_state.message)

# === 手動盤面入力用 UI ===
st.subheader("手動で盤面を入力")
manual_input = st.text_area(
    "各行は 9 個の数値(0: EMPTY, 1: CAT, 2: CHICK, 3: COW) を空白区切りで入力し、改行で区切ってください。\n例:\n0 0 0 0 0 0 0 0 0\n1 0 2 0 3 0 0 1 0\n..."
)
if st.button("盤面更新"):
    try:
        new_board_data = parse_board_input(manual_input)
        st.session_state.board.grid = new_board_data
        st.session_state.message = "盤面を更新しました。"
        st.experimental_rerun()  # 状態更新のため再描画
    except Exception as e:
        st.session_state.message = f"入力エラー: {e}"

# --- 操作用ボタン ---
col1, col2, col3, col4 = st.columns(4)

# 左にスライド
if col1.button("左にスライド"):
    if st.session_state.selected_row is not None:
        st.session_state.board.slide_row(st.session_state.selected_row, "left")
        st.session_state.board.apply_gravity()
        st.session_state.message = f"{st.session_state.selected_row} 行目を左にスライドしました。"
    else:
        st.session_state.message = "まずは行番号（0～10）を入力してください。"

# 右にスライド
if col2.button("右にスライド"):
    if st.session_state.selected_row is not None:
        st.session_state.board.slide_row(st.session_state.selected_row, "right")
        st.session_state.board.apply_gravity()
        st.session_state.message = f"{st.session_state.selected_row} 行目を右にスライドしました。"
    else:
        st.session_state.message = "まずは行番号（0～10）を入力してください。"

# 最適解の提示
if col3.button("最適解を提示"):
    move, score = get_optimal_move(st.session_state.board, st.session_state.new_row)
    if move is not None:
        row, direction = move
        st.session_state.selected_row = row
        st.session_state.message = f"提案：{row} 行目を「{direction}」にスライド（評価: {score}）"
    else:
        st.session_state.message = "有効な手が見つかりませんでした。"

# 次のターン
if col4.button("次のターン"):
    cleared = simulate_turn(st.session_state.board, st.session_state.new_row)
    st.session_state.message = f"次のターン実行！（消去行：{cleared}）"
    st.session_state.new_row = generate_new_row()
    if st.session_state.board.game_over():
        st.session_state.message = "ゲームオーバー！"

# 行番号入力欄：操作したい行番号（0～10）
selected_row_input = st.number_input("行番号を指定（0～10）", min_value=0, max_value=ROWS-1, step=1)
st.session_state.selected_row = int(selected_row_input)
