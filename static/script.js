// Tela do ConcretoAI: monta o formulário a partir de /api/metadata,
// valida no navegador e envia para /api/prever. A API valida de novo.

const formulario = document.getElementById("formulario");
const containerCampos = document.getElementById("campos");
const erroGeral = document.getElementById("erro-geral");
const botaoPrever = document.getElementById("botao-prever");
const resultadoVazio = document.getElementById("resultado-vazio");
const resultadoValor = document.getElementById("resultado-valor");
const valorMpa = document.getElementById("valor-mpa");
const infoModelo = document.getElementById("info-modelo");

let metadata = null;

const formatador = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });

function formatar(valor) {
  return formatador.format(valor);
}

function criarCampo(nome) {
  const limites = metadata.limites[nome];
  const unidade = metadata.unidades[nome];
  const ehIdade = nome === "idade_dias";

  const campo = document.createElement("div");
  campo.className = "campo";
  campo.dataset.campo = nome;
  campo.innerHTML = `
    <label for="campo-${nome}"></label>
    <div class="entrada">
      <input id="campo-${nome}" name="${nome}" type="text" autocomplete="off"
             inputmode="${ehIdade ? "numeric" : "decimal"}">
      <span class="sufixo"></span>
    </div>
    <div class="faixa"></div>
    <div class="mensagem-erro" hidden></div>
  `;
  campo.querySelector("label").textContent = metadata.rotulos[nome];
  campo.querySelector(".sufixo").textContent = unidade;
  campo.querySelector(".faixa").textContent =
    `Faixa: ${formatar(limites.min)} a ${formatar(limites.max)} ${unidade}`;
  campo.querySelector("input").addEventListener("input", () => limparErro(nome));
  return campo;
}

function mostrarErro(nome, mensagem) {
  const campo = containerCampos.querySelector(`[data-campo="${nome}"]`);
  if (!campo) {
    mostrarErroGeral(mensagem);
    return;
  }
  campo.classList.add("com-erro");
  const elemento = campo.querySelector(".mensagem-erro");
  elemento.textContent = mensagem;
  elemento.hidden = false;
}

function limparErro(nome) {
  const campo = containerCampos.querySelector(`[data-campo="${nome}"]`);
  campo.classList.remove("com-erro");
  campo.querySelector(".mensagem-erro").hidden = true;
}

function mostrarErroGeral(mensagem) {
  erroGeral.textContent = mensagem;
  erroGeral.hidden = false;
}

function limparErros() {
  metadata.features.forEach(limparErro);
  erroGeral.hidden = true;
}

function esconderResultado() {
  resultadoValor.hidden = true;
  resultadoVazio.hidden = false;
}

// Converte para o formato do JavaScript. Pontos em grupos de 3 dígitos são
// separador de milhar ("1.040", "1.134,3"); fora disso, o ponto é decimal ("2.5").
function normalizarNumero(texto) {
  const semEspacos = texto.trim();
  if (/^[-+]?\d{1,3}(\.\d{3})+(,\d+)?$/.test(semEspacos)) {
    return semEspacos.replace(/\./g, "").replace(",", ".");
  }
  return semEspacos.replace(",", ".");
}

// Aceita vírgula ou ponto como separador decimal. Retorna {valor} ou {erro}.
function lerValor(nome, texto) {
  const limpo = normalizarNumero(texto);
  if (limpo === "") return { erro: "Campo obrigatório." };
  if (!/^[-+]?(\d+\.?\d*|\.\d+)$/.test(limpo)) return { erro: "Informe um número." };

  const valor = Number(limpo);
  const limites = metadata.limites[nome];
  const unidade = metadata.unidades[nome];

  if (nome === "idade_dias" && (!Number.isInteger(valor) || valor <= 0)) {
    return { erro: "A idade deve ser um número inteiro positivo de dias." };
  }
  if (valor < limites.min || valor > limites.max) {
    return {
      erro: `Valor fora da faixa usada no treino (${formatar(limites.min)} a ${formatar(limites.max)} ${unidade}).`,
    };
  }
  return { valor };
}

async function prever(evento) {
  evento.preventDefault();
  limparErros();

  const dados = {};
  let valido = true;
  for (const nome of metadata.features) {
    const texto = formulario.elements[nome].value;
    const lido = lerValor(nome, texto);
    if (lido.erro) {
      mostrarErro(nome, lido.erro);
      valido = false;
    } else {
      dados[nome] = lido.valor;
    }
  }
  if (!valido) {
    esconderResultado();
    mostrarErroGeral("Corrija os campos destacados e tente novamente.");
    return;
  }

  botaoPrever.disabled = true;
  botaoPrever.textContent = "Calculando…";
  try {
    const resposta = await fetch("/api/prever", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });
    const corpo = await resposta.json();

    if (!resposta.ok) {
      esconderResultado();
      (corpo.erros || [{ mensagem: "Não foi possível calcular a previsão." }])
        .forEach((e) => mostrarErro(e.campo, e.mensagem));
      return;
    }

    valorMpa.textContent = formatar(corpo.resistencia_mpa);
    resultadoVazio.hidden = true;
    resultadoValor.hidden = false;
  } catch {
    esconderResultado();
    mostrarErroGeral("Não foi possível falar com o servidor. Verifique se a API está rodando.");
  } finally {
    botaoPrever.disabled = false;
    botaoPrever.textContent = "Prever resistência";
  }
}

async function preencherExemplo() {
  limparErros();
  esconderResultado();
  let exemplo;
  try {
    const resposta = await fetch("/api/exemplo");
    if (!resposta.ok) throw new Error();
    exemplo = await resposta.json();
  } catch {
    mostrarErroGeral("Não foi possível sortear um exemplo. Verifique se a API está rodando.");
    return;
  }
  for (const nome of metadata.features) {
    formulario.elements[nome].value = formatar(exemplo[nome]).replace(/\./g, "");
  }
}

function limparFormulario() {
  formulario.reset();
  limparErros();
  esconderResultado();
}

async function iniciar() {
  try {
    const resposta = await fetch("/api/metadata");
    if (!resposta.ok) throw new Error();
    metadata = await resposta.json();
  } catch {
    containerCampos.innerHTML = "";
    mostrarErroGeral("Não foi possível carregar o modelo. Verifique se a API está rodando.");
    return;
  }

  containerCampos.innerHTML = "";
  metadata.features.forEach((nome) => containerCampos.appendChild(criarCampo(nome)));

  const m = metadata.metricas_teste;
  infoModelo.textContent =
    `Modelo: ${metadata.modelo}. No conjunto de teste: erro médio absoluto de ` +
    `${formatar(m["MAE (MPa)"])} MPa, RMSE de ${formatar(m["RMSE (MPa)"])} MPa e R² de ${formatar(m["R²"])}.`;

  formulario.addEventListener("submit", prever);
  document.getElementById("botao-exemplo").addEventListener("click", preencherExemplo);
  document.getElementById("botao-limpar").addEventListener("click", limparFormulario);
}

iniciar();
