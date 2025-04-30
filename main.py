import streamlit as st
import json

# 初期設定
BOARD_SIZE = 8
player_pos = [3, 3]
initial_enemy_positions = {"E1": [[1, 1]], "E2": [[6, 6]]}

if "player_pos" not in st.session_state:
    st.session_state.player_pos = player_pos
if "enemy_positions" not in st.session_state:
    st.session_state.enemy_positions = {"E1": [[1, 1]], "E2": [[6, 6]]}
if "highlight_positions" not in st.session_state:
    st.session_state.highlight_positions = []
if "selected_pos" not in st.session_state:
    st.session_state.selected_pos = None

enemy_pool = {"E1": "E1", "E2": "E2"}

def calculate_highlight_positions(enemy_positions):
    highlight_positions = []
    for enemy_type, positions in enemy_positions.items():
        for pos in positions:
            x, y = pos
            if enemy_type == "E1":
                highlight_positions += [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]
            elif enemy_type == "E2":
                highlight_positions += [[x - 1, y - 1], [x - 1, y + 1], [x + 1, y - 1], [x + 1, y + 1]]
    return [pos for pos in highlight_positions if 0 <= pos[0] < BOARD_SIZE and 0 <= pos[1] < BOARD_SIZE]

if st.button("敵の行動範囲を更新"):
    st.session_state.highlight_positions = calculate_highlight_positions(st.session_state.enemy_positions)

st.write("盤面上のコマをクリックして選択し、移動先のマスをクリックしてください")

def render_board():
    for x in range(BOARD_SIZE):
        cols = st.columns(BOARD_SIZE)
        for y in range(BOARD_SIZE):
            label = ""
            if [x, y] == st.session_state.player_pos:
                label = "P"
            else:
                for enemy_type, positions in st.session_state.enemy_positions.items():
                    if [x, y] in positions:
                        label = enemy_type

            style = ""
            if [x, y] == st.session_state.selected_pos:
                style = "background-color: yellow;"
            elif [x, y] in st.session_state.highlight_positions:
                style = "background-color: #ffcccc;"

            if cols[y].button(label or " ", key=f"cell-{x}-{y}", help=f"{x},{y}"):
                if st.session_state.selected_pos is None:
                    # コマがある場所なら選択
                    if [x, y] == st.session_state.player_pos or any([x, y] in v for v in st.session_state.enemy_positions.values()):
                        st.session_state.selected_pos = [x, y]
                else:
                    sel = st.session_state.selected_pos
                    # プレイヤー移動
                    if sel == st.session_state.player_pos:
                        st.session_state.player_pos = [x, y]
                    else:
                        for k in st.session_state.enemy_positions:
                            if sel in st.session_state.enemy_positions[k]:
                                st.session_state.enemy_positions[k] = [pos for pos in st.session_state.enemy_positions[k] if pos != sel]
                                st.session_state.enemy_positions[k].append([x, y])
                    st.session_state.selected_pos = None
                    st.session_state.highlight_positions = []  # 移動後はハイライトを一旦消す

render_board()

st.markdown("### 敵コマ置き場")
enemy_cols = st.columns(len(enemy_pool))
for idx, (enemy_type, label) in enumerate(enemy_pool.items()):
    if enemy_cols[idx].button(label, key=f"spawn-{enemy_type}"):
        st.session_state.enemy_positions[enemy_type].append([0, 0])
