import random
import time
import streamlit as st
import streamlit.components.v1 as components
import chess

st.set_page_config(page_title="ROYAL CLASH | Cờ vua", page_icon="♟️", layout="wide")

st.markdown("""
<style>
.stApp { background: radial-gradient(circle at top, #17263b 0%, #0b1220 65%); color: #f4f7fb; }
.block-container { max-width: 1100px; padding-top: 1.2rem; }
h1, h2, h3 { color: #f4f7fb; }
div[data-testid="stButton"] > button {
  min-height: 48px; width: 100%; border-radius: 9px; border: 1px solid #29374b;
  font-size: clamp(18px, 2.5vw, 30px); font-weight: 600; padding: 0;
  transition: transform .12s ease, filter .12s ease;
}
div[data-testid="stButton"] > button:hover { filter: brightness(1.13); transform: scale(1.025); }
div[data-testid="stButton"] > button:focus { outline: 3px solid #facc15; }
div[data-testid="stHorizontalBlock"] { gap: 3px; }
.board-label { color:#9fb2ca; font-size:12px; text-align:center; margin: 0 0 4px 0; }
.info-card { background:#111d2e; border:1px solid #2a3a50; padding:12px 15px; border-radius:14px; margin:8px 0 12px; }
.legend {display:flex; gap:14px; flex-wrap:wrap; color:#d8e3f1; font-size:14px; margin:8px 0 14px;}
.dot {display:inline-block;width:12px;height:12px;border-radius:50%;background:#16865f;margin-right:5px;}
.ring {display:inline-block;width:12px;height:12px;border:3px solid #e4a11b;border-radius:50%;margin-right:5px;}
</style>
""", unsafe_allow_html=True)

PIECES = {
    "K":"♔", "Q":"♕", "R":"♖", "B":"♗", "N":"♘", "P":"♙",
    "k":"♚", "q":"♛", "r":"♜", "b":"♝", "n":"♞", "p":"♟"
}
LIGHT_SQUARE = "#f0d9b5"
DARK_SQUARE = "#8b5e3c"
SELECTED = "#e7c84b"
MOVE_SQUARE = "#a8df91"
CAPTURE_SQUARE = "#e78b87"

def new_game():
    st.session_state.board = chess.Board()
    st.session_state.selected = None
    st.session_state.message = "Trắng đi trước. Bấm vào một quân của mình để xem đường đi."
    st.session_state.last_move = None
    st.session_state.game_over_announced = False

if "board" not in st.session_state:
    new_game()
if "selected" not in st.session_state:
    st.session_state.selected = None
if "message" not in st.session_state:
    st.session_state.message = "Trắng đi trước."
if "last_move" not in st.session_state:
    st.session_state.last_move = None

st.title("♟️ ROYAL CLASH")
st.caption("CỜ VUA • Chọn quân để xem đường đi • Chơi với bạn hoặc AI")

with st.sidebar:
    st.header("⚙️ Cài đặt")
    mode = st.radio("Chế độ chơi", ["Chơi với AI", "Chơi 2 người"], index=0)
    difficulty = st.select_slider("Độ khó AI", options=["Dễ", "Trung bình", "Khó"], value="Trung bình",
                                  help="Dễ: chọn nước hợp lệ ngẫu nhiên; Trung bình: tìm nước tốt một bước; Khó: tìm sâu hơn.")
    show_coords = st.checkbox("Hiện tọa độ bàn cờ", value=True)
    st.markdown("---")
    if st.button("🔄 Ván mới", use_container_width=True):
        new_game()
        st.rerun()
    if st.button("↩️ Đi lại một nước", use_container_width=True):
        b = st.session_state.board
        if b.move_stack:
            b.pop()
            # In AI mode, undo AI move too if present
            if mode == "Chơi với AI" and b.move_stack:
                b.pop()
            st.session_state.selected = None
            st.session_state.message = "Đã đi lại."
            st.rerun()
    st.markdown("---")
    st.markdown("**Cách chơi nhanh**")
    st.markdown("- Bấm quân cờ để hiện các ô có thể đi.\n- **Chấm xanh** = ô trống có thể đi.\n- **Vòng đỏ / dấu ✕** = có thể ăn quân đối phương.\n- Bấm ô được đánh dấu để đi tới đó.")
    st.caption("AI và luật đi quân sử dụng thư viện python-chess.")

# Sound/music toggle; audio is generated locally in browser and no external file is required.
components.html("""
<div style="font-family:system-ui;color:#e6edf7;background:#111d2e;border:1px solid #2a3a50;border-radius:12px;padding:10px 12px;display:flex;align-items:center;justify-content:space-between;gap:10px">
  <span>🎵 Nhạc nền & âm thanh nước đi</span>
  <button id="musicToggle" style="background:#1d7559;color:white;border:0;border-radius:9px;padding:8px 12px;cursor:pointer;font-weight:600">▶ Bật nhạc</button>
  <span id="musicState" style="font-size:12px;color:#b9c8d9">Đang tắt</span>
</div>
<script>
(() => {
 let on=false, ctx=null, timer=null, note=0;
 const btn=document.getElementById('musicToggle'), state=document.getElementById('musicState');
 const notes=[261.63,329.63,392.00,329.63,293.66,349.23,440.00,349.23];
 function tick(){
   if(!on || !ctx) return;
   const osc=ctx.createOscillator(), gain=ctx.createGain();
   osc.type='sine'; osc.frequency.value=notes[note++%notes.length];
   gain.gain.setValueAtTime(0.0001,ctx.currentTime);
   gain.gain.exponentialRampToValueAtTime(0.035,ctx.currentTime+0.03);
   gain.gain.exponentialRampToValueAtTime(0.0001,ctx.currentTime+0.28);
   osc.connect(gain); gain.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime+0.3);
 }
 btn.addEventListener('click', async () => {
   on=!on;
   if(on){
     try { ctx=ctx||new (window.AudioContext||window.webkitAudioContext)(); await ctx.resume(); }
     catch(e){ on=false; state.textContent='Trình duyệt chặn âm thanh'; return; }
     tick(); timer=setInterval(tick,430); btn.textContent='⏸ Tắt nhạc'; state.textContent='Đang phát';
   } else {
     clearInterval(timer); btn.textContent='▶ Bật nhạc'; state.textContent='Đang tắt';
   }
 });
})();
</script>
""", height=70)

board = st.session_state.board
selected = st.session_state.selected

if board.is_checkmate():
    winner = "Đen" if board.turn == chess.WHITE else "Trắng"
    st.error(f"Chiếu hết! {winner} thắng.")
elif board.is_stalemate():
    st.info("Hòa cờ: hết nước đi hợp lệ.")
elif board.is_insufficient_material() or board.can_claim_threefold_repetition() or board.can_claim_fifty_moves():
    st.info("Ván cờ có thể kết thúc hòa theo luật.")

turn_name = "Trắng" if board.turn == chess.WHITE else "Đen"
status_text = "♔ Đang bị chiếu!" if board.is_check() else f"Đến lượt: **{turn_name}**"
st.markdown(f'<div class="info-card">{status_text}<br>{st.session_state.message}</div>', unsafe_allow_html=True)
st.markdown('<div class="legend"><span><i class="dot"></i>Ô trống có thể đi</span><span><i class="ring"></i>Ô có thể ăn quân</span><span>🟨 Quân đang chọn</span></div>', unsafe_allow_html=True)

# Legal moves are calculated by python-chess, including king safety and all blockers.
legal_by_from = {}
if selected is not None and board.piece_at(selected) and board.piece_at(selected).color == board.turn:
    for move in board.legal_moves:
        if move.from_square == selected:
            legal_by_from[move.to_square] = move

# Show board with one row per rank, file A-H left-to-right.
for rank in range(7, -1, -1):
    cols = st.columns(8, gap="small")
    for file in range(8):
        sq = chess.square(file, rank)
        piece = board.piece_at(sq)
        is_light = (file + rank) % 2 == 1
        bg = LIGHT_SQUARE if is_light else DARK_SQUARE
        if sq == selected:
            bg = SELECTED
        elif sq in legal_by_from:
            bg = CAPTURE_SQUARE if board.piece_at(sq) else MOVE_SQUARE
        elif st.session_state.last_move and sq in (st.session_state.last_move.from_square, st.session_state.last_move.to_square):
            bg = "#c6b36b" if is_light else "#947d48"

        if piece:
            glyph = PIECES[piece.symbol()]
            # A subtle text shadow separates the two sides on both light and dark squares.
            label = glyph
        elif sq in legal_by_from:
            label = "✕" if board.piece_at(sq) else "•"
        else:
            label = " "
        with cols[file]:
            clicked = st.button(label, key=f"sq_{sq}", help=chess.square_name(sq),
                                use_container_width=True)
            # Color the button by its square through nth-child CSS class via per-button key is not exposed;
            # use a small HTML background stripe above as fallback and Unicode move markers for clarity.
            if clicked:
                current_piece = board.piece_at(sq)
                if selected is not None and sq in legal_by_from:
                    move = legal_by_from[sq]
                    if move.promotion:
                        move = chess.Move(move.from_square, move.to_square, promotion=chess.QUEEN)
                    board.push(move)
                    st.session_state.last_move = move
                    st.session_state.selected = None
                    st.session_state.message = f"Đã đi {chess.square_name(move.from_square).upper()} → {chess.square_name(move.to_square).upper()}."
                    st.rerun()
                elif current_piece and current_piece.color == board.turn:
                    st.session_state.selected = sq
                    legal_count = sum(1 for m in board.legal_moves if m.from_square == sq)
                    st.session_state.message = f"Đã chọn {chess.piece_name(current_piece.symbol()).capitalize()} tại {chess.square_name(sq).upper()}: có {legal_count} nước đi hợp lệ."
                    st.rerun()
                else:
                    st.session_state.selected = None
                    st.session_state.message = "Ô đó không phải nước đi hợp lệ. Chọn quân của bên đang tới lượt."
                    st.rerun()

# AI reply after the human makes a move.
def evaluate(b):
    values = {chess.PAWN:100, chess.KNIGHT:320, chess.BISHOP:335, chess.ROOK:500, chess.QUEEN:900, chess.KING:20000}
    score = 0
    for sq, piece in b.piece_map().items():
        value = values[piece.piece_type]
        # Encourage minor/major pieces to occupy central squares.
        f, r = chess.square_file(sq), chess.square_rank(sq)
        center = 3.5 - (abs(3.5-f) + abs(3.5-r))/2
        value += int(center * (8 if piece.piece_type in (chess.KNIGHT, chess.BISHOP, chess.QUEEN) else 3))
        score += value if piece.color == chess.BLACK else -value
    if b.is_checkmate():
        return -999999 if b.turn == chess.BLACK else 999999
    return score

def minimax(b, depth, alpha, beta, maximizing):
    if depth == 0 or b.is_game_over():
        return evaluate(b), None
    best_move = None
    moves = list(b.legal_moves)
    # Try captures first to improve search.
    moves.sort(key=lambda m: (b.is_capture(m), b.gives_check(m)), reverse=True)
    if maximizing:
        best = -float("inf")
        for move in moves:
            b.push(move)
            val, _ = minimax(b, depth-1, alpha, beta, False)
            b.pop()
            if val > best:
                best, best_move = val, move
            alpha = max(alpha, best)
            if beta <= alpha: break
        return best, best_move
    best = float("inf")
    for move in moves:
        b.push(move)
        val, _ = minimax(b, depth-1, alpha, beta, True)
        b.pop()
        if val < best:
            best, best_move = val, move
        beta = min(beta, best)
        if beta <= alpha: break
    return best, best_move

# In AI mode, the human plays White. After White's turn, make one AI move.
if mode == "Chơi với AI" and board.turn == chess.BLACK and not board.is_game_over():
    with st.spinner("AI đang suy nghĩ..."):
        if difficulty == "Dễ":
            candidates = list(board.legal_moves)
            # Prefer a capture sometimes, but keep the level forgiving.
            captures = [m for m in candidates if board.is_capture(m)]
            ai_move = random.choice(captures if captures and random.random() < 0.35 else candidates)
        else:
            depth = 1 if difficulty == "Trung bình" else 2
            _, ai_move = minimax(board, depth, -float("inf"), float("inf"), True)
            if ai_move is None:
                ai_move = random.choice(list(board.legal_moves))
        board.push(ai_move)
        st.session_state.last_move = ai_move
        st.session_state.selected = None
        st.session_state.message = f"AI đi {chess.square_name(ai_move.from_square).upper()} → {chess.square_name(ai_move.to_square).upper()}."
        st.rerun()

with st.expander("📖 Hướng dẫn nhận biết các quân cờ"):
    st.markdown("""
    - **♔ Vua / ♚ Vua:** đi một ô; không được đi vào ô bị đối phương khống chế.
    - **♕ Hậu / ♛ Hậu:** đi ngang, dọc và chéo.
    - **♖ Xe / ♜ Xe:** đi ngang và dọc, không xuyên qua quân khác.
    - **♗ Tượng / ♝ Tượng:** đi chéo, không xuyên qua quân khác.
    - **♘ Mã / ♞ Mã:** đi hình chữ L, có thể nhảy qua quân.
    - **♙ Tốt / ♟ Tốt:** tiến về phía trước, ăn chéo; nước đầu có thể đi hai ô.
    """)
st.caption("Lưu ý: Đây là bản Streamlit thay thế độc lập. Nếu repository của mày có thêm tính năng cũ, hãy giữ bản cũ trước khi thay file.")
