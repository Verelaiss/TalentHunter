import csv
from urllib.parse import parse_qs, urlparse
from unittest.mock import Mock
import requests
import main


def test_consulta_github_sucesso(monkeypatch):
    resposta = Mock()
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = {'items': [{'login': 'teste'}]}
    monkeypatch.setattr(main.requests, 'get', lambda *args, **kwargs: resposta)
    assert main.consultar_api('/search/users') == {'items': [{'login': 'teste'}]}


def test_consulta_github_timeout(monkeypatch, capsys):
    def falhar(*args, **kwargs):
        raise requests.exceptions.Timeout()
    monkeypatch.setattr(main.requests, 'get', falhar)
    assert main.consultar_api('/search/users') is None
    assert 'tempo' in capsys.readouterr().out.lower()


def test_consulta_github_http_403(monkeypatch, capsys):
    resposta = requests.Response()
    resposta.status_code = 403
    resposta.url = 'https://api.github.com/search/users'
    def falhar(*args, **kwargs):
        raise requests.exceptions.HTTPError(response=resposta)
    monkeypatch.setattr(main.requests, 'get', falhar)
    assert main.consultar_api('/search/users') is None
    assert '403' in capsys.readouterr().out


def test_entrada_obrigatoria(monkeypatch):
    entradas = iter(['  ', ' Python '])
    monkeypatch.setattr('builtins.input', lambda _: next(entradas))
    assert main.ler_obrigatorio('Linguagem: ') == 'Python'


def test_linkedin_consultas_porto_alegre():
    consultas = main.construir_consultas_linkedin('QA', ['Python', 'SQL'], 'Porto Alegre,RS')
    assert len(consultas) == 3
    assert all('"Porto Alegre"' in consulta for _, consulta in consultas)
    assert all('site:linkedin.com/in/' in consulta for _, consulta in consultas)


def test_linkedin_nao_pede_nome(monkeypatch):
    entradas = iter(['QA', 'Python, SQL', 'Porto Alegre'])
    monkeypatch.setattr('builtins.input', lambda _: next(entradas))
    abertas = []
    monkeypatch.setattr(main.webbrowser, 'open_new_tab', lambda url: abertas.append(url) or True)
    main.pesquisar_linkedin()
    assert len(abertas) == 3
    assert all('google.com/search?' in url for url in abertas)
    assert not main.resultados


def test_github_limita_oito_e_remove_duplicados(monkeypatch):
    main.resultados.clear()
    usuarios = [{'login': f'user{i}', 'type': 'User'} for i in range(15)]
    def api(endpoint, parametros=None):
        if endpoint == '/search/users':
            return {'items': usuarios}
        login = endpoint.split('/')[-1]
        return {'name': login, 'html_url': f'https://github.com/{login}', 'public_repos': 2}
    monkeypatch.setattr(main, 'consultar_api', api)
    entradas = iter(['Python', ''])
    monkeypatch.setattr('builtins.input', lambda _: next(entradas))
    main.pesquisar_github()
    assert len(main.resultados) == 8
    main.resultados.clear()


def test_exportar_csv(monkeypatch, tmp_path):
    main.resultados.clear()
    main.resultados.append({'fonte':'GitHub','nome':'Exemplo','link':'https://github.com/exemplo','cidade':'Porto Alegre','experiencia':'Não verificada','area':'Python','repositorios':2})
    monkeypatch.chdir(tmp_path)
    main.exportar_csv()
    arquivos = list(tmp_path.glob('talenthunter_*.csv'))
    assert len(arquivos) == 1
    with arquivos[0].open(encoding='utf-8-sig', newline='') as f:
        linhas = list(csv.DictReader(f, delimiter=';'))
    assert linhas[0]['nome'] == 'Exemplo'
    main.resultados.clear()
