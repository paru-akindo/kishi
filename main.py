import streamlit as st

# セッションステートの初期化
if "board" not in st.session_state:
    # 8x8のボード。各セルは (row, col) をキーに、None または駒の文字列（例："knight", "rook"）を保持する
    st.session_state.board = {(r, c): None for r in range(8) for c in range(8)}
if "selected_piece_coord" not in st.session_state:
    st.session_state.selected_piece_coord = None
if "highlighted_moves" not in st.session_state:
    st.session_state.highlighted_moves = []

def compute_moves(piece, pos):
    """
    与えられた駒の種類と現在の位置 pos に対して、移動可能なセルの座標リストを返す。
    この例では knight（ナイト）と rook（ルーク）のみを実装。
    """
    moves = []
    r, c = pos
    if piece == "knight":
        # ナイトの移動パターン：L字型
        offsets = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in offsets:
            r_new = r + dr
            c_new = c + dc
            if 0 <= r_new < 8 and 0 <= c_new < 8:
                moves.append((r_new, c_new))
    elif piece == "rook":
        # ルークは縦横全方向
        for i in range(8):
            if i != r:
                moves.append((i, c))
        for j in range(8):
            if j != c:
                moves.append((r, j))
    # 他の駒の動きをここに追加可能
    return moves

st.title("チェス風ボードの移動範囲表示")

# サイドバーで駒を配置するための設定
st.sidebar.subheader("駒を配置する")
piece_type = st.sidebar.selectbox("駒の種類を選択", ["knight", "rook"])
place_cell = st.sidebar.text_input("配置するセル (例: 3,4)", value="")

if st.sidebar.button("駒を配置") and place_cell:
    try:
        # カンマ区切りの入力から行と列を取得
        row, col = map(int, place_cell.split(","))
        if 0 <= row < 8 and 0 <= col < 8:
            st.session_state.board[(row, col)] = piece_type
        else:
            st.sidebar.write("セルの値は 0 から 7 の範囲で指定してください。")
    except Exception as e:
        st.sidebar.write("入力フォーマットが正しくありません。例: 3,4")

st.write("※ボード上のセルをクリックすると、そこに駒がある場合はその駒の移動可能範囲をハイライトします。ハイライトされたセルをクリックすると、駒が移動されます。")

# ボードのレンダリング
for r in range(8):
    cols = st.columns(8)
    for c in range(8):
        cell = (r, c)
        # セルに表示する文字列：駒がある場合はその名前、なければドットで表示
        cell_content = st.session_state.board[cell] if st.session_state.board[cell] is not None else ""
        # 移動可能範囲に含まれている場合は見た目を変える（ここでは装飾用に ** を付加）
        if cell in st.session_state.highlighted_moves:
            button_label = f"**{cell_content}**" if cell_content else "**.**"
        else:
            button_label = cell_content if cell_content else "."
        # 各セルをボタンとして配置
        if cols[c].button(button_label, key=f"cell_{r}_{c}"):
            # もしクリックされたセルに駒があるなら、その駒を選択して移動可能範囲を算出
            if st.session_state.board[cell] is not None:
                st.session_state.selected_piece_coord = cell
                st.session_state.highlighted_moves = compute_moves(st.session_state.board[cell], cell)
            else:
                # すでに選択中の駒があり、クリックされたセルが移動可能な範囲内なら移動実行
                if cell in st.session_state.highlighted_moves and st.session_state.selected_piece_coord is not None:
                    piece = st.session_state.board[st.session_state.selected_piece_coord]
                    st.session_state.board[cell] = piece
                    st.session_state.board[st.session_state.selected_piece_coord] = None
                # 移動後、選択状態とハイライトをクリア
                st.session_state.selected_piece_coord = None
                st.session_state.highlighted_moves = []
