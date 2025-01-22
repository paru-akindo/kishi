import streamlit as st

# 初期設定
BOARD_SIZE = 8  # 碁盤のサイズ
player_pos = [3, 3]  # 自分のコマの初期位置
initial_enemy_positions = {"E1": [[1, 1]], "E2": [[6, 6]]}  # 敵のコマの初期位置

# Streamlitアプリ
st.title("ボードゲームシミュレータ")

# セッション状態を保持
if "player_pos" not in st.session_state:
    st.session_state.player_pos = player_pos
if "enemy_positions" not in st.session_state:
    st.session_state.enemy_positions = initial_enemy_positions

# HTMLとCSSで盤面と敵の駒置き場を作成
html_code = f"""
<style>
  .container {{
    display: flex;
  }}
  .board {{
    display: grid;
    grid-template-columns: repeat({BOARD_SIZE}, 50px);
    grid-template-rows: repeat({BOARD_SIZE}, 50px);
    gap: 1px;
    background-color: black;
    margin-right: 20px;
  }}
  .enemy-pool {{
    display: grid;
    grid-template-columns: repeat(2, 50px);
    gap: 1px;
  }}
  .cell {{
    width: 50px;
    height: 50px;
    background-color: #f0d9b5;
    position: relative;
    text-align: center;
    line-height: 50px;
    font-size: 24px;
    font-weight: bold;
    cursor: pointer;
  }}
  .highlight {{
    background-color: #ffcccc;
  }}
  .draggable {{
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
</style>
<div class="container">
  <div class="board">
"""

# 盤面を作成し、自分のコマと敵のコマを配置
for x in range(BOARD_SIZE):
    for y in range(BOARD_SIZE):
        cell_id = f"cell-{x}-{y}"
        content = ""
        highlight_class = ""

        # ハイライト（E1の上下左右、E2の斜め）
        highlight_positions = []
        for enemy_type, positions in st.session_state.enemy_positions.items():
            for pos in positions:
                if pos == [x, y]:
                    if enemy_type == "E1":
                        highlight_positions += [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]
                    elif enemy_type == "E2":
                        highlight_positions += [[x - 1, y - 1], [x - 1, y + 1], [x + 1, y - 1], [x + 1, y + 1]]

        if [x, y] in highlight_positions:
            highlight_class = "highlight"

        # 駒を配置
        if [x, y] == st.session_state.player_pos:
            content = '<div class="draggable" draggable="true" id="player">P</div>'
        elif [x, y] in st.session_stat
