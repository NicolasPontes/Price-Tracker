const API_PRODUTOS = "/api/produtos";
const API_AUTH = "/api/auth";
const CHAVE_TOKEN = "notificador_token";

// ===== Elementos =====

const viewAuth = document.getElementById("view-auth");
const viewApp = document.getElementById("view-app");

const abas = document.querySelectorAll(".aba");
const formLogin = document.getElementById("form-login");
const formRegistro = document.getElementById("form-registro");
const authErroEl = document.getElementById("auth-erro");

const btnLogout = document.getElementById("btn-logout");

const listaEl = document.getElementById("lista-produtos");
const estadoVazioEl = document.getElementById("estado-vazio");
const estadoCarregandoEl = document.getElementById("estado-carregando");
const formCadastro = document.getElementById("form-cadastro");
const btnCadastrarEl = document.getElementById("btn-cadastrar");
const mensagemErroEl = document.getElementById("mensagem-erro");
const templateLinha = document.getElementById("template-linha-produto");
const inputPrecoAlvo = document.getElementById("input-preco-alvo");

aplicarMascaraMoeda(inputPrecoAlvo);

// ===== Utilitários =====

function formatarPreco(valor) {
  return Number(valor).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Formata o campo como moeda brasileira enquanto o usuário digita
// (ex: digitar "12550" vira "125,50"). Funciona só com dígitos,
// então cada tecla numérica empurra os centavos.
function aplicarMascaraMoeda(input) {
  input.addEventListener("input", () => {
    let digitos = input.value.replace(/\D/g, "");

    if (!digitos) {
      input.value = "";
      return;
    }

    const valorEmCentavos = parseInt(digitos, 10);
    const valorFormatado = (valorEmCentavos / 100).toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });

    input.value = valorFormatado;
  });
}

// Converte "1.234,56" (formato mascarado) de volta para 1234.56 (número)
function valorMascaraParaNumero(valorMascarado) {
  if (!valorMascarado) return null;

  const limpo = valorMascarado.replace(/\./g, "").replace(",", ".");
  const numero = parseFloat(limpo);

  return isNaN(numero) ? null : numero;
}

function getToken() {
  return localStorage.getItem(CHAVE_TOKEN);
}

function setToken(token) {
  localStorage.setItem(CHAVE_TOKEN, token);
}

function limparToken() {
  localStorage.removeItem(CHAVE_TOKEN);
}

// Wrapper de fetch que injeta o token e trata 401 (token expirado/ inválido)
// globalmente, jogando o usuário de volta pra tela de login.
async function apiFetch(url, options = {}) {
  const headers = { ...(options.headers || {}), Authorization: `Bearer ${getToken()}` };
  const resp = await fetch(url, { ...options, headers });

  if (resp.status === 401) {
    limparToken();
    mostrarTelaAuth();
    throw new Error("Sessão expirada. Faça login novamente.");
  }

  return resp;
}

function mostrarErro(el, msg) {
  el.textContent = msg;
  el.hidden = false;
}

function limparErro(el) {
  el.hidden = true;
  el.textContent = "";
}

// ===== Alternância de telas =====

function mostrarTelaAuth() {
  viewAuth.hidden = false;
  viewApp.hidden = true;
}

function mostrarTelaApp() {
  viewAuth.hidden = true;
  viewApp.hidden = false;
  carregarProdutos();
}

// ===== Abas login / registro =====

abas.forEach(aba => {
  aba.addEventListener("click", () => {
    abas.forEach(a => a.classList.remove("aba-ativa"));
    aba.classList.add("aba-ativa");

    limparErro(authErroEl);

    if (aba.dataset.aba === "login") {
      formLogin.hidden = false;
      formRegistro.hidden = true;
    } else {
      formLogin.hidden = true;
      formRegistro.hidden = false;
    }
  });
});

// ===== Login =====

formLogin.addEventListener("submit", async (e) => {
  e.preventDefault();
  limparErro(authErroEl);

  const email = document.getElementById("login-email").value.trim();
  const senha = document.getElementById("login-senha").value;

  const btn = formLogin.querySelector("button");
  btn.disabled = true;
  btn.textContent = "Entrando…";

  try {
    const corpo = new URLSearchParams();
    corpo.set("username", email);
    corpo.set("password", senha);

    const resp = await fetch(`${API_AUTH}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: corpo
    });

    if (!resp.ok) {
      const erro = await resp.json().catch(() => ({}));
      throw new Error(erro.detail || "E-mail ou senha inválidos.");
    }

    const dados = await resp.json();
    setToken(dados.access_token);
    formLogin.reset();
    mostrarTelaApp();
  } catch (e) {
    mostrarErro(authErroEl, e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Entrar";
  }
});

// ===== Registro =====

formRegistro.addEventListener("submit", async (e) => {
  e.preventDefault();
  limparErro(authErroEl);

  const email = document.getElementById("registro-email").value.trim();
  const senha = document.getElementById("registro-senha").value;

  const btn = formRegistro.querySelector("button");
  btn.disabled = true;
  btn.textContent = "Criando conta…";

  try {
    const resp = await fetch(`${API_AUTH}/registrar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, senha })
    });

    if (!resp.ok) {
      const erro = await resp.json().catch(() => ({}));
      throw new Error(erro.detail || "Não foi possível criar a conta.");
    }

    // Conta criada -> loga automaticamente
    const corpo = new URLSearchParams();
    corpo.set("username", email);
    corpo.set("password", senha);

    const respLogin = await fetch(`${API_AUTH}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: corpo
    });

    const dadosLogin = await respLogin.json();
    setToken(dadosLogin.access_token);
    formRegistro.reset();
    mostrarTelaApp();
  } catch (e) {
    mostrarErro(authErroEl, e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Criar conta";
  }
});

// ===== Logout =====

btnLogout.addEventListener("click", () => {
  limparToken();
  mostrarTelaAuth();
});

// ===== Produtos (dashboard) =====

async function carregarProdutos() {
  estadoCarregandoEl.hidden = false;
  estadoVazioEl.hidden = true;
  listaEl.innerHTML = "";

  try {
    const resp = await apiFetch(API_PRODUTOS);
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
      carregarHistorico(produto.id);
    }
  } catch (e) {
    estadoCarregandoEl.hidden = true;
    if (e.message.includes("Sessão expirada")) return;
    mostrarErro(mensagemErroEl, "Não foi possível carregar os produtos.");
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

async function carregarHistorico(produtoId) {
  try {
    const resp = await apiFetch(`${API_PRODUTOS}/${produtoId}/historico`);
    if (!resp.ok) return;
    const pontos = await resp.json();

    const artigo = listaEl.querySelector(`.linha-produto[data-id="${produtoId}"]`);
    if (!artigo || pontos.length < 2) return;

    desenharSparkline(artigo.querySelector(".sparkline"), pontos);
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
    const resp = await apiFetch(`${API_PRODUTOS}/${produtoId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ativo: novoAtivo })
    });
    if (!resp.ok) throw new Error();
    carregarProdutos();
  } catch (e) {
    mostrarErro(mensagemErroEl, "Não foi possível atualizar o produto.");
  }
}

async function verificarAgora(produtoId, botao) {
  const textoOriginal = botao.textContent;
  botao.disabled = true;
  botao.textContent = "Verificando…";

  try {
    const resp = await apiFetch(`${API_PRODUTOS}/${produtoId}/verificar`, { method: "POST" });
    if (!resp.ok) {
      const erro = await resp.json().catch(() => ({}));
      throw new Error(erro.detail || "Falha ao verificar preço");
    }
    await carregarProdutos();
  } catch (e) {
    mostrarErro(mensagemErroEl, e.message);
    botao.disabled = false;
    botao.textContent = textoOriginal;
  }
}

async function removerProduto(produtoId, nome) {
  if (!confirm(`Parar de monitorar "${nome}"? Isso apaga o histórico de preços dele.`)) return;

  try {
    const resp = await apiFetch(`${API_PRODUTOS}/${produtoId}`, { method: "DELETE" });
    if (!resp.ok) throw new Error();
    carregarProdutos();
  } catch (e) {
    mostrarErro(mensagemErroEl, "Não foi possível remover o produto.");
  }
}

formCadastro.addEventListener("submit", async (e) => {
  e.preventDefault();
  limparErro(mensagemErroEl);

  const url = document.getElementById("input-url").value.trim();
  const precoAlvo = valorMascaraParaNumero(inputPrecoAlvo.value);

  if (precoAlvo === null || precoAlvo <= 0) {
    mostrarErro(mensagemErroEl, "Informe um valor desejado válido.");
    return;
  }

  btnCadastrarEl.disabled = true;
  btnCadastrarEl.textContent = "Buscando produto…";

  try {
    const resp = await apiFetch(API_PRODUTOS, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, preco_alvo: precoAlvo })
    });

    if (!resp.ok) {
      const erro = await resp.json().catch(() => ({}));
      throw new Error(erro.detail || "Não foi possível cadastrar o produto.");
    }

    formCadastro.reset();
    await carregarProdutos();
  } catch (e) {
    mostrarErro(mensagemErroEl, e.message);
  } finally {
    btnCadastrarEl.disabled = false;
    btnCadastrarEl.textContent = "Monitorar";
  }
});

// ===== Bootstrap =====

if (getToken()) {
  mostrarTelaApp();
} else {
  mostrarTelaAuth();
}