const tg = window.Telegram?.WebApp;
tg?.expand();

let initData = tg?.initData || "";      // подписанные данные
let user = tg?.initDataUnsafe?.user || null;

// Общий fetch с заголовком подписи initData
async function api(path, body, method="POST") {
  const res = await fetch(path, {
    method,
    headers: { "Content-Type":"application/json", "X-TG-INIT-DATA": initData },
    body: method==="POST" ? JSON.stringify(body||{}) : undefined
  });
  if (!res.ok) throw new Error("API error");
  return await res.json();
}

async function loadState() {
  const st = await api("/api/state", null);   // создаёт пользователя при первом заходе
  document.getElementById("coins_val").textContent = `Коины: ${st.coins}`;
  document.getElementById("energy_val").textContent = `EE: ${st.energy}`;
  document.getElementById("power_val").textContent  = `Сила клика: ${st.click_power}`;
}

document.getElementById("energize").onclick = async () => {
  const r = await api("/api/energize", {});
  if (r.ok) document.getElementById("energy_val").textContent = `EE: ${r.energy}`;
};

document.getElementById("buy_power").onclick = async () => {
  const r = await api("/api/upgrade_click", {});
  if (r.ok) {
    document.getElementById("coins_val").textContent = `Коины: ${r.coins}`;
    document.getElementById("power_val").textContent = `Сила клика: ${r.click_power}`;
  } else alert(r.error||"Ошибка");
};

document.getElementById("mine_tick").onclick = async () => {
  const use = parseInt(document.getElementById("use_energy").value||"0",10);
  const r = await api("/api/mine_tick", { use });
  if (r.ok) {
    document.getElementById("coins_val").textContent = `Коины: ${r.coins}`;
    document.getElementById("energy_val").textContent = `EE: ${r.energy}`;
  } else alert(r.error||"Ошибка");
};

document.getElementById("sell_btn").onclick = async () => {
  const amount = parseInt(document.getElementById("sell_amount").value||"0",10);
  const price  = parseFloat(document.getElementById("sell_price").value||"0");
  const r = await api("/api/order_energy", { side:"sell", amount, price_ton: price });
  alert(r.ok ? "Ордер выставлен" : (r.error||"Ошибка"));
};

async function loadTop() {
  const top = await api("/api/leaderboard", null, "GET");
  const list = document.getElementById("top_list");
  list.innerHTML = "";
  top.forEach((r,i) => {
    const li = document.createElement("li");
    li.textContent = `#${i+1} ${r.name||r.uid}: ${r.coins} коинов`;
    list.appendChild(li);
  });
}

document.querySelectorAll(".tabs button").forEach(btn=>{
  btn.onclick = ()=>{
    document.querySelectorAll(".tabs button").forEach(b=>b.classList.remove("active"));
    btn.classList.add("active");
    document.querySelectorAll(".tab").forEach(s=>s.classList.remove("active"));
    document.getElementById(btn.dataset.tab).classList.add("active");
    if (btn.dataset.tab==="top") loadTop();
  }
});

loadState().catch(console.error);
