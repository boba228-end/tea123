<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Пересказ параграфа — 7 класс</title>
<style>
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    background: #f4f2ec;
    margin: 0;
    padding: 24px 16px 60px;
    color: #26221c;
  }
  .wrap { max-width: 720px; margin: 0 auto; }
  h1 { font-size: 22px; font-weight: 600; margin-bottom: 4px; }
  .sub { color: #6b675e; font-size: 14px; margin-bottom: 20px; }
  textarea {
    width: 100%;
    min-height: 160px;
    padding: 12px 14px;
    border: 1px solid #d8d3c6;
    border-radius: 10px;
    font-size: 15px;
    line-height: 1.5;
    resize: vertical;
    font-family: inherit;
  }
  .styles {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 16px 0;
  }
  .style-btn {
    padding: 8px 14px;
    border-radius: 999px;
    border: 1px solid #d8d3c6;
    background: #fff;
    cursor: pointer;
    font-size: 14px;
    transition: 0.15s;
  }
  .style-btn:hover { border-color: #b5ab8f; }
  .style-btn.active {
    background: #26221c;
    color: #fff;
    border-color: #26221c;
  }
  .go {
    margin-top: 8px;
    width: 100%;
    padding: 12px;
    border-radius: 10px;
    border: none;
    background: #c65d2e;
    color: #fff;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
  }
  .go:disabled { opacity: 0.5; cursor: default; }
  .go:hover:not(:disabled) { background: #b04e23; }
  .result {
    margin-top: 24px;
    padding: 18px 20px;
    background: #fff;
    border-radius: 12px;
    border: 1px solid #e5e0d2;
    font-size: 16px;
    line-height: 1.7;
    white-space: pre-wrap;
    display: none;
  }
  .loading {
    margin-top: 20px;
    color: #6b675e;
    font-size: 14px;
    display: none;
  }
  .error {
    margin-top: 16px;
    color: #a02020;
    font-size: 14px;
    display: none;
  }
</style>
</head>
<body>
<div class="wrap">
  <h1>Пересказ параграфа</h1>
  <div class="sub">Вставьте текст параграфа из учебника (7 класс) и выберите, как его пересказать.</div>

  <textarea id="input" placeholder="Вставьте здесь текст параграфа из учебника..."></textarea>

  <div class="styles" id="styles">
    <button class="style-btn active" data-style="просто">Простыми словами</button>
    <button class="style-btn" data-style="сказка">Как сказка</button>
    <button class="style-btn" data-style="диалог">Диалог двух героев</button>
    <button class="style-btn" data-style="конспект">Краткий конспект (тезисы)</button>
    <button class="style-btn" data-style="стихи">В стихах</button>
    <button class="style-btn" data-style="блогер">Как рассказал бы блогер-подросток</button>
    <button class="style-btn" data-style="детектив">Как детективная история</button>
    <button class="style-btn" data-style="примеры">С примерами из жизни</button>
  </div>

  <button class="go" id="goBtn">Пересказать</button>

  <div class="loading" id="loading">Пересказываю...</div>
  <div class="error" id="error"></div>
  <div class="result" id="result"></div>
</div>

<script>
let selectedStyle = "просто";

document.getElementById("styles").addEventListener("click", (e) => {
  const btn = e.target.closest(".style-btn");
  if (!btn) return;
  document.querySelectorAll(".style-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  selectedStyle = btn.dataset.style;
});

const styleInstructions = {
  "просто": "перескажи очень простыми словами, как для человека, который вообще не понимает тему, используя короткие предложения и понятные аналогии",
  "сказка": "перескажи в виде сказки со сказочными персонажами, зачином и присказками, но сохрани все факты из параграфа",
  "диалог": "перескажи в виде диалога двух школьников-семиклассников, где один объясняет тему другому, задавая наводящие вопросы",
  "конспект": "оформи как краткий конспект: заголовки, нумерованные тезисы, самые важные факты и определения",
  "стихи": "перескажи содержание в стихотворной форме (можно с юмором), сохранив все ключевые факты",
  "блогер": "перескажи в стиле энергичного видеоблогера-подростка, с восклицаниями и современным сленгом, но без искажения фактов",
  "детектив": "оформи как детективную историю, где факты из параграфа — это 'улики', которые распутывает сыщик",
  "примеры": "объясни тему, добавив к каждому важному факту понятный пример из повседневной жизни семиклассника"
};

document.getElementById("goBtn").addEventListener("click", async () => {
  const input = document.getElementById("input").value.trim();
  const resultEl = document.getElementById("result");
  const loadingEl = document.getElementById("loading");
  const errorEl = document.getElementById("error");
  const goBtn = document.getElementById("goBtn");

  errorEl.style.display = "none";
  resultEl.style.display = "none";

  if (!input) {
    errorEl.textContent = "Вставьте текст параграфа перед тем, как продолжить.";
    errorEl.style.display = "block";
    return;
  }

  loadingEl.style.display = "block";
  goBtn.disabled = true;

  try {
    const prompt = `Вот параграф из школьного учебника (7 класс):\n\n"""${input}"""\n\nЗадача: ${styleInstructions[selectedStyle]}. Не добавляй фактов, которых нет в тексте. Отвечай только пересказом, без вступления вроде "Вот пересказ".`;

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "claude-sonnet-4-6",
        max_tokens: 1000,
        messages: [{ role: "user", content: prompt }]
      })
    });

    if (!response.ok) throw new Error("Ошибка запроса к API");

    const data = await response.json();
    const text = data.content.map(b => b.text || "").join("\n").trim();

    resultEl.textContent = text;
    resultEl.style.display = "block";
  } catch (err) {
    errorEl.textContent = "Не получилось получить пересказ. Попробуйте ещё раз.";
    errorEl.style.display = "block";
  } finally {
    loadingEl.style.display = "none";
    goBtn.disabled = false;
  }
});
</script>
</body>
</html>