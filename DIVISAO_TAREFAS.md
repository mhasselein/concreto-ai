# Divisão de tarefas — ConcretoAI

Trabalho final de Machine Learning (PUC Minas). **Entrega no Portal do Aluno: 11/11, até 23:59** (o enunciado também traz "11/10/2026" na tabela inicial; conferir no portal). Para ter margem, o grupo entrega até **10/11**.

O que o professor pede: notebook executado, relatório em PDF (mínimo 5 páginas, com prints da interface), código da interface, modelo `.joblib` e, como bônus, o link deste repositório no relatório. O relatório precisa dizer o que cada integrante fez.

## Visão geral

| Integrante | Responsabilidade | Entrega principal | Situação |
| --- | --- | --- | --- |
| Mateus | Estrutura, dados, notebook e modelo | `notebooks/experimento.ipynb`, `models/`, `README.md` | **Concluído** |
| Eduardo | Interface (FastAPI + HTML) | `app.py`, `static/index.html` | A fazer |
| Paulo | Testes e prints da interface | `reports/screenshots/` | A fazer |
| Yara | Relatório: parte técnica | Seções 1 a 5 do PDF | A fazer |
| Carlos | Relatório: interface, conclusão e fechamento | Seções 6 e 7, PDF final e `.zip` | A fazer |

## O que o Mateus já fez

- Escolheu o tema, o dataset (Concrete Compressive Strength, UCI) e a técnica (regressão).
- Montou a estrutura do projeto e o repositório no GitHub.
- Escreveu e executou o notebook completo, nas 14 seções pedidas:
  - inspeção dos dados, tratamento de duplicatas e separação treino/teste por grupos;
  - EDA com 4 gráficos e interpretações;
  - comparação de Ridge, Random Forest e uma referência pela média, com validação cruzada;
  - avaliação final (RMSE 4,67 MPa, MAE 3,44 MPa, R² 0,906) e gráfico real × predito;
  - exportação do pipeline, do scaler e dos metadados com `joblib`;
  - conclusão.
- Definiu o contrato do modelo para a interface (seção 13 do notebook).
- Escreveu o README e este plano.

**Daqui para frente:** revisar os pull requests, trocar os primeiros nomes pelos nomes completos (notebook e capa do relatório) e fazer a leitura final do conjunto antes de entregar.

## Eduardo — interface

Branch: `interface`. Arquivos: `app.py` na raiz e `static/index.html` (CSS e JS podem ficar em `static/`).

- API FastAPI que carrega `models/pipeline.joblib` **uma vez**, na inicialização. Nunca retreina.
- Rota de previsão que recebe as 8 entradas em unidades originais, monta um DataFrame com as colunas na ordem de `models/metadata.json` e chama `pipeline.predict`. **Não** aplicar o `scaler.joblib` antes: o scaler já está dentro do pipeline.
- A tela serve o `index.html` e tem:
  - um campo para cada uma das 8 entradas, com a unidade (kg/m³ ou dias);
  - botão de previsão;
  - resultado claro, em MPa;
  - identidade visual limpa.
- Tratamento de erro com mensagem amigável para:
  - campo vazio;
  - texto no lugar de número;
  - valor fora da faixa plausível. Usar `limites_operacionais_treino` do `metadata.json`.
  - A idade deve ser um inteiro positivo.
- Teste de conferência: com a entrada `exemplo_treino` do `metadata.json`, o resultado deve ser **69,29 MPa**, igual ao do notebook.
- Como rodar: `python -m uvicorn app:app --reload`.

## Paulo — testes e prints

Branch: `testes`.

1. **Agora, sem depender da interface:** clonar o repositório numa pasta nova, criar a venv, instalar o `requirements.txt` e rodar o notebook inteiro (*Restart & Run All*). Anotar qualquer erro ou instrução que faltou no README e corrigir.
2. **Depois que o Eduardo entregar a interface:**
   - conferir que a previsão da tela é igual à do pipeline;
   - testar as entradas inválidas (vazio, texto, fora da faixa, valores negativos);
   - registrar o que encontrar como *issue* para o Eduardo corrigir.
3. Tirar os prints finais e salvar em `reports/screenshots/`:
   - `01_tela_principal.png`
   - `02_previsao_sucesso.png`
   - `03_erro_tratado.png`

## Yara — relatório, parte técnica

Branch: `relatorio`. Fonte do texto em `reports/relatorio/` e PDF final em `reports/`.

Seções:
1. Capa (título, integrantes, data).
2. Introdução (contexto, justificativa e objetivo).
3. Dataset (fonte e citação do autor, 1030 registros, 1005 após remover duplicatas, descrição das colunas e um ou dois prints dos dados).
4. Metodologia (pré-processamento, separação por grupos, modelos testados, validação cruzada e métricas).
5. Resultados (tabela comparativa dos modelos, gráficos de `reports/figures/` e interpretação).

Todos os números e gráficos já estão no notebook e em `reports/`. Citar a fonte dos dados: I-Cheng Yeh, *Cement and Concrete Research*, 1998 (referência completa no cabeçalho do notebook).

## Carlos — relatório, interface e fechamento

Branch: `relatorio-final`.

Seções:
6. Interface gráfica (descrição, instruções curtas de instalação e execução, os 3 prints do Paulo e uma breve explicação de uso).
7. Conclusão (resumo, resposta ao problema, limitações e melhorias futuras), mais a **contribuição de cada integrante** (usar este documento) e o **link do GitHub** (bônus).

Fechamento:
- juntar as partes da Yara e do Carlos num único PDF, com pelo menos 5 páginas;
- montar o `.zip` de entrega com notebook, `app.py`, `static/`, `models/`, `data/`, `requirements.txt` e o PDF, **sem** a pasta `.venv`.

## Cronograma sugerido

| Data | Marco |
| --- | --- |
| 31/10 | Eduardo abre o pull request da interface. Paulo termina o teste em ambiente limpo. |
| 03/11 | Interface revisada e na `main`. Paulo entrega os prints. |
| 05/11 | Rascunho completo do relatório (Yara e Carlos). |
| 08/11 | Revisão do grupo: notebook, interface e PDF. |
| 10/11 | Entrega no Portal do Aluno, com o repositório público. |

## Como trabalhar no repositório

```powershell
git clone https://github.com/mhasselein/concreto-ai.git
cd concreto-ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

git checkout -b NOME-DA-SUA-BRANCH
# ... trabalhar ...
git add .
git commit -m "descrição curta do que foi feito"
git push -u origin NOME-DA-SUA-BRANCH
```

Depois do push, abrir um *pull request* no GitHub para a `main`. O Mateus revisa e junta. Não commitar diretamente na `main` e não mexer em `models/` nem no notebook sem combinar antes, porque o relatório e a interface dependem deles.
