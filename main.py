import streamlit as st
import numpy as np
import pandas as pd

# 初期設定
BOARD_SIZE = 8  # 碁盤のサイズ
player_pos = [3, 3]  # 自分のコマの初期位置
enemy_positions = [[1, 1], [2, 5], [6, 6]]  # 敵のコマの初期位置

def draw_board(player_pos, enemy_positions):
    """盤面を描画する"""
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=str)
    board[player_pos[0], player_pos[1]] = "P"  # 自分のコマ
    for pos in enemy_positions:
        board[pos[0], pos[1]] = "E"  # 敵のコマ
    return board

def get_enemy_range(enemy_positions):
    """敵が動ける範囲を計算する"""
    ranges = set()
    for ex, ey in enemy_positions:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 上下左右に1マス移動可能
            nx, ny = ex + dx, ey + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                ranges.add((nx, ny))
    return ranges

# Streamlitアプリ
st.title("ボードゲームシミュレータ")
st.write("盤面をクリックしてコマを動かしてみましょう。")

# セッション状態を保持
if "player_pos" not in st.session_state:
    st.session_state.player_pos = player_pos
if "enemy_positions" not in st.session_state:
    st.session_state.enemy_positions = enemy_positions

# 盤面の描画
board = draw_board(st.session_state.player_pos, st.session_state.enemy_positions)
enemy_range = get_enemy_range(st.session_state.enemy_positions)

# 盤面をデータフレームとして表示
df = pd.DataFrame(board)
st.dataframe(df.style.applymap(lambda x: "background-color: yellow" if (x == "P") else "background-color: red" if (x == "E") else ""))

# ユーザーの入力を受け付ける
col1, col2 = st.columns(2)
with col1:
    new_x = st.number_input("新しいX座標", min_value=0, max_value=BOARD_SIZE - 1, value=st.session_state.player_pos[0])
with col2:
    new_y = st.number_input("新しいY座標", min_value=0, max_value=BOARD_SIZE - 1, value=st.session_state.player_pos[1])

# コマの移動
if st.button("移動"):
    if (new_x, new_y) in enemy_range:
        st.warning("その位置は敵の範囲内です！")
    else:
        st.session_state.player_pos = [new_x, new_y]
        st.success("移動しました！")

# 敵の範囲を表示
st.write("敵が動ける範囲:")
enemy_range_df = pd.DataFrame(np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=str))
for ex, ey in enemy_range:
    enemy_range_df.iloc[ex, ey] = "R"
st.dataframe(enemy_range_df.style.applymap(lambda x: "background-color: orange" if x == "R" else ""))
