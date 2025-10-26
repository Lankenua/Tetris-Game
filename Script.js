// === LANKEN TETRIS === //
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scoreDisplay = document.getElementById("score");

// --- Game constants ---
const BLOCK_SIZE = 30;
const ROWS = 20;
const COLS = 10;
const COLORS = [
  "#00FFFF", // I
  "#FF6464", // Z
  "#64FF64", // S
  "#FFFF64", // O
  "#FFA500", // J
  "#6464FF", // T
  "#A020F0", // Bonus
];

// --- Shapes definition ---
const SHAPES = [
  [[1, 1, 1, 1]], // I
  [
    [1, 1, 0],
    [0, 1, 1],
  ], // Z
  [
    [0, 1, 1],
    [1, 1, 0],
  ], // S
  [
    [1, 1],
    [1, 1],
  ], // O
  [
    [1, 0, 0],
    [1, 1, 1],
  ], // J
  [
    [0, 1, 0],
    [1, 1, 1],
  ], // T
];

// --- Utility functions ---
function createMatrix(rows, cols, fill = "#000") {
  return Array.from({ length: rows }, () => Array(cols).fill(fill));
}

function clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

// --- Tetromino class ---
class Tetromino {
  constructor(x, y, type) {
    this.x = x;
    this.y = y;
    this.type = type;
    this.shape = clone(SHAPES[type]);
    this.color = COLORS[type];
  }

  rotate() {
    // Transpose and reverse rows to rotate clockwise
    const rotated = this.shape[0].map((_, i) => this.shape.map(r => r[i])).reverse();
    this.shape = rotated;
  }

  getBlocks() {
    const blocks = [];
    for (let r = 0; r < this.shape.length; r++) {
      for (let c = 0; c < this.shape[r].length; c++) {
        if (this.shape[r][c]) {
          blocks.push({ x: this.x + c, y: this.y + r });
        }
      }
    }
    return blocks;
  }
}

// --- Game variables ---
let grid = createMatrix(ROWS, COLS);
let locked = {};
let current = randomPiece();
let next = randomPiece();
let fallTimer = 0;
let fallSpeed = 500; // milliseconds
let lastTime = 0;
let score = 0;
let gameOver = false;

// --- Functions ---
function randomPiece() {
  const type = Math.floor(Math.random() * SHAPES.length);
  return new Tetromino(3, 0, type);
}

function drawGrid() {
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      ctx.fillStyle = grid[r][c];
      ctx.fillRect(c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
      ctx.strokeStyle = "#111";
      ctx.strokeRect(c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
    }
  }
}

function merge(piece) {
  piece.getBlocks().forEach(b => {
    if (b.y >= 0) grid[b.y][b.x] = piece.color;
  });
}

function isValidMove(piece) {
  return piece.getBlocks().every(b => {
    return (
      b.x >= 0 &&
      b.x < COLS &&
      b.y < ROWS &&
      (b.y < 0 || grid[b.y][b.x] === "#000")
    );
  });
}

function clearFullRows() {
  let cleared = 0;
  grid = grid.filter(row => {
    if (row.every(cell => cell !== "#000")) {
      cleared++;
      return false;
    }
    return true;
  });
  while (grid.length < ROWS) grid.unshift(Array(COLS).fill("#000"));
  score += cleared * 10;
  scoreDisplay.textContent = "SCORE: " + score;
}

function handleInput(e) {
  if (gameOver) return;

  if (e.key === "ArrowLeft") {
    current.x--;
    if (!isValidMove(current)) current.x++;
  } else if (e.key === "ArrowRight") {
    current.x++;
    if (!isValidMove(current)) current.x--;
  } else if (e.key === "ArrowDown") {
    current.y++;
    if (!isValidMove(current)) current.y--;
  } else if (e.key === "ArrowUp") {
    const prevShape = clone(current.shape);
    current.rotate();
    if (!isValidMove(current)) current.shape = prevShape;
  }
}
document.addEventListener("keydown", handleInput);

function drawPiece(piece) {
  piece.getBlocks().forEach(b => {
    if (b.y >= 0) {
      ctx.fillStyle = piece.color;
      ctx.fillRect(b.x * BLOCK_SIZE, b.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
      ctx.strokeStyle = "#111";
      ctx.strokeRect(b.x * BLOCK_SIZE, b.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
    }
  });
}

function update(time = 0) {
  if (gameOver) {
    ctx.fillStyle = "rgba(0,0,0,0.7)";
    ctx.fillRect(0, canvas.height / 2 - 30, canvas.width, 60);
    ctx.fillStyle = "#FF0000";
    ctx.font = "24px Comic Sans MS";
    ctx.fillText("GAME OVER", canvas.width / 2 - 70, canvas.height / 2 + 10);
    return;
  }

  const deltaTime = time - lastTime;
  lastTime = time;
  fallTimer += deltaTime;

  if (fallTimer > fallSpeed) {
    current.y++;
    if (!isValidMove(current)) {
      current.y--;
      merge(current);
      clearFullRows();
      current = next;
      next = randomPiece();
      if (!isValidMove(current)) {
        gameOver = true;
      }
    }
    fallTimer = 0;
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawGrid();
  drawPiece(current);
  requestAnimationFrame(update);
}

// --- Start the game ---
update();
