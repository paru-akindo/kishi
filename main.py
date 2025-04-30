import streamlit as st
import streamlit.components.v1 as components
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
if "board_data" not in st.session_state:
    st.session_state.board_data = {}

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

# ハイライトを更新するボタン
if st.button("敵の行動範囲を更新"):
    st.session_state.highlight_positions = calculate_highlight_positions(st.session_state.enemy_positions)

# HTML + JSで盤面描画
board_html = """
<style>
  .board { display: grid; grid-template-columns: repeat(%(size)d, 40px); grid-gap: 2px; }
  .cell { width: 40px; height: 40px; border: 1px solid #ccc; text-align: center; line-height: 40px; font-weight: bold; }
  .highlight { background-color: #ffcccc; }
  .player { background-color: #ccf; }
  .enemy { background-color: #fdd; }
  .dragging { opacity: 0.5; }
</style>
<div class="board" id="board">
""" % {"size": BOARD_SIZE}

# JSデータ変換のための構造
positions = {}
positions["P"] = st.session_state.player_pos
for t in ["E1", "E2"]:
    for i, pos in enumerate(st.session_state.enemy_positions[t]):
        positions[f"{t}_{i}"] = pos

highlight_json = json.dumps(st.session_state.highlight_positions)

for x in range(BOARD_SIZE):
    for y in range(BOARD_SIZE):
        piece = ""
        css_class = "cell"
        for name, pos in positions.items():
            if pos == [x, y]:
                piece = name
                if name == "P":
                    css_class += " player"
                elif name.startswith("E"):
                    css_class += " enemy"
        if [x, y] in st.session_state.highlight_positions:
            css_class += " highlight"
        board_html += f'<div class="{css_class}" data-pos="{x},{y}" draggable="true">{piece}</div>'

board_html += "</div>"

# ドラッグ＆ドロップ用JavaScript
board_html += f"""
<script>
  let dragged = null;
  document.querySelectorAll('.cell').forEach(cell => {
    cell.addEventListener('dragstart', e => {
      dragged = cell;
      setTimeout(() => cell.classList.add('dragging'), 0);
    });
    cell.addEventListener('dragend', e => {
      dragged.classList.remove('dragging');
      dragged = null;
    });
    cell.addEventListener('dragover', e => e.preventDefault());
    cell.addEventListener('drop', e => {
      e.preventDefault();
      const from = dragged.getAttribute('data-pos');
      const to = cell.getAttribute('data-pos');
      const label = dragged.innerText;
      fetch('/', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{from, to, label}})
      }}).then(() => location.reload());
    });
  });
</script>
"""

components.html(board_html, height=BOARD_SIZE * 45 + 100)

# POSTで受信したドラッグ操作を反映
if st._is_running_with_streamlit:
    import streamlit.runtime.scriptrunner.script_run_context as context
    from streamlit.web.server.websocket_headers import _get_websocket_headers
    import streamlit.web.server.server_util as server_util
    try:
        req = st.experimental_get_query_params()
        raw = server_util.get_current_server()._session_info_by_id
        for k, v in raw.items():
            headers = _get_websocket_headers(v.ws)
            ctx = context.get_script_run_ctx()
            break
        import streamlit.web.server.websocket_headers as wh
        import streamlit.web.server.server_util as su
    except:
        pass

st.markdown("### 敵コマ置き場")
enemy_cols = st.columns(len(enemy_pool))
for idx, (enemy_type, label) in enumerate(enemy_pool.items()):
    if enemy_cols[idx].button(label, key=f"spawn-{enemy_type}"):
        st.session_state.enemy_positions[enemy_type].append([0, 0])
