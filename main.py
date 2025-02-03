import streamlit as st

# 初期設定
BOARD_SIZE = 8  # 碁盤のサイズ
player_pos = [3, 3]  # 自分のコマの初期位置
initial_enemy_positions = {"E1": [[1, 1]], "E2": [[6, 6]]}  # 敵のコマの初期位置

# セッション状態を保持
if "player_pos" not in st.session_state:
    st.session_state.player_pos = player_pos
if "enemy_positions" not in st.session_state:
    st.session_state.enemy_positions = {"E1": [[1, 1]], "E2": [[6, 6]]}  # 変更しない初期値
if "highlight_positions" not in st.session_state:
    st.session_state.highlight_positions = []
if "saved_board" not in st.session_state:
    st.session_state.saved_board = {}

# 駒置き場の定義
enemy_pool = {"E1": "E1", "E2": "E2"}

# ハイライト範囲を計算する関数
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

# ボタンが押されたときに現在の盤面を保存し、ハイライトを計算
if st.button("敵の行動範囲をハイライト"):
    st.session_state.saved_board = {
        "player_pos": st.session_state.player_pos,
        "enemy_positions": {k: v[:] for k, v in st.session_state.enemy_positions.items()}  # 深いコピー
    }
    st.session_state.highlight_positions = calculate_highlight_positions(st.session_state.saved_board["enemy_positions"])

# 盤面を描画する関数
def render_board(player_pos, enemy_positions, highlight_positions, include_enemy_pool=True):
    html_code = f"""
    <style>
      .container {{ display: flex; flex-direction: column; gap: 20px; }}
      .board {{
        display: grid;
        grid-template-columns: repeat({BOARD_SIZE}, 50px);
        grid-template-rows: repeat({BOARD_SIZE}, 50px);
        gap: 1px;
        background-color: black;
        margin-right: 20px;
      }}
      .enemy-pool {{ display: grid; grid-template-columns: repeat(2, 50px); gap: 1px; }}
      .cell {{
        width: 50px;
        height: 50px;
        background-color: #f0d9b5;
        text-align: center;
        line-height: 50px;
        font-size: 24px;
        font-weight: bold;
        cursor: pointer;
      }}
      .highlight {{ background-color: #ffcccc; }}
      .draggable {{ display: flex; align-items: center; justify-content: center; }}
    </style>
    <div class="board">
    """

    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            cell_id = f"cell-{x}-{y}"
            content = ""
            highlight_class = "highlight" if [x, y] in highlight_positions else ""

            if [x, y] == player_pos:
                content = f'<div class="draggable" draggable="true" id="player" ondragstart="drag(event)">P</div>'
            for enemy_type in ["E1", "E2"]:
                if [x, y] in enemy_positions[enemy_type]:
                    color = "red" if enemy_type == "E1" else "blue"
                    content = f'<div class="draggable" draggable="true" id="enemy-{x}-{y}-{enemy_type}" ondragstart="drag(event)" style="color: {color};">{enemy_type}</div>'

            html_code += f'<div class="cell {highlight_class}" id="{cell_id}" ondrop="drop(event)" ondragover="allowDrop(event)">{content}</div>'

    html_code += "</div>"
    
    if include_enemy_pool:
        html_code += "<div class='enemy-pool'>"
        for enemy_type, label in enemy_pool.items():
            html_code += f'<div class="cell" id="pool-{enemy_type}" ondrop="drop(event)" ondragover="allowDrop(event)"><div class="draggable" draggable="true" id="enemy-{enemy_type}" ondragstart="drag(event)">{label}</div></div>'
        html_code += "</div>"
    
    html_code += """
    <script>
    function allowDrop(ev) {{
      ev.preventDefault();
    }}
    function drag(ev) {{
      ev.dataTransfer.setData("text", ev.target.id);
    }}
    function drop(ev) {{
      ev.preventDefault();
      var data = ev.dataTransfer.getData("text");
      var draggedElement = document.getElementById(data);
      ev.target.appendChild(draggedElement);
    }}
    </script>
    """
    
    return html_code

st.components.v1.html(render_board(st.session_state.player_pos, st.session_state.enemy_positions, [], include_enemy_pool=True), height=BOARD_SIZE * 52 + 150, scrolling=False)

if st.session_state.saved_board:
    st.write("### 敵の行動範囲ハイライト")
    st.components.v1.html(render_board(st.session_state.saved_board["player_pos"], st.session_state.saved_board["enemy_positions"], st.session_state.highlight_positions, include_enemy_pool=False), height=BOARD_SIZE * 52 + 100, scrolling=False)
