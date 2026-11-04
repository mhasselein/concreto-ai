# ConcretoAI

Estimativa da **resistência à compressão do concreto (MPa)** a partir da composição da mistura e da idade, usando regressão supervisionada, com interface web.

Trabalho final da disciplina **Machine Learning** — Pós-Graduação em IA Generativa e Aplicações com LLMs, PUC Minas (Prof. Maurício Rodrigues da Silva).

> **Status:** notebook concluído e executado do início ao fim (modelagem, avaliação e exportação do pipeline). API FastAPI e interface web concluídas. Relatório em PDF em desenvolvimento.

Divisão de tarefas do grupo e cronograma: [DIVISAO_TAREFAS.md](DIVISAO_TAREFAS.md).

## Objetivo

Prever a resistência à compressão do concreto (variável contínua, em MPa) com um modelo de regressão, e disponibilizá-lo em uma interface onde o usuário informa os componentes da mistura e recebe o valor estimado.

## Proposta

| Item | Definição |
| --- | --- |
| Dataset | Concrete Compressive Strength (UCI Machine Learning Repository) |
| Tarefa | Regressão supervisionada |
| Modelos comparados | Ridge e RandomForestRegressor |
| Métricas | RMSE, MAE, R² e gráfico real vs. predito |
| Interface | FastAPI + HTML, CSS e JavaScript |

## Tecnologias

Python 3.12 · pandas · numpy · scikit-learn · matplotlib · seaborn · joblib · Jupyter/ipykernel · FastAPI · uvicorn · pydantic · xlrd

## Ambiente virtual

Cada integrante cria a própria venv na raiz do projeto (a pasta `.venv/` não vai para o repositório). Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

No VS Code, selecione o interpretador `.venv` e use-o como kernel do notebook.

## Estrutura

```
concreto-ai/
├── README.md
├── data/                 # README.md do dataset
│   ├── raw/              # dataset original (UCI)
│   └── processed/        # registro do split treino/teste
├── notebooks/            # notebook de experimento (.ipynb)
├── models/               # pipeline exportado (.joblib)
├── static/               # frontend (index.html, style.css, script.js)
├── reports/
│   ├── figures/          # gráficos gerados pelo notebook
│   └── screenshots/      # prints da interface
├── tests/                # testes automatizados da API (pytest)
└── app.py                # API FastAPI (serve também a interface)
```

## Decisões de dados (resumo)

- Base de trabalho: 1005 linhas, após remover 25 duplicatas exatas (decisão do projeto; as 9 entradas iguais com resistências diferentes e os zeros legítimos foram preservados).
- Separação por grupos (combinação exata das 8 entradas): `GroupShuffleSplit`, 20 %, `random_state=42` → 803 linhas no treino e 202 no teste, sem grupos em comum. O teste fica reservado para a avaliação final.
- Validação cruzada prevista: `GroupKFold` com 5 folds, só no treino.
- Limitação: o agrupamento não impede a mesma composição em idades diferentes nos dois conjuntos; não se garante generalização para receitas inéditas.
- EDA (só no treino): 4 gráficos em `reports/figures/`.
- Modelo escolhido: Random Forest (RMSE médio de CV 5,58 MPa, contra 10,33 do Ridge e 16,52 da média). No teste: RMSE 4,67 MPa, MAE 3,44 MPa e R² 0,906.

## Como executar

Na raiz do projeto, com a venv ativa (ver seção anterior):

```powershell
# 1. Notebook: abra notebooks/experimento.ipynb, selecione o kernel da venv e use Restart & Run All.
#    Ele regenera os gráficos em reports/figures e o modelo em models/.

# 2. Interface:
python -m uvicorn app:app --reload
```

Com o servidor rodando, abra **http://127.0.0.1:8000** no navegador. A documentação interativa da API fica em http://127.0.0.1:8000/docs.

> No Windows, o `--reload` às vezes não recarrega depois de uma mudança no `app.py`. Se a tela não refletir a alteração, pare o servidor (Ctrl+C) e rode o comando de novo.

## Interface

A API (`app.py`) carrega `models/pipeline.joblib` e `models/metadata.json` **uma única vez**, na inicialização, e nunca retreina o modelo. As entradas vão para o pipeline em unidades originais: o scaler já está dentro dele, então `scaler.joblib` não é aplicado antes.

| Rota | Função |
| --- | --- |
| `GET /` | Tela (`static/index.html`). |
| `GET /api/metadata` | Campos, rótulos, unidades, faixas de treino e métricas; a tela monta o formulário a partir daqui. |
| `GET /api/exemplo` | Sorteia uma mistura real do conjunto de treino (usada no botão *Exemplo aleatório*). |
| `POST /api/prever` | Recebe as 8 entradas e devolve a resistência estimada, por exemplo `{"resistencia_mpa": 69.29, "unidade": "MPa"}`. |

**Uso da tela:** preencha as 8 entradas (componentes em kg/m³ e idade em dias) e clique em *Prever resistência*. O botão *Exemplo aleatório* preenche os campos com uma mistura real do treino, e *Limpar* zera o formulário. Os números aceitam vírgula ou ponto como decimal e ponto como separador de milhar (`1.040`, `2,5`).

**Validação:** é feita no navegador e repetida na API. Erros retornam HTTP 422 no formato `{"erros": [{"campo", "rotulo", "mensagem"}]}`, e a tela mostra a mensagem embaixo do campo correspondente. Casos tratados:

- campo vazio ou ausente;
- texto no lugar de número;
- valor fora da faixa observada no treino (`limites_operacionais_treino` do `metadata.json`);
- idade que não seja um número inteiro positivo de dias.

**Teste de conferência:** com a entrada `exemplo_treino` do `metadata.json` (540 / 0 / 0 / 162 / 2,5 / 1040 / 676 / 28), a previsão deve ser **69,29 MPa**, igual à do notebook.

**Testes automatizados:** `tests/test_api.py` cobre a previsão de conferência, os limites de cada faixa e todos os casos de erro acima, além das rotas de metadata, exemplo e da página. As dependências de teste ficam em `requirements-dev.txt` (não fazem parte da entrega):

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Fonte dos dados

Base pública *Concrete Compressive Strength*, UCI Machine Learning Repository — https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength · DOI https://doi.org/10.24432/C5PK67 · licença CC BY 4.0 · crédito: I-Cheng Yeh. Detalhes em `data/README.md`.
