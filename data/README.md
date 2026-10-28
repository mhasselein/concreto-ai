# Dados — Concrete Compressive Strength

## Fonte
- **Base pública:** Concrete Compressive Strength, do UCI Machine Learning Repository.
- **Página oficial:** https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength
- **DOI:** https://doi.org/10.24432/C5PK67
- **Crédito:** I-Cheng Yeh (Prof., Chung-Hua University, Taiwan), criador e doador. Doado em 3 de agosto de 2007.
- **Download:** `https://archive.ics.uci.edu/static/public/165/concrete+compressive+strength.zip` (endereço apontado pelo botão *Download* da página oficial), baixado em 05/10/2026.

## Referência (citação exigida pelo readme original)
I-Cheng Yeh, "Modeling of strength of high performance concrete using artificial neural networks," *Cement and Concrete Research*, Vol. 28, No. 12, pp. 1797–1808 (1998). DOI: 10.1016/S0008-8846(98)00165-3

## Licença
**Creative Commons Attribution 4.0 International (CC BY 4.0)** — https://creativecommons.org/licenses/by/4.0/ — licença **declarada explicitamente na página oficial** da UCI (conferida pelo autor do trabalho). Permite uso, compartilhamento e adaptação, inclusive para fins educacionais, desde que se dê o crédito adequado a I-Cheng Yeh, se indique a fonte (página/DOI acima) e se informe eventuais alterações. Neste trabalho os dados originais não foram modificados; apenas colunas são renomeadas em memória no notebook.

**Sobre a API:** a resposta da API da UCI (`https://archive.ics.uci.edu/api/dataset?id=165`) retornou o campo `license` vazio (`None`) em 05/10/2026. Isso é uma **ausência de metadado na API**, não ausência de licença: a licença CC BY 4.0 consta na página oficial e prevalece como referência.

**Aviso do readme original** (`raw/Concrete_Readme.txt`, preservado):
> "Reuse of this database is unlimited with retention of copyright notice for Prof. I-Cheng Yeh and the following published paper: [referência acima]"

## Arquivos em `raw/` (originais, não modificar)
| Arquivo | Descrição |
| --- | --- |
| `concrete_compressive_strength_uci.zip` | Pacote exatamente como baixado (o servidor entrega um `.zip`). |
| `Concrete_Data.xls` | Dados (extraído do zip). Planilha `Sheet1`. |
| `Concrete_Readme.txt` | Readme oficial (extraído do zip). |

SHA-256 (para conferir integridade):
- `concrete_compressive_strength_uci.zip`: `dad85d14de8aee4e07479daa774e6b569a313715b71a3b92c95a07cf91c2c9a7`
- `Concrete_Data.xls`: `710076c66b9ca3f8050e7942f3dcbdbe04013534daeb0077ffd3079a52d8e0c4`

## Variáveis e unidades
Segundo o readme: 1030 observações, 8 entradas quantitativas e 1 saída; sem valores ausentes declarados. Dados brutos, sem escalonamento.

| Coluna original no `.xls` | Papel | Unidade |
| --- | --- | --- |
| Cement (component 1) | entrada | kg por m³ de mistura |
| Blast Furnace Slag (component 2) | entrada | kg por m³ de mistura |
| Fly Ash (component 3) | entrada | kg por m³ de mistura |
| Water (component 4) | entrada | kg por m³ de mistura |
| Superplasticizer (component 5) | entrada | kg por m³ de mistura |
| Coarse Aggregate (component 6) | entrada | kg por m³ de mistura |
| Fine Aggregate (component 7) | entrada | kg por m³ de mistura |
| Age | entrada | dias (1–365) |
| Concrete compressive strength | **alvo** | MPa |

Os nomes originais das colunas contêm espaços duplicados e espaço final; o notebook os renomeia por um mapeamento explícito, sem alterar o arquivo original.
