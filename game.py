import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="벽돌깨기 게임 (모바일)", page_icon="🧱", layout="centered")

st.title("🧱 벽돌깨기 게임 — 모바일 버전")
st.caption("화면을 드래그하거나 하단 버튼으로 패들 조작 · 손가락으로 즐기는 스테이지 & 파워업 에디션")

GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
  * { -webkit-tap-highlight-color: transparent; }
  html, body {
    margin: 0;
    padding: 0;
    background: #0f1117;
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: 'Segoe UI', sans-serif;
    overscroll-behavior: none;
    touch-action: manipulation;
  }
  #wrap {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    max-width: 360px;
    box-sizing: border-box;
    padding: 6px;
  }
  #ui {
    color: #fff;
    display: flex;
    justify-content: space-between;
    width: 100%;
    padding: 6px 4px;
    font-size: 12.5px;
    box-sizing: border-box;
    flex-wrap: wrap;
    gap: 4px;
  }
  #ui span { white-space: nowrap; }
  #canvasHolder {
    width: 100%;
    max-width: 340px;
    touch-action: none;
  }
  #gameCanvas {
    background: #1a1c25;
    border: 2px solid #3a3d4d;
    border-radius: 8px;
    display: block;
    width: 100%;
    height: auto;
    touch-action: none;
  }
  #overlay {
    position: absolute;
    color: #fff;
    text-align: center;
    font-size: 16px;
    background: rgba(0,0,0,0.75);
    padding: 16px 20px;
    border-radius: 10px;
    display: none;
    white-space: pre-line;
    line-height: 1.55;
    max-width: 260px;
  }
  .controls {
    display: flex;
    width: 100%;
    justify-content: space-between;
    gap: 6px;
    margin-top: 8px;
  }
  .ctl-btn {
    flex: 1;
    padding: 14px 0;
    font-size: 15px;
    border: none;
    border-radius: 10px;
    background: #2b2f3f;
    color: #fff;
    user-select: none;
    touch-action: manipulation;
  }
  .ctl-btn:active { background: #4f5570; }
  #laserBtn { background: #6c5ce7; }
  #laserBtn:active { background: #5849c4; }
  #pauseBtn { background: #4f8cff; }
  #pauseBtn:active { background: #3a75e0; }
  #resetBtn { background: #ff6b6b; }
  #resetBtn:active { background: #e05555; }
  #legend {
    color: #9aa0b4;
    font-size: 10.5px;
    width: 100%;
    margin-top: 8px;
    text-align: center;
    line-height: 1.6;
  }
</style>
</head>
<body>
<div id="wrap">
  <div id="ui">
    <span>점수:<span id="score">0</span></span>
    <span>StG:<span id="stage">1</span></span>
    <span>♥:<span id="lives">3</span></span>
    <span>콤보:x<span id="combo">1</span></span>
  </div>
  <div id="canvasHolder">
    <canvas id="gameCanvas" width="340" height="420"></canvas>
  </div>
  <div id="overlay"></div>

  <div class="controls">
    <button class="ctl-btn" id="leftBtn">◀</button>
    <button class="ctl-btn" id="laserBtn">⚡레이저</button>
    <button class="ctl-btn" id="rightBtn">▶</button>
  </div>
  <div class="controls">
    <button class="ctl-btn" id="pauseBtn">⏸ 일시정지</button>
    <button class="ctl-btn" id="resetBtn">🔄 처음부터</button>
  </div>
  <div id="legend">🔵E 확대 · 🔴S 축소 · 🟡M 멀티볼 · 💗+ 목숨 · 🟢W 슬로우 · 🟣L 레이저<br>화면을 좌우로 드래그해도 패들이 움직여요</div>
</div>

<script>
if (!CanvasRenderingContext2D.prototype.roundRect) {
  CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
    if (w < 2 * r) r = w / 2;
    if (h < 2 * r) r = h / 2;
    this.beginPath();
    this.moveTo(x + r, y);
    this.arcTo(x + w, y, x + w, y + h, r);
    this.arcTo(x + w, y + h, x, y + h, r);
    this.arcTo(x, y + h, x, y, r);
    this.arcTo(x, y, x + w, y, r);
    this.closePath();
    return this;
  };
}

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const overlay = document.getElementById("overlay");

const ballRadius = 6;
const paddleHeight = 10;
const basePaddleWidth = 72;
const brickWidth = 40, brickHeight = 16, brickPadding = 6;
const brickOffsetTop = 34, brickOffsetLeft = 12;
const colorsByRow = ["#ff6b6b", "#feca57", "#1dd1a1", "#54a0ff", "#a29bfe", "#ff9ff3"];

const STAGES = [
[
 [1,1,1,1,1,1,1],
 [1,1,1,1,1,1,1],
 [1,1,1,1,1,1,1],
 [1,1,1,1,1,1,1],
 [0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0],
],
[
 [2,0,2,0,2,0,2],
 [0,1,0,1,0,1,0],
 [2,0,2,0,2,0,2],
 [0,1,0,1,0,1,0],
 [2,0,2,0,2,0,2],
 [0,0,0,0,0,0,0],
],
[
 [0,0,0,2,0,0,0],
 [0,0,1,1,1,0,0],
 [0,1,1,1,1,1,0],
 [1,1,1,1,1,1,1],
 [0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0],
],
[
 [0,0,3,1,3,0,0],
 [0,3,1,2,1,3,0],
 [3,1,2,2,2,1,3],
 [0,3,1,2,1,3,0],
 [0,0,3,1,3,0,0],
 [0,0,0,0,0,0,0],
],
[
 [2,2,2,2,2,2,2],
 [1,3,1,1,1,3,1],
 [2,1,2,1,2,1,2],
 [1,3,1,1,1,3,1],
 [2,2,2,2,2,2,2],
 [0,0,0,0,0,0,0],
],
];

let score = 0, lives = 3, stageNum = 1, combo = 1;
let running = true, isPaused = false, awaitingNext = false;
let bricks = [];
let balls = [];
let particles = [];
let powerups = [];
let lasers = [];
let paddleX, paddleWidth;
let movingLeft = false, movingRight = false;
let laserActive = false, laserCooldown = 0;
let shakeFrames = 0;
let effectTimers = {};
let dragging = false;

function stagePattern(n) { return STAGES[(n - 1) % STAGES.length]; }
function stageSpeed(n) { return 2.6 + (n - 1) * 0.4; }

function initBricks() {
  bricks = [];
  const pattern = stagePattern(stageNum);
  for (let r = 0; r < pattern.length; r++) {
    for (let c = 0; c < pattern[r].length; c++) {
      const type = pattern[r][c];
      if (type === 0) continue;
      const bx = c * (brickWidth + brickPadding) + brickOffsetLeft;
      const by = r * (brickHeight + brickPadding) + brickOffsetTop;
      bricks.push({ x: bx, y: by, row: r, type: type, hp: type === 2 ? 2 : 1, active: true });
    }
  }
}

function makeBall(speedMul) {
  const speed = stageSpeed(stageNum) * (speedMul || 1);
  const angle = (Math.random() * 0.6 - 0.3);
  return {
    x: canvas.width / 2,
    y: canvas.height - 40,
    dx: speed * Math.sin(angle) * (Math.random() > 0.5 ? 1 : -1),
    dy: -speed * Math.cos(angle)
  };
}

function resetBallsAndPaddle() {
  paddleWidth = basePaddleWidth;
  paddleX = (canvas.width - paddleWidth) / 2;
  balls = [makeBall(1)];
  combo = 1;
  updateUI();
}

function clearEffects() {
  Object.values(effectTimers).forEach(t => clearTimeout(t));
  effectTimers = {};
  laserActive = false;
}

function resetGame() {
  score = 0; lives = 3; stageNum = 1; combo = 1;
  running = true; isPaused = false; awaitingNext = false;
  particles = []; powerups = []; lasers = [];
  clearEffects();
  overlay.style.display = "none";
  initBricks();
  resetBallsAndPaddle();
  updateUI();
  requestAnimationFrame(draw);
}

function togglePause() {
  if (!running || awaitingNext) return;
  isPaused = !isPaused;
}

function updateUI() {
  document.getElementById("score").innerText = score;
  document.getElementById("lives").innerText = lives;
  document.getElementById("stage").innerText = stageNum;
  document.getElementById("combo").innerText = combo;
}

// ---------- touch / drag controls on canvas ----------
function getCanvasX(clientX) {
  const rect = canvas.getBoundingClientRect();
  const scale = canvas.width / rect.width;
  return (clientX - rect.left) * scale;
}

function moveTo(clientX) {
  const cx = getCanvasX(clientX);
  paddleX = Math.min(Math.max(cx - paddleWidth / 2, 0), canvas.width - paddleWidth);
}

canvas.addEventListener("touchstart", e => {
  dragging = true;
  moveTo(e.touches[0].clientX);
  e.preventDefault();
}, { passive: false });

canvas.addEventListener("touchmove", e => {
  if (dragging) moveTo(e.touches[0].clientX);
  e.preventDefault();
}, { passive: false });

canvas.addEventListener("touchend", e => { dragging = false; }, { passive: false });

canvas.addEventListener("mousedown", e => { dragging = true; moveTo(e.clientX); });
canvas.addEventListener("mousemove", e => { if (dragging) moveTo(e.clientX); });
window.addEventListener("mouseup", () => { dragging = false; });

// ---------- on-screen buttons ----------
function bindHold(el, onDown, onUp) {
  el.addEventListener("touchstart", e => { onDown(); e.preventDefault(); }, { passive: false });
  el.addEventListener("touchend", e => { onUp(); e.preventDefault(); }, { passive: false });
  el.addEventListener("touchcancel", () => onUp());
  el.addEventListener("mousedown", onDown);
  el.addEventListener("mouseup", onUp);
  el.addEventListener("mouseleave", onUp);
}
bindHold(document.getElementById("leftBtn"), () => movingLeft = true, () => movingLeft = false);
bindHold(document.getElementById("rightBtn"), () => movingRight = true, () => movingRight = false);

document.getElementById("laserBtn").addEventListener("touchstart", e => { fireLaser(); e.preventDefault(); }, { passive: false });
document.getElementById("laserBtn").addEventListener("click", fireLaser);
document.getElementById("pauseBtn").addEventListener("click", togglePause);
document.getElementById("resetBtn").addEventListener("click", resetGame);

// ---------- keyboard (for desktop browsers too) ----------
document.addEventListener("keydown", e => {
  if (e.key === "ArrowRight") movingRight = true;
  else if (e.key === "ArrowLeft") movingLeft = true;
  else if (e.key === " ") { e.preventDefault(); fireLaser(); }
  else if (e.key === "p" || e.key === "P") togglePause();
});
document.addEventListener("keyup", e => {
  if (e.key === "ArrowRight") movingRight = false;
  else if (e.key === "ArrowLeft") movingLeft = false;
});

function fireLaser() {
  if (!laserActive || !running || isPaused) return;
  if (Date.now() < laserCooldown) return;
  laserCooldown = Date.now() + 350;
  const py = canvas.height - paddleHeight - 8;
  lasers.push({ x: paddleX + 6, y: py });
  lasers.push({ x: paddleX + paddleWidth - 6, y: py });
}

function applyPowerup(type) {
  if (type === "expand") {
    paddleWidth = basePaddleWidth * 1.6;
    clearTimeout(effectTimers.expand);
    effectTimers.expand = setTimeout(() => { paddleWidth = basePaddleWidth; }, 8000);
  } else if (type === "shrink") {
    paddleWidth = basePaddleWidth * 0.6;
    clearTimeout(effectTimers.shrink);
    effectTimers.shrink = setTimeout(() => { paddleWidth = basePaddleWidth; }, 6000);
  } else if (type === "multi") {
    const src = balls.slice(0, 2);
    src.forEach(b => {
      if (balls.length >= 6) return;
      balls.push({ x: b.x, y: b.y, dx: -b.dx + (Math.random()-0.5), dy: b.dy });
      balls.push({ x: b.x, y: b.y, dx: b.dx + (Math.random()-0.5)*2, dy: b.dy });
    });
  } else if (type === "life") {
    lives = Math.min(lives + 1, 5);
  } else if (type === "slow") {
    balls.forEach(b => { b.dx *= 0.55; b.dy *= 0.55; });
    clearTimeout(effectTimers.slow);
    effectTimers.slow = setTimeout(() => {
      balls.forEach(b => { b.dx /= 0.55; b.dy /= 0.55; });
    }, 6000);
  } else if (type === "laser") {
    laserActive = true;
    clearTimeout(effectTimers.laser);
    effectTimers.laser = setTimeout(() => { laserActive = false; }, 10000);
  }
  updateUI();
}

const POWERUP_STYLE = {
  expand: { color: "#4f8cff", label: "E" },
  shrink: { color: "#ff6b6b", label: "S" },
  multi:  { color: "#feca57", label: "M" },
  life:   { color: "#ff85c0", label: "+" },
  slow:   { color: "#1dd1a1", label: "W" },
  laser:  { color: "#a29bfe", label: "L" },
};

function maybeDropPowerup(x, y) {
  if (Math.random() > 0.24) return;
  const types = ["expand", "shrink", "multi", "life", "slow", "laser"];
  const type = types[Math.floor(Math.random() * types.length)];
  powerups.push({ x, y, type, vy: 2 });
}

function spawnParticles(x, y, color) {
  for (let i = 0; i < 7; i++) {
    particles.push({ x, y, vx: (Math.random()-0.5)*3.5, vy: (Math.random()-0.5)*3.5 - 1, alpha: 1, color });
  }
}
function updateParticles() {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.x += p.vx; p.y += p.vy; p.vy += 0.08; p.alpha -= 0.04;
    if (p.alpha <= 0) particles.splice(i, 1);
  }
}
function drawParticles() {
  particles.forEach(p => {
    ctx.globalAlpha = Math.max(p.alpha, 0);
    ctx.fillStyle = p.color;
    ctx.fillRect(p.x - 2, p.y - 2, 4, 4);
  });
  ctx.globalAlpha = 1;
}

function checkStageClear() { return bricks.every(b => b.type === 3 || !b.active); }

function brickHit(b) {
  if (b.type === 3) return;
  b.hp -= 1;
  if (b.hp <= 0) {
    b.active = false;
    score += 10 * combo;
    combo += 1;
    spawnParticles(b.x + brickWidth/2, b.y + brickHeight/2, colorsByRow[b.row % colorsByRow.length]);
    maybeDropPowerup(b.x + brickWidth/2, b.y + brickHeight/2);
  } else {
    score += 5;
  }
  updateUI();
}

function drawBricks() {
  bricks.forEach(b => {
    if (!b.active) return;
    ctx.beginPath();
    ctx.roundRect(b.x, b.y, brickWidth, brickHeight, 4);
    if (b.type === 3) ctx.fillStyle = "#555a6b";
    else if (b.type === 2) ctx.fillStyle = b.hp === 2 ? "#ff9f43" : "#ffd28a";
    else ctx.fillStyle = colorsByRow[b.row % colorsByRow.length];
    ctx.fill();
    ctx.closePath();
  });
}

function drawBalls() {
  balls.forEach(ball => {
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ballRadius, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.closePath();
  });
}

function drawPaddle() {
  ctx.beginPath();
  ctx.roundRect(paddleX, canvas.height - paddleHeight - 8, paddleWidth, paddleHeight, 6);
  ctx.fillStyle = laserActive ? "#a29bfe" : "#4f8cff";
  ctx.fill();
  ctx.closePath();
}

function drawPowerups() {
  powerups.forEach(p => {
    const s = POWERUP_STYLE[p.type];
    ctx.beginPath();
    ctx.roundRect(p.x - 10, p.y - 10, 20, 20, 5);
    ctx.fillStyle = s.color;
    ctx.fill();
    ctx.closePath();
    ctx.fillStyle = "#fff";
    ctx.font = "bold 12px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(s.label, p.x, p.y + 1);
  });
}

function drawLasers() {
  ctx.fillStyle = "#a29bfe";
  lasers.forEach(l => ctx.fillRect(l.x - 2, l.y - 10, 4, 10));
}

function showOverlay(text) {
  overlay.innerText = text;
  overlay.style.display = "block";
  overlay.style.left = (canvas.offsetLeft + canvas.offsetWidth / 2 - overlay.offsetWidth / 2) + "px";
  overlay.style.top = (canvas.offsetTop + canvas.offsetHeight / 2 - overlay.offsetHeight / 2) + "px";
}
function hideOverlay() { overlay.style.display = "none"; }

function goNextStage() {
  awaitingNext = true;
  const cleared = stageNum;
  showOverlay("🎉 스테이지 " + cleared + " 클리어!\\n다음 스테이지 준비 중...");
  setTimeout(() => {
    stageNum += 1;
    initBricks();
    resetBallsAndPaddle();
    hideOverlay();
    awaitingNext = false;
  }, 1500);
}

function updateBalls() {
  for (let i = balls.length - 1; i >= 0; i--) {
    const ball = balls[i];
    ball.x += ball.dx;
    ball.y += ball.dy;

    if (ball.x + ball.dx > canvas.width - ballRadius || ball.x - ballRadius < 0) ball.dx = -ball.dx;
    if (ball.y - ballRadius < 0) ball.dy = -ball.dy;

    for (let j = 0; j < bricks.length; j++) {
      const b = bricks[j];
      if (!b.active) continue;
      if (ball.x > b.x && ball.x < b.x + brickWidth && ball.y > b.y && ball.y < b.y + brickHeight) {
        ball.dy = -ball.dy;
        brickHit(b);
        break;
      }
    }

    const paddleY = canvas.height - paddleHeight - 8;
    if (ball.y + ballRadius >= paddleY && ball.y - ballRadius <= paddleY + paddleHeight &&
        ball.x > paddleX && ball.x < paddleX + paddleWidth && ball.dy > 0) {
      const hitPos = (ball.x - paddleX) / paddleWidth;
      const angle = (hitPos - 0.5) * Math.PI * 0.7;
      const speed = Math.max(Math.sqrt(ball.dx*ball.dx + ball.dy*ball.dy), stageSpeed(stageNum)*0.8);
      ball.dx = speed * Math.sin(angle);
      ball.dy = -Math.abs(speed * Math.cos(angle));
      combo = 1;
      updateUI();
    } else if (ball.y - ballRadius > canvas.height) {
      balls.splice(i, 1);
    }
  }

  if (balls.length === 0) {
    lives -= 1;
    shakeFrames = 10;
    updateUI();
    if (lives <= 0) {
      running = false;
      showOverlay("💥 게임 오버!\\n최종 점수: " + score + "\\n'처음부터' 버튼을 눌러 재도전하세요");
    } else {
      resetBallsAndPaddle();
    }
  }
}

function updatePowerups() {
  for (let i = powerups.length - 1; i >= 0; i--) {
    const p = powerups[i];
    p.y += p.vy;
    const paddleY = canvas.height - paddleHeight - 8;
    if (p.y + 10 >= paddleY && p.x > paddleX && p.x < paddleX + paddleWidth) {
      applyPowerup(p.type);
      powerups.splice(i, 1);
    } else if (p.y > canvas.height) {
      powerups.splice(i, 1);
    }
  }
}

function updateLasers() {
  for (let i = lasers.length - 1; i >= 0; i--) {
    const l = lasers[i];
    l.y -= 6.5;
    let hit = false;
    for (let j = 0; j < bricks.length; j++) {
      const b = bricks[j];
      if (!b.active || b.type === 3) continue;
      if (l.x > b.x && l.x < b.x + brickWidth && l.y > b.y && l.y < b.y + brickHeight) {
        brickHit(b);
        hit = true;
        break;
      }
    }
    if (hit || l.y < 0) lasers.splice(i, 1);
  }
}

function updatePaddleMovement() {
  const speed = 5.5;
  if (movingRight) paddleX = Math.min(paddleX + speed, canvas.width - paddleWidth);
  else if (movingLeft) paddleX = Math.max(paddleX - speed, 0);
}

function draw() {
  if (!running) return;

  if (isPaused) {
    showOverlay("⏸ 일시정지\\n버튼을 눌러 재개하세요");
    requestAnimationFrame(draw);
    return;
  }
  if (awaitingNext) {
    requestAnimationFrame(draw);
    return;
  }
  hideOverlay();

  ctx.save();
  if (shakeFrames > 0) {
    ctx.translate((Math.random()-0.5)*5, (Math.random()-0.5)*5);
    shakeFrames -= 1;
  }

  ctx.clearRect(-10, -10, canvas.width + 20, canvas.height + 20);
  drawBricks();
  drawPowerups();
  drawLasers();
  drawParticles();
  drawBalls();
  drawPaddle();
  ctx.restore();

  updatePaddleMovement();
  updateBalls();
  updatePowerups();
  updateLasers();
  updateParticles();

  if (running && !awaitingNext && checkStageClear()) {
    goNextStage();
  }

  requestAnimationFrame(draw);
}

initBricks();
resetBallsAndPaddle();
updateUI();
requestAnimationFrame(draw);
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=620, scrolling=False)

st.markdown("---")
st.markdown(
    "**모바일 조작 방법**\n"
    "- 화면(캔버스)을 손가락으로 좌우로 드래그하면 패들이 따라 움직입니다\n"
    "- 화면 아래 **◀ / ▶** 버튼을 눌러도 이동할 수 있어요\n"
    "- **⚡레이저** 버튼: 레이저 파워업을 먹은 상태에서 누르면 발사\n"
    "- **⏸ 일시정지 / 🔄 처음부터** 버튼으로 게임 제어\n"
    "- PC 브라우저에서도 방향키·스페이스바·마우스로 동일하게 플레이 가능합니다"
)
