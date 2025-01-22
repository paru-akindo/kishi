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

# HTMLとCSSで盤面を作成
html_code = f"""
<style>
  .board {{
    display: grid;
    grid-template-columns: repeat({BOARD_SIZE}, 50px);
    grid-template-rows: repeat({BOARD_SIZE}, 50px);
    gap: 1px;
    background-color: black;
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
<div class="board">
"""

# 盤面を作成し、自分のコマと敵のコマを配置
for x in range(BOARD_SIZE):
    for y in range(BOARD_SIZE):
        cell_id = f"cell-{x}-{y}"
        if [x, y] == st.session_state.player_pos:
            content = '<div class="draggable" draggable="true" id="player">P</div>'
        elif [x, y] in st.session_state.enemy_positions:
            content = '<div class="draggable" draggable="false" style="color: red;">E</div>'
        else:
            content = ""
        html_code += f'<div class="cell" id="{cell_id}" ondrop="drop(event)" ondragover="allowDrop(event)">{content}</div>'

html_code += "</div>"

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
    const position = cellId.split('-').slice(1).map(Number);
    Streamlit.setComponentValue(position);
  }

  document.querySelectorAll('.draggable').forEach(el => {
    el.setAttribute('ondragstart', 'drag(event)');
  });
</script>
"""

# StreamlitにHTMLを埋め込む
position = st.components.v1.html(html_code, height=BOARD_SIZE * 52, scrolling=False)

# 新しい位置を受け取ったら更新
if position:
    st.session_state.player_pos = position
    st.success(f"コマを移動しました: {position}")
