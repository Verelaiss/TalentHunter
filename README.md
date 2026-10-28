# TalentHunter 2.1

Projeto de estudo em Python voltado à descoberta inicial de perfis técnicos para recrutamento, com validação final humana. O objetivo é demonstrar integração com API REST, tratamento de erros, filtros, testes e exportação de dados.

## Funcionalidades

- Pesquisa automática de perfis públicos no **GitHub** por linguagem e cidade, com até oito novos perfis por busca.
- Pesquisa direcionada de perfis públicos do **LinkedIn via Google**, abrindo consultas no navegador por cargo, competências e cidade.
- Relatório no terminal e exportação **CSV** dos perfis estruturados coletados no GitHub.
- Tratamento de timeout, erros HTTP, falhas de conexão e entradas inválidas.

## Requisitos

Python 3.10 ou superior (recomendado). Conexão com a internet para pesquisas reais.

## Instalação e execução (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Testes automatizados

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

Os testes simulam a API e a abertura do navegador, sem fazer consultas reais ao GitHub ou Google.

## Limitações conhecidas

- O LinkedIn **não é consultado por API**: a ferramenta abre buscas no Google e **não coleta automaticamente** nomes, experiência ou links dos resultados.
- Filtros geográficos no Google não garantem residência na cidade pesquisada.
- Dados do GitHub são públicos e autodeclarados; número de repositórios não indica competência ou senioridade.
- O CSV contém apenas perfis estruturados adicionados durante a sessão (atualmente GitHub); a lista em memória é perdida ao encerrar.
- Consultas ao GitHub estão sujeitas a limites de requisições da API.
- O projeto não determina elegibilidade nem substitui a avaliação humana.

## Tecnologias

Python, requests, API REST do GitHub, CSV, pytest e unittest.mock.

## Próximas evoluções

Integração com fonte autorizada de resultados estruturados, deduplicação entre fontes, análise verificável de repositórios e persistência dos dados.
