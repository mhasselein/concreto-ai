"""Testes automatizados da API do ConcretoAI (validação das entradas e previsão).

Executar na raiz do projeto, com a venv ativa:
    python -m pip install -r requirements-dev.txt
    python -m pytest
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import app

METADATA = json.loads(
    (Path(__file__).resolve().parents[1] / "models" / "metadata.json").read_text(encoding="utf-8")
)
FEATURES = METADATA["features"]
LIMITES = METADATA["limites_operacionais_treino"]
EXEMPLO = METADATA["exemplo_treino"]


@pytest.fixture(scope="module")
def cliente():
    # O "with" executa o lifespan, que carrega o pipeline e o metadata.
    with TestClient(app) as c:
        yield c


def prever(cliente, dados):
    return cliente.post("/api/prever", json=dados)


def com(**alteracoes):
    """Cópia do exemplo_treino com alguns campos alterados."""
    return {**EXEMPLO, **alteracoes}


def unico_erro(resposta):
    assert resposta.status_code == 422
    erros = resposta.json()["erros"]
    assert len(erros) == 1
    return erros[0]


# --- Previsão válida ---------------------------------------------------------

def test_exemplo_treino_reproduz_notebook(cliente):
    resposta = prever(cliente, EXEMPLO)
    assert resposta.status_code == 200
    assert resposta.json() == {"resistencia_mpa": 69.29, "unidade": "MPa"}


def test_numeros_como_texto_sao_aceitos(cliente):
    dados = {campo: str(valor) for campo, valor in EXEMPLO.items()}
    resposta = prever(cliente, dados)
    assert resposta.status_code == 200
    assert resposta.json()["resistencia_mpa"] == 69.29


@pytest.mark.parametrize("campo", FEATURES)
@pytest.mark.parametrize("extremo", ["min", "max"])
def test_limites_da_faixa_sao_aceitos(cliente, campo, extremo):
    valor = LIMITES[campo][extremo]
    if campo == "idade_dias":
        valor = int(valor)
    resposta = prever(cliente, com(**{campo: valor}))
    assert resposta.status_code == 200
    assert resposta.json()["resistencia_mpa"] > 0


# --- Campo vazio, ausente ou com texto ---------------------------------------

@pytest.mark.parametrize("campo", FEATURES)
def test_campo_ausente(cliente, campo):
    dados = {k: v for k, v in EXEMPLO.items() if k != campo}
    erro = unico_erro(prever(cliente, dados))
    assert erro["campo"] == campo
    assert erro["mensagem"] == "Campo obrigatório."


@pytest.mark.parametrize("campo", FEATURES)
def test_campo_vazio(cliente, campo):
    erro = unico_erro(prever(cliente, com(**{campo: ""})))
    assert erro["campo"] == campo
    assert "Informe um número" in erro["mensagem"]


@pytest.mark.parametrize("campo", FEATURES)
def test_campo_nulo(cliente, campo):
    erro = unico_erro(prever(cliente, com(**{campo: None})))
    assert erro["campo"] == campo
    assert "Informe um número" in erro["mensagem"]


@pytest.mark.parametrize("campo", FEATURES)
@pytest.mark.parametrize("texto", ["abc", "12abc", "1,5"])
def test_texto_no_lugar_de_numero(cliente, campo, texto):
    erro = unico_erro(prever(cliente, com(**{campo: texto})))
    assert erro["campo"] == campo
    assert "Informe um número" in erro["mensagem"]


@pytest.mark.parametrize("valor", ["NaN", "inf", "-inf"])
def test_numero_nao_finito(cliente, valor):
    erro = unico_erro(prever(cliente, com(cimento=valor)))
    assert erro["campo"] == "cimento"
    assert erro["mensagem"] == "Informe um número válido."


def test_todos_os_campos_vazios_geram_um_erro_por_campo(cliente):
    resposta = prever(cliente, {campo: "" for campo in FEATURES})
    assert resposta.status_code == 422
    assert [e["campo"] for e in resposta.json()["erros"]] == FEATURES


# --- Fora da faixa ------------------------------------------------------------

@pytest.mark.parametrize("campo", [f for f in FEATURES if f != "idade_dias"])
def test_acima_do_maximo(cliente, campo):
    erro = unico_erro(prever(cliente, com(**{campo: LIMITES[campo]["max"] + 0.01})))
    assert erro["campo"] == campo
    assert erro["mensagem"].startswith("Valor fora da faixa usada no treino")
    assert METADATA["unidades"][campo] in erro["mensagem"]


@pytest.mark.parametrize("campo", [f for f in FEATURES if f != "idade_dias"])
def test_abaixo_do_minimo(cliente, campo):
    erro = unico_erro(prever(cliente, com(**{campo: LIMITES[campo]["min"] - 0.01})))
    assert erro["campo"] == campo
    assert erro["mensagem"].startswith("Valor fora da faixa usada no treino")


def test_mensagem_de_faixa_no_formato_brasileiro(cliente):
    erro = unico_erro(prever(cliente, com(escoria=400)))
    assert erro["mensagem"] == "Valor fora da faixa usada no treino (0 a 359,4 kg/m³)."


def test_varios_campos_fora_da_faixa(cliente):
    resposta = prever(cliente, com(cimento=900, agua=10, idade_dias=400))
    assert resposta.status_code == 422
    assert {e["campo"] for e in resposta.json()["erros"]} == {"cimento", "agua", "idade_dias"}


# --- Idade --------------------------------------------------------------------

@pytest.mark.parametrize("idade", [0, -1, -28])
def test_idade_nao_positiva(cliente, idade):
    erro = unico_erro(prever(cliente, com(idade_dias=idade)))
    assert erro["campo"] == "idade_dias"
    assert erro["mensagem"] == "A idade deve ser um número inteiro positivo de dias."


@pytest.mark.parametrize("idade", [28.5, "28.5", 0.5])
def test_idade_nao_inteira(cliente, idade):
    erro = unico_erro(prever(cliente, com(idade_dias=idade)))
    assert erro["campo"] == "idade_dias"
    assert "inteiro" in erro["mensagem"]


def test_idade_acima_do_maximo(cliente):
    erro = unico_erro(prever(cliente, com(idade_dias=366)))
    assert erro["campo"] == "idade_dias"
    assert erro["mensagem"].startswith("Valor fora da faixa usada no treino")


def test_idade_inteira_escrita_com_decimal_zero_e_aceita(cliente):
    resposta = prever(cliente, com(idade_dias=28.0))
    assert resposta.status_code == 200
    assert resposta.json()["resistencia_mpa"] == 69.29


# --- Corpo da requisição ------------------------------------------------------

def test_campo_desconhecido(cliente):
    erro = unico_erro(prever(cliente, com(areia=100)))
    assert erro["campo"] == "areia"
    assert erro["mensagem"] == "Campo não reconhecido."


def test_json_invalido(cliente):
    resposta = cliente.post(
        "/api/prever", content="{oops", headers={"Content-Type": "application/json"}
    )
    erro = unico_erro(resposta)
    assert erro["campo"] is None
    assert "JSON válido" in erro["mensagem"]


@pytest.mark.parametrize("corpo", [[1, 2, 3], "texto", 42])
def test_corpo_que_nao_e_objeto(cliente, corpo):
    erro = unico_erro(prever(cliente, corpo))
    assert erro["campo"] is None
    assert "8 entradas" in erro["mensagem"]


def test_formato_padrao_dos_erros(cliente):
    erro = unico_erro(prever(cliente, com(agua="abc")))
    assert set(erro) == {"campo", "rotulo", "mensagem"}
    assert erro["rotulo"] == "Água"


# --- Demais rotas -------------------------------------------------------------

def test_metadata(cliente):
    resposta = cliente.get("/api/metadata")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["features"] == FEATURES
    assert corpo["limites"] == LIMITES
    assert set(corpo["rotulos"]) == set(FEATURES)


def test_exemplo_aleatorio_esta_na_faixa_e_preve(cliente):
    for _ in range(20):
        exemplo = cliente.get("/api/exemplo").json()
        assert list(exemplo) == FEATURES
        assert isinstance(exemplo["idade_dias"], int)
        for campo, valor in exemplo.items():
            assert LIMITES[campo]["min"] <= valor <= LIMITES[campo]["max"]
        assert prever(cliente, exemplo).status_code == 200


def test_pagina_inicial(cliente):
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert "ConcretoAI" in resposta.text
    for arquivo in ("style.css", "script.js"):
        assert cliente.get(f"/static/{arquivo}").status_code == 200
