const API_BASE = "/api/produtos";

const listaEl = document.getElementById("lista-produtos");
const estadoVazioEl = document.getElementById("estado-vazio");
const estadoCarregandoEl = document.getElementById("estado-carregando");
const formEl = document.getElementById("form-cadastro");
const btnCadastrarEl = document.getElementById("btn-cadastrar");
const mensagemErroEl = document.getElementById("mensagem-erro");
const templateLinha = document.getElementById("template-linha-produto");

function formatarPreco(valor) {
  return Number(valor).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatarData(iso) {
  return new Date(iso).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

function mostrarErro(msg) {
  mensagemErroEl.textContent = msg;
  mensagemErroEl.hidden = false;
}

function limparErro() {
  mensagemErroEl.hidden = true;
  mensagemErroEl.textContent = "";
}

async function carregarProdutos() {
  estadoCarregandoEl.hidden = false;
  estadoVazioEl.hidden = true;
  listaEl.innerHTML = "";

  try {
    const resp = await fetch(API_BASE);
    if (!resp.ok) throw new Error("Falha ao carregar produtos");
    const produtos = await resp.json();

    estadoCarregandoEl.hidden = true;

    if (produtos.length === 0) {
      estadoVazioEl.hidden = false;
      return;
    }

    for (const produto of produtos) {
      const linha = criarLinhaProduto(produto);
      listaEl.appendChild(linha);
      carregarHistorico(produto.id, linha);
    }
  } catch (e) {
    estadoCarregandoEl.hidden = true;
    mostrarErro("Não foi possível carregar os produtos. Verifique se a API está no ar.");
  }
}

function criarLinhaProduto(produto) {
  const clone = templateLinha.content.cloneNode(true);
  const artigo = clone.querySelector(".linha-produto");
  artigo.dataset.id = produto.id;

  const nomeEl = clone.querySelector(".linha-nome");
  nomeEl.textContent = produto.nome;
  nomeEl.href = produto.url;

  const badgeEl = clone.querySelector(".badge");
  const abaixoDoAlvo = produto.preco_atual !== null && Number(produto.preco_atual) <= Number(produto.preco_alvo);
  badgeEl.textContent = abaixoDoAlvo ? "abaixo do alvo" : "aguardando queda";
  badgeEl.classList.add(abaixoDoAlvo ? "abaixo-alvo" : "aguardando");

  clone.querySelector(".linha-alvo").textContent = `alvo: R$ ${formatarPreco(produto.preco_alvo)}`;

  clone.querySelector(".valor-preco").textContent =
    produto.preco_atual !== null ? formatarPreco(produto.preco_atual) : "—";

  const btnPausar = clone.querySelector(".acao-pausar");
  btnPausar.textContent = produto.ativo ? "Pausar" : "Retomar";
  btnPausar.addEventListener("click", () => alternarAtivo(produto.id, !produto.ativo));

  clone.querySelector(".acao-verificar").addEventListener("click", (e) => verificarAgora(produto.id, e.target));
  clone.querySelector(".acao-remover").addEventListener("click", () => removerProduto(produto.id, produto.nome));

  return clone;
}

async function carregarHistorico(produtoId, linhaFragment) {
  try {
    const resp = await fetch(`${API_BASE}/${produtoId}/historico`);
    if (!resp.ok) return;
    const pontos = await resp.json();

    const artigo = listaEl.querySelector(`.linha-produto[data-id="${produtoId}"]`);
    if (!artigo || pontos.length < 2) return;

    const svg = artigo.querySelector(".sparkline");
    desenharSparkline(svg, pontos);
  } catch (e) {
    // Sparkline é um extra visual; falha silenciosa não deve travar a UI
  }
}

function desenharSparkline(svg, pontos) {
  const precos = pontos.map(p => Number(p.preco));
  const min = Math.min(...precos);
  const max = Math.max(...precos);
  const largura = 300;
  const altura = 60;
  const margem = 4;

  const coords = precos.map((preco, i) => {
    const x = (i / (precos.length - 1)) * largura;
    const y = max === min
      ? altura / 2
      : altura - margem - ((preco - min) / (max - min)) * (altura - margem * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");

  const linha = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
  linha.setAttribute("points", coords);
  svg.appendChild(linha);
}

async function alternarAtivo(produtoId, novoAtivo) {
  try {
    const resp = await fetch(`${API_BASE}/${produtoId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ativo: novoAtivo })
    });
    if (!resp.ok) throw new Error();
    carregarProdutos();
  } catch (e) {
    mostrarErro("Não foi possível atualizar o produto.");
  }
}

async function verificarAgora(produtoId, botao) {
  const textoOriginal = botao.textContent;
  botao.disabled = true;
  botao.textContent = "Verificando…";

  try {
    const resp = await fetch(`${API_BASE}/${produtoId}/verificar`, { method: "POST" });
    if (!resp.ok) {
      const erro = await resp.json().catch(() => ({}));
      throw new Error(erro.detail || "Falha ao verificar preço");
    }
    await carregarProdutos();
  } catch (e) {
    mostrarErro(e.message);
    botao.disabled = false;
    botao.textContent = textoOriginal;
  }
}

async function removerProduto(produtoId, nome) {
  if (!confirm(`Parar de monitorar "${nome}"? Isso apaga o histórico de preços dele.`)) return;

  try {
    const resp = await fetch(`${API_BASE}/${produtoId}`, { method: "DELETE" });
    if (!resp.ok) throw new Error();
    carregarProdutos();
  } catch (e) {
    mostrarErro("Não foi possível remover o produto.");
  }
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  limparErro();

  const url = document.getElementById("input-url").value.trim();
  const precoAlvo = document.getElementById("input-preco-alvo").value;

  btnCadastrarEl.disabled = true;
  btnCadastrarEl.textContent = "Buscando produto…";

  try {
    const resp = await fetch(API_BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, preco_alvo: precoAlvo })
    });

    if (!resp.ok) {
      const erro = await resp.json().catch(() => ({}));
      throw new Error(erro.detail || "Não foi possível cadastrar o produto.");
    }

    formEl.reset();
    await carregarProdutos();
  } catch (e) {
    mostrarErro(e.message);
  } finally {
    btnCadastrarEl.disabled = false;
    btnCadastrarEl.textContent = "Monitorar";
  }
});

carregarProdutos();