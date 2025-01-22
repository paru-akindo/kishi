import streamlit as st

# 初期設定
BOARD_SIZE = 8  # 碁盤のサイズ
player_pos = [3, 3]  # 自分のコマの初期位置
initial_enemy_positions = {"E1": [[1, 1]], "E2": [[6, 6]]}  # 敵のコマの初期位置

# セッション状態を保持
if "player_pos" not in st.session_state:
    st.session_state.player_pos = player_pos
if "enemy_positions" not in st.session_state:
    st.session_state.enemy_positions = initial_enemy_positions

# ハイライト範囲を動的に計算する関数
def calculate_highlight_positions():
    highlight_positions = []
    for enemy_type, positions in st.session_state.enemy_positions.items():
        for pos in positions:
            x, y = pos
            if enemy_type == "E1":
                highlight_positions += [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]
            elif enemy_type == "E2":
                highlight_positions += [[x - 1, y - 1], [x - 1, y + 1], [x + 1, y - 1], [x + 1, y + 1]]
    return highlight_positions

highlight_positions = calculate_highlight_positions()

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
        highlight_class = "highlight" if [x, y] in highlight_positions else ""

        # 駒を配置
        if [x, y] == st.session_state.player_pos:
            content = '<div class="draggable" draggable="true" id="player">P</div>'
        elif [x, y] in st.session_state.enemy_positions["E1"]:
            content = '<div class="draggable" draggable="true" id="enemy-E1" style="color: red;">E1</div>'
        elif [x, y] in st.session_state.enemy_positions["E2"]:
            content = '<div class="draggable" draggable="true" id="enemy-E2" style="color: blue;">E2</div>'

        html_code += f'<div class="cell {highlight_class}" id="{cell_id}" ondrop="drop(event)" ondragover="allowDrop(event)">{content}</div>'

html_code += """
  </div>
  <div class="enemy-pool">
"""

# 敵の駒置き場を作成（駒が消えないようにする）
for i in range(2):  # E1とE2の駒置き場
    enemy_type = f"E{i+1}"
    html_code += f'<div class="cell" id="pool-{enemy_type}" ondrop="drop(event)" ondragover="allowDrop(event)"><div class="draggable" draggable="true" id="pool-{enemy_type}" style="color: {"red" if enemy_type == "E1" else "blue"};">{enemy_type}</div></div>'

html_code += """
  </div>
</div>
"""

# JavaScriptでドラッグ＆ドロップを制御
html_code += """
<script>
  function allowDrop(ev) {
    ev.preventDefault();
  }

  function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
  }

  function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    var draggedElement = document.getElementById(data);
    ev.target.appendChild(draggedElement);

    // Send the new position to Streamlit
    const cellId = ev.target.id;
    const position = cellId.includes("cell") ? cellId.split('-').slice(1).map(Number) : null;

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
        st.session_state.enemy_positions[enemy_type].append(result["position"])
    highlight_positions = calculate_highlight_positions()  # ハイライトを再計算
