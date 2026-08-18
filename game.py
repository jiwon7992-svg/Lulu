import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="벽돌깨기 게임", page_icon="🧱", layout="centered")

st.title("🧱 벽돌깨기 게임")
st.caption("← → 방향키 또는 마우스로 패들을 움직여 공을 튕겨내고 벽돌을 모두 깨보세요!")

GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  html, body {
    margin: 0;
    padding: 0;
    background: #0f1117;
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: 'Segoe UI', sans-serif;
  }
  #ui {
    color: #fff;
    display: flex;
    justify-content: space-between;
    width: 480px;
    padding: 8px 4px;
    font-size: 16px;
    box-sizing: border-box;
  }
  #gameCanvas {
    background: #1a1c25;
    border: 2px solid #3a3d4d;
    border-radius: 8px;
    display: block;
  }
  #overlay {
    position: absolute;
    color: #fff;
    text-align: center;
    font-size: 22px;
    background: rgba(0,0,0,0.6);
    padding: 20px 30px;
    border-radius: 10px;
    display: none;
  }
  #wrap {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  button {
    margin-top: 10px;
    padding: 8px 20px;
    font-size: 15px;
    border: none;
    border-radius: 6px;
    background: #4f8cff;
    color: white;
    cursor: pointer;
  }
  button:hover { background: #3a75e0; }
</style>
</head>
<body>
<div id="wrap">
  <div id="ui">
    <span>점수: <span id="score">0</span></span>
    <span>레벨: <span id="level">1</span></span>
    <span>목숨: <span id="lives">3</span></span>
  </div>
  <canvas id="gameCanvas" width="480" height="420"></canvas>
  <div id="overlay"></div>
  <button id="restartBtn" onclick="resetGame()">🔄 다시 시작</button>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const overlay = document.getElementById("overlay");

let ballRadius = 8;
let x, y, dx, dy;
let paddleHeight = 12;
let paddleWidth = 90;
let paddleX;
let rightPressed = false;
let leftPressed = false;

let brickRowCount = 5;
let brickColumnCount = 7;
let brickWidth = 55;
let brickHeight = 18;
let brickPadding = 8;
let brickOffsetTop = 40;
let brickOffsetLeft = 20;

let score = 0;
let lives = 3;
let level = 1;
let running = true;
let bricks = [];

const colors = ["#ff6b6b", "#feca57", "#1dd1a1", "#54a0ff", "#a29bfe"];

function initBricks() {
  bricks = [];
  for (let c = 0; c < brickColumnCount; c++) {
    bricks[c] = [];
    for (let r = 0; r < brickRowCount; r++) {
      bricks[c][r] = { x: 0, y: 0, status: 1 };
    }
  }
}

function resetBallAndPaddle() {
  x = canvas.width / 2;
  y = canvas.height - 40;
  const speed = 3 + (level - 1) * 0.6;
  dx = speed * (Math.random() > 0.5 ? 1 : -1);
  dy = -speed;
  paddleX = (canvas.width - paddleWidth) / 2;
}

function resetGame() {
  score = 0;
  lives = 3;
  level = 1;
  running = true;
  overlay.style.display = "none";
  initBricks();
  resetBallAndPaddle();
  updateUI();
  requestAnimationFrame(draw);
}

function updateUI() {
  document.getElementById("score").innerText = score;
  document.getElementById("lives").innerText = lives;
  document.getElementById("level").innerText = level;
}

document.addEventListener("keydown", keyDownHandler);
document.addEventListener("keyup", keyUpHandler);
canvas.addEventListener("mousemove", mouseMoveHandler);

function keyDownHandler(e) {
  if (e.key === "Right" || e.key === "ArrowRight") rightPressed = true;
  else if (e.key === "Left" || e.key === "ArrowLeft") leftPressed = true;
}
function keyUpHandler(e) {
  if (e.key === "Right" || e.key === "ArrowRight") rightPressed = false;
  else if (e.key === "Left" || e.key === "ArrowLeft") leftPressed = false;
}
function mouseMoveHandler(e) {
  const rect = canvas.getBoundingClientRect();
  const relativeX = e.clientX - rect.left;
  if (relativeX > 0 && relativeX < canvas.width) {
    paddleX = relativeX - paddleWidth / 2;
    if (paddleX < 0) paddleX = 0;
    if (paddleX + paddleWidth > canvas.width) paddleX = canvas.width - paddleWidth;
  }
}

function collisionDetection() {
  for (let c = 0; c < brickColumnCount; c++) {
    for (let r = 0; r < brickRowCount; r++) {
      const b = bricks[c][r];
      if (b.status === 1) {
        if (x > b.x && x < b.x + brickWidth && y > b.y && y < b.y + brickHeight) {
          dy = -dy;
          b.status = 0;
          score += 10;
          updateUI();
          if (checkWin()) {
            level += 1;
            initBricks();
            resetBallAndPaddle();
            updateUI();
          }
        }
      }
    }
  }
}

function checkWin() {
  for (let c = 0; c < brickColumnCount; c++)
    for (let r = 0; r < brickRowCount; r++)
      if (bricks[c][r].status === 1) return false;
  return true;
}

function drawBall() {
  ctx.beginPath();
  ctx.arc(x, y, ballRadius, 0, Math.PI * 2);
  ctx.fillStyle = "#ffffff";
  ctx.fill();
  ctx.closePath();
}

function drawPaddle() {
  ctx.beginPath();
  ctx.roundRect(paddleX, canvas.height - paddleHeight - 8, paddleWidth, paddleHeight, 6);
  ctx.fillStyle = "#4f8cff";
  ctx.fill();
  ctx.closePath();
}

function drawBricks() {
  for (let c = 0; c < brickColumnCount; c++) {
    for (let r = 0; r < brickRowCount; r++) {
      if (bricks[c][r].status === 1) {
        const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
        const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
        bricks[c][r].x = brickX;
        bricks[c][r].y = brickY;
        ctx.beginPath();
        ctx.roundRect(brickX, brickY, brickWidth, brickHeight, 4);
        ctx.fillStyle = colors[r % colors.length];
        ctx.fill();
        ctx.closePath();
      }
    }
  }
}

function showOverlay(text) {
  overlay.innerText = text;
  overlay.style.display = "block";
  overlay.style.left = (canvas.offsetLeft + canvas.width / 2 - overlay.offsetWidth / 2) + "px";
  overlay.style.top = (canvas.offsetTop + canvas.height / 2 - 30) + "px";
}

function draw() {
  if (!running) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawBricks();
  drawBall();
  drawPaddle();
  collisionDetection();

  if (x + dx > canvas.width - ballRadius || x + dx < ballRadius) dx = -dx;
  if (y + dy < ballRadius) dy = -dy;
  else if (y + dy > canvas.height - ballRadius - paddleHeight - 8) {
    if (x > paddleX && x < paddleX + paddleWidth) {
      const hitPos = (x - paddleX) / paddleWidth;
      const angle = (hitPos - 0.5) * Math.PI * 0.7;
      const speed = Math.sqrt(dx * dx + dy * dy);
      dx = speed * Math.sin(angle);
      dy = -Math.abs(speed * Math.cos(angle));
    } else if (y + dy > canvas.height - ballRadius) {
      lives -= 1;
      updateUI();
      if (lives <= 0) {
        running = false;
        showOverlay("💥 게임 오버! 점수: " + score);
        return;
      } else {
        resetBallAndPaddle();
      }
    }
  }

  if (rightPressed) {
    paddleX += 6;
    if (paddleX + paddleWidth > canvas.width) paddleX = canvas.width - paddleWidth;
  } else if (leftPressed) {
    paddleX -= 6;
    if (paddleX < 0) paddleX = 0;
  }

  x += dx;
  y += dy;

  requestAnimationFrame(draw);
}

initBricks();
resetBallAndPaddle();
updateUI();
requestAnimationFrame(draw);
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=560, scrolling=False)

st.markdown("---")
st.markdown(
    "**조작 방법**\n"
    "- ⬅️➡️ 방향키 또는 마우스 이동으로 패들 조작\n"
    "- 공이 패들 어느 지점에 맞느냐에 따라 반사 각도가 달라집니다\n"
    "- 벽돌을 모두 깨면 다음 레벨(공 속도 증가)로 진행합니다\n"
    "- 목숨 3개를 모두 잃으면 게임 오버, '다시 시작' 버튼으로 재도전하세요"
)
