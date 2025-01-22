import streamlit as st
import numpy as np

# 初期設定
BOARD_SIZE = 8  # 碁盤のサイズ
player_pos = [3, 3]  # 自分のコマの初期位置
enemy_positions = [[1, 1], [2, 5], [6, 6]]  # 敵のコマの初期位置

# Streamlitアプリ
st.title("ドラッグ＆ドロップ対応ボードゲームシミュレータ")

# セッション状態を保持
if "player_pos" not in st.session_state:
    st.session_state.player_pos = player_pos
if "enemy_positions" not in st.session_state:
    st.session_state.enemy_positions = enemy_positions

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
  .cell:nth-child(odd) {{ background-color: #b58863; }}
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
        if [x, y] == st.session_state.player_pos:
            content = '<div class="draggable" draggable="true" id="player">P</div>'
        elif [x, y] in st.session_state.enemy_positions:
            enemy_index = st.session_state.enemy_positions.index([x, y])
            content = f'<div class="draggable" draggable="true" id="enemy-{enemy_index}" style="color: red;">E</div>'
        else:
            content = ""
        html_code += f'<div class="cell" id="{cell_id}" ondrop="drop(event)" ondragover="allowDrop(event)">{content}</div>'

html_code += """
  </div>
  <div class="enemy-pool">
"""

# 敵のコマ置き場を作成
for i in range(5):  # 最大5個の敵コマを置き場に表示
    html_code += f'<div class="cell" id="pool-{i}" ondrop="drop(event)" ondragover="allowDrop(event)"><div class="draggable" draggable="true" id="pool-enemy-{i}" style="color: red;">E</div></div>'

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
      const enemyIndex = parseInt(data.split('-')[1]);
      Streamlit.setComponentValue({ type: "enemy", index: enemyIndex, position });
    } else if (data.startsWith("pool-enemy")) {
      const poolIndex = parseInt(data.split('-')[2]);
      Streamlit.setComponentValue({ type: "new_enemy", poolIndex, position });
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
        st.success(f"自分のコマを移動しました: {result['position']}")
    elif result.get("type") == "enemy" and result.get("position"):
        st.session_state.enemy_positions[result["index"]] = result["position"]
        st.success(f"敵のコマを移動しました: {result['position']}")
    elif result.get("type") == "new_enemy" and result.get("position"):
        st.session_state.enemy_positions.append(result["position"])
        st.success(f"敵のコマを新たに配置しました: {result['position']}")
else:
    st.info("コマを動かしてみてください。")
