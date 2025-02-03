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

# ハイライト範囲を計算する関数
def calculate_highlight_positions():
    highlight_positions = []
    for enemy_type, positions in st.session_state.enemy_positions.items():
        for pos in positions:
            x, y = pos
            if enemy_type == "E1":
                highlight_positions += [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]
            elif enemy_type == "E2":
                highlight_positions += [[x - 1, y - 1], [x - 1, y + 1], [x + 1, y - 1], [x + 1, y + 1]]
    return [pos for pos in highlight_positions if 0 <= pos[0] < BOARD_SIZE and 0 <= pos[1] < BOARD_SIZE]

# ボタンが押されたときにハイライトを更新（駒の位置は保持）
if st.button("敵の行動範囲をハイライト"):
    st.session_state.highlight_positions = calculate_highlight_positions()

# 盤面のHTMLを作成
html_code = f"""
<style>
  .container {{ display: flex; }}
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
<div class="container">
  <div class="board">
"""

# 盤面作成
for x in range(BOARD_SIZE):
    for y in range(BOARD_SIZE):
        cell_id = f"cell-{x}-{y}"
        content = ""
        highlight_class = "highlight" if [x, y] in st.session_state.highlight_positions else ""

        if [x, y] == st.session_state.player_pos:
            content = '<div class="draggable" draggable="true" id="player">P</div>'
        for enemy_type in ["E1", "E2"]:
            if [x, y] in st.session_state.enemy_positions[enemy_type]:
                color = "red" if enemy_type == "E1" else "blue"
                content = f'<div class="draggable" draggable="true" id="enemy-{enemy_type}" style="color: {color};">{enemy_type}</div>'

        html_code += f'<div class="cell {highlight_class}" id="{cell_id}" ondrop="drop(event)" ondragover="allowDrop(event)">{content}</div>'

html_code += """
  </div>
  <div class="enemy-pool">
"""

# 敵の駒置き場（常に駒が残る）
for enemy_type in ["E1", "E2"]:
    color = "red" if enemy_type == "E1" else "blue"
    html_code += f'<div class="cell" id="pool-{enemy_type}" ondrop="drop(event)" ondragover="allowDrop(event)"><div class="draggable" draggable="true" id="pool-{enemy_type}" style="color: {color};">{enemy_type}</div></div>'

html_code += """
  </div>
</div>
"""

# JavaScriptでドラッグ＆ドロップを制御
html_code += """
<script>
  function allowDrop(ev) { ev.preventDefault(); }
  function drag(ev) { ev.dataTransfer.setData("text", ev.target.id); }
  function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    var draggedElement = document.getElementById(data);
    if (!draggedElement) return;
    
    const cellId = ev.target.id;
    if (!cellId.startsWith("cell")) return;
    ev.target.appendChild(draggedElement.cloneNode(true));

    const position = cellId.split('-').slice(1).map(Number);
    if (data.startsWith("player")) {
      Streamlit.setComponentValue({ type: "player", position });
    } else if (data.startsWith("enemy")) {
      const enemyType = data.split('-')[1];
      Streamlit.setComponentValue({ type: "enemy", enemyType, position });
    }
  }

  document.querySelectorAll('.draggable').forEach(el => {
    el.setAttribute('ondragstart', 'drag(event)');
  });
</script>
"""

# StreamlitにHTMLを埋め込む
result = st.components.v1.html(html_code, height=BOARD_SIZE * 52 + 100, scrolling=False)

# 新しい位置を受け取ったら更新
if result is not None and isinstance(result, dict):
    if result.get("type") == "player" and result.get("position"):
        st.session_state.player_pos = result["position"]
    elif result.get("type") == "enemy" and result.get("position"):
        enemy_type = result["enemyType"]
        if result["position"] not in st.session_state.enemy_positions[enemy_type]:
            st.session_state.enemy_positions[enemy_type].append(result["position"])
