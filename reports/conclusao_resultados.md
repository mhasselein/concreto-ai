1. O objetivo foi estimar a resistência à compressão a partir da composição e da idade.
2. Foi utilizada a base pública Concrete Compressive Strength, da UCI, com crédito a I-Cheng Yeh.
3. A base lida contém 1030 registros; a base de trabalho contém 1005.
4. Foram removidas 25 duplicatas exatas por decisão documentada do projeto.
5. Entradas iguais com alvos diferentes foram mantidas porque a causa das diferenças não foi comprovada.
6. Zeros legítimos foram preservados e não foram descartados outliers automaticamente.
7. A separação reservou 803 linhas para treino e 202 para teste, sem grupos em comum.
8. A EDA foi realizada no treino, com quatro gráficos; associações não foram tratadas como causalidade.
9. Ridge e Random Forest foram comparados nos mesmos cinco folds por grupos, com uma baseline da média.
10. Imputação e padronização foram ajustadas dentro dos pipelines para evitar vazamento de estatísticas.
11. O modelo escolhido foi Random Forest, com RMSE médio de CV de 5.578 MPa.
12. No teste final, RMSE = 4.673 MPa, MAE = 3.442 MPa e R² = 0.906.
13. Esses números descrevem este protocolo; não demonstram aprovação para uso estrutural.
14. A mesma composição em idades diferentes pode estar em conjuntos distintos, limitando a generalização avaliada.
15. Como melhoria, propõe-se avaliar grupos por composição e obter medições adicionais com contexto experimental.
16. O pipeline exportado pode ser consumido por uma interface, sem retreinamento nem padronização duplicada.
