def get_matrix_game_html(user, get_transfer_js):
    js = get_transfer_js(user)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
body{{background:#050505;color:#00ffff;margin:0;text-align:center}}
canvas{{background:#111;border:2px solid #333;margin-top:10px}}
.btn{{position:absolute;top:10px;right:10px;background:#ff00ff;border:none;padding:5px 15px;border-radius:15px;font-weight:bold;color:white}}
</style>
</head>

<body>
<div style="padding:10px;display:flex;justify-content:space-between">
<span>PUAN: <span id="s">0</span></span>
<button id="mBtn" class="btn" onclick="autoTransfer()">AKTAR</button>
</div>

<canvas id="c"></canvas>

<script>
let score=0;
document.getElementById('s').innerText=score;
{js}
</script>
</body>
</html>"""