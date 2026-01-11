def get_finance_game_html(start, user, get_transfer_js):
    js = get_transfer_js(user)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
body{{background:#0f172a;color:#fff;font-family:sans-serif;padding:5px;text-align:center}}
.tab{{display:flex;justify-content:center;gap:10px;margin-bottom:10px}}
.tab button{{background:#334155;border:none;color:#fff;padding:8px;border-radius:5px;cursor:pointer}}
.active{{background:#3b82f6!important}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:5px}}
.card{{background:#1e293b;padding:8px;border-radius:5px;border:1px solid #475569;cursor:pointer}}
.btn{{background:radial-gradient(circle,#3b82f6,#1d4ed8);width:80px;height:80px;border-radius:50%;margin:10px auto;display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:0 0 15px #3b82f6;cursor:pointer}}
.bank{{background:#10b981;color:white;width:100%;padding:12px;border:none;border-radius:8px;margin-top:10px;font-weight:bold}}
</style>
</head>

<body>
<div style="font-size:20px;font-weight:bold;color:#fbbf24">
💰 <span id="m">{start}</span>
</div>

<div style="font-size:12px;color:#94a3b8">
Gelir: <span id="cps">0</span>/sn
</div>

<div class="tab">
<button onclick="sTab('main')" class="active" id="btn-main">İşletme</button>
<button onclick="sTab('mgr')" id="btn-mgr">Yöneticiler</button>
</div>

<div id="main">
<div class="btn" onclick="clk()">👆</div>
<div class="grid" id="market"></div>
</div>

<div id="mgr" style="display:none">
<div class="grid" id="managers"></div>
</div>

<button id="bBtn" class="bank" onclick="autoTransfer()">🏦 KASAYI BANKAYA AKTAR</button>

<script>
let money={start},startBalance={start};

const assets=[
{{n:"Limonata",c:100,g:1,k:0}},
{{n:"Simit",c:500,g:5,k:0}},
{{n:"Kantin",c:2500,g:30,k:0}},
{{n:"Cafe",c:10000,g:100,k:0}},
{{n:"Yazılım",c:50000,g:600,k:0}},
{{n:"Fabrika",c:200000,g:3000,k:0}},
{{n:"Banka",c:1000000,g:15000,k:0}}
];

const mgrs=[
{{n:"Çırak",c:5000,e:0,desc:"Limonata/Simit Oto"}},
{{n:"Müdür",c:50000,e:0,desc:"Kantin/Cafe Oto"}},
{{n:"CEO",c:1000000,e:0,desc:"x2 Hız"}}
];

function update() {{
document.getElementById('m').innerText=Math.floor(money).toLocaleString();
let total=assets.reduce((t,x)=>t+(x.k*x.g),0)*(mgrs[2].e?2:1);
document.getElementById('cps').innerText=total.toLocaleString();
}}

function clk(){{ money+=1; update(); }}

setInterval(()=>{{ 
let g=assets.reduce((t,x)=>t+(x.k*x.g),0);
money+=g/10;
update();
}},100);

update();
{js}
</script>
</body>
</html>"""