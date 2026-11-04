"""API do ConcretoAI: estima a resistência à compressão do concreto (MPa).

Carrega o pipeline exportado pelo notebook uma única vez, na inicialização.
O pipeline já contém imputador e scaler; as entradas vão em unidades originais.

Executar na raiz do projeto:
    python -m uvicorn app:app --reload
"""

import json
import random
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict

RAIZ = Path(__file__).resolve().parent
CAMINHO_PIPELINE = RAIZ / "models" / "pipeline.joblib"
CAMINHO_METADATA = RAIZ / "models" / "metadata.json"
CAMINHO_DADOS = RAIZ / "data" / "raw" / "Concrete_Data.xls"
CAMINHO_SPLIT = RAIZ / "data" / "processed" / "split_treino_teste.csv"
PASTA_STATIC = RAIZ / "static"

ROTULOS = {
    "cimento": "Cimento",
    "escoria": "Escória de alto-forno",
    "cinza_volante": "Cinza volante",
    "agua": "Água",
    "superplastificante": "Superplastificante",
    "agregado_graudo": "Agregado graúdo",
    "agregado_miudo": "Agregado miúdo",
    "idade_dias": "Idade",
}

# Mensagens amigáveis para os erros de validação do pydantic.
MENSAGENS_ERRO = {
    "missing": "Campo obrigatório.",
    "float_parsing": "Informe um número.",
    "float_type": "Informe um número.",
    "finite_number": "Informe um número válido.",
    "int_parsing": "Informe um número inteiro.",
    "int_type": "Informe um número inteiro.",
    "int_from_float": "Informe um número inteiro de dias.",
    "extra_forbidden": "Campo não reconhecido.",
    "json_invalid": "Requisição inválida: o corpo não é um JSON válido.",
    "model_attributes_type": "Requisição inválida: envie um objeto JSON com as 8 entradas.",
}


class Mistura(BaseModel):
    """As 8 entradas do modelo, em kg/m³ (componentes) e dias (idade)."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    cimento: float
    escoria: float
    cinza_volante: float
    agua: float
    superplastificante: float
    agregado_graudo: float
    agregado_miudo: float
    idade_dias: int


class Previsao(BaseModel):
    resistencia_mpa: float
    unidade: str


def formatar_numero(valor: float) -> str:
    """Formata no padrão brasileiro, sem casas decimais desnecessárias."""
    texto = f"{valor:,.2f}".rstrip("0").rstrip(".")
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def erro(campo: str | None, mensagem: str) -> dict:
    return {"campo": campo, "rotulo": ROTULOS.get(campo), "mensagem": mensagem}


def validar_faixas(mistura: Mistura, metadata: dict) -> list[dict]:
    """Confere cada entrada contra a faixa observada no treino."""
    erros = []
    for campo, limites in metadata["limites_operacionais_treino"].items():
        valor = getattr(mistura, campo)
        if campo == "idade_dias" and valor <= 0:
            erros.append(erro(campo, "A idade deve ser um número inteiro positivo de dias."))
        elif not limites["min"] <= valor <= limites["max"]:
            unidade = metadata["unidades"][campo]
            erros.append(erro(
                campo,
                f"Valor fora da faixa usada no treino "
                f"({formatar_numero(limites['min'])} a {formatar_numero(limites['max'])} {unidade}).",
            ))
    return erros


def carregar_misturas_treino(features: list[str]) -> list[dict]:
    """Misturas reais do conjunto de treino, usadas no botão de exemplo aleatório.

    As 8 primeiras colunas do .xls estão na mesma ordem das features.
    """
    dados = pd.read_excel(CAMINHO_DADOS).iloc[:, : len(features)]
    dados.columns = features
    split = pd.read_csv(CAMINHO_SPLIT)
    indices_treino = split.loc[split["conjunto"] == "treino", "indice_original"]
    treino = dados.loc[indices_treino].round(2)
    treino["idade_dias"] = treino["idade_dias"].astype(int)
    return treino.to_dict(orient="records")


@asynccontextmanager
async def lifespan(app: FastAPI):
    metadata = json.loads(CAMINHO_METADATA.read_text(encoding="utf-8"))
    if list(Mistura.model_fields) != metadata["features"]:
        raise RuntimeError("As entradas da API não batem com as features do metadata.json.")
    app.state.metadata = metadata
    app.state.pipeline = joblib.load(CAMINHO_PIPELINE)
    app.state.misturas_treino = carregar_misturas_treino(metadata["features"])
    yield


app = FastAPI(
    title="ConcretoAI",
    description="Estimativa da resistência à compressão do concreto (MPa).",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(request: Request, exc: RequestValidationError):
    erros = []
    for e in exc.errors():
        local = [parte for parte in e["loc"] if parte != "body"]
        campo = local[0] if local and isinstance(local[0], str) else None
        erros.append(erro(campo, MENSAGENS_ERRO.get(e["type"], "Valor inválido.")))
    return JSONResponse(status_code=422, content={"erros": erros})


@app.get("/api/metadata")
def obter_metadata(request: Request):
    """Informações que a tela usa para montar o formulário."""
    metadata = request.app.state.metadata
    return {
        "features": metadata["features"],
        "rotulos": ROTULOS,
        "unidades": metadata["unidades"],
        "limites": metadata["limites_operacionais_treino"],
        "exemplo": metadata["exemplo_treino"],
        "unidade_resultado": metadata["unidade_resultado"],
        "modelo": metadata["modelo"],
        "metricas_teste": metadata["metricas_teste"],
    }


@app.get("/api/exemplo")
def sortear_exemplo(request: Request):
    """Sorteia uma mistura real do conjunto de treino para preencher a tela."""
    return random.choice(request.app.state.misturas_treino)


@app.post("/api/prever", response_model=Previsao)
def prever(mistura: Mistura, request: Request):
    metadata = request.app.state.metadata
    erros = validar_faixas(mistura, metadata)
    if erros:
        return JSONResponse(status_code=422, content={"erros": erros})

    entrada = pd.DataFrame([mistura.model_dump()], columns=metadata["features"])
    resistencia = float(request.app.state.pipeline.predict(entrada)[0])
    return Previsao(resistencia_mpa=round(resistencia, 2), unidade=metadata["unidade_resultado"])


@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(PASTA_STATIC / "index.html")


app.mount("/static", StaticFiles(directory=PASTA_STATIC), name="static")
