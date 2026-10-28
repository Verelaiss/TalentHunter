import csv
import re
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

import requests

URL_API = 'https://api.github.com'
LIMITE_PERFIS = 8
TIMEOUT = 10
resultados = []


def ler_obrigatorio(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print('Informe um valor para continuar.')


def consultar_api(endpoint, parametros=None):
    try:
        resposta = requests.get(
            f'{URL_API}{endpoint}', params=parametros,
            headers={'Accept': 'application/vnd.github+json'}, timeout=TIMEOUT
        )
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.Timeout:
        print('Erro: tempo de resposta excedido.')
    except requests.exceptions.HTTPError as erro:
        codigo = erro.response.status_code if erro.response is not None else 'desconhecido'
        print(f'Erro HTTP {codigo} ao consultar GitHub.')
    except requests.exceptions.ConnectionError:
        print('Erro: falha de conexão com GitHub.')
    except requests.exceptions.RequestException as erro:
        print(f'Erro na requisição: {erro}')
    except ValueError:
        print('Erro: resposta JSON inválida.')
    return None


def adicionar_perfil(perfil):
    if any(item['link'].rstrip('/').lower() == perfil['link'].rstrip('/').lower()
           for item in resultados):
        return False
    resultados.append(perfil)
    return True


def pesquisar_github():
    linguagem = ler_obrigatorio('\nLinguagem de programação: ')
    cidade = input('Cidade (Enter para qualquer localidade): ').strip()
    consulta = f'language:{linguagem}'
    if cidade:
        consulta += f' location:"{cidade}"'
    dados = consultar_api('/search/users', {'q': consulta, 'per_page': 30})
    if dados is None:
        return
    usuarios = [u for u in dados.get('items', []) if u.get('type') == 'User']
    adicionados = 0
    for usuario in usuarios:
        if adicionados >= LIMITE_PERFIS:
            break
        login = usuario.get('login')
        if not login:
            continue
        detalhes = consultar_api(f'/users/{login}')
        if detalhes is None:
            continue
        perfil = {
            'fonte': 'GitHub',
            'nome': detalhes.get('name') or login,
            'link': detalhes.get('html_url') or usuario.get('html_url') or '',
            'cidade': detalhes.get('location') or 'Não informada',
            'experiencia': 'Não verificada',
            'area': linguagem,
            'repositorios': detalhes.get('public_repos', 0),
        }
        if perfil['link'] and adicionar_perfil(perfil):
            adicionados += 1
            print(f"\n{adicionados}. {perfil['nome']} | {perfil['cidade']}")
            print(perfil['link'])
    print(f'\n{adicionados} perfis novos do GitHub. Dados profissionais sujeitos à validação.')


def limpar_termos(entrada):
    return [termo.strip() for termo in re.split(r'[,;\n]+', entrada) if termo.strip()]


def construir_consultas_linkedin(cargo, palavras, cidade):
    # O Google não oferece garantia de cidade. Cada consulta usa uma forma
    # geográfica alternativa e restringe URLs ao padrão de perfil pessoal.
    base = ['site:linkedin.com/in/']
    if cargo:
        base.append(f'"{cargo}"')
    if palavras:
        # OR permite que uma pessoa tenha parte das competências buscadas.
        grupo = ' OR '.join(f'"{p}"' for p in palavras[:5])
        base.append(f'({grupo})')
    prefixo = ' '.join(base)
    if not cidade:
        return [('Sem filtro de cidade', prefixo)]

    normalizada = cidade.strip()
    # Para Porto Alegre, expandimos as grafias mais frequentes.
    if re.search(r'\bporto\s+alegre\b', normalizada, re.I):
        alternativas = [
            ('Cidade exata', '"Porto Alegre"'),
            ('Cidade e estado', '"Porto Alegre" "RS"'),
            ('Região metropolitana', '"Porto Alegre" "Rio Grande do Sul"'),
        ]
    else:
        alternativas = [('Cidade informada', f'"{normalizada}"')]
    return [(rotulo, f'{prefixo} {filtro}') for rotulo, filtro in alternativas]


def pesquisar_linkedin():
    print('\nPESQUISA DIRECIONADA DE PERFIS NO LINKEDIN')
    cargo = input('Cargo desejado (ex.: QA Tester): ').strip()
    palavras = limpar_termos(input('Competências separadas por vírgula: '))
    cidade = input('Cidade (ex.: Porto Alegre): ').strip()
    if not cargo and not palavras:
        print('Informe ao menos um cargo ou uma competência.')
        return
    consultas = construir_consultas_linkedin(cargo, palavras, cidade)
    print('\nConsultas preparadas:')
    for indice, (rotulo, consulta) in enumerate(consultas, start=1):
        print(f'{indice}. {rotulo}: {consulta}')
    print('\nAbrindo resultados no Google. Não é necessário informar nomes.')
    for _, consulta in consultas:
        url = 'https://www.google.com/search?' + urlencode({'q': consulta})
        if not webbrowser.open_new_tab(url):
            print('Abra este endereço manualmente:', url)
    print('\nAtenção: o Google pode mostrar outras cidades. Confira a localização')
    print('de cada profissional antes de considerá-lo para a vaga.')
    print('Nenhum dado de LinkedIn foi extraído ou cadastrado automaticamente.')


def exibir_relatorio():
    if not resultados:
        print('\nNenhum perfil estruturado salvo. Pesquisas no navegador não entram no CSV.')
        return
    print('\n' + '=' * 55)
    print('TALENTHUNTER - PERFIS REGISTRADOS')
    print('=' * 55)
    for numero, perfil in enumerate(resultados, 1):
        print(f"\n{numero}. {perfil['nome']} ({perfil['fonte']})")
        print(f"Área: {perfil['area']} | Cidade: {perfil['cidade']}")
        print(f"Experiência: {perfil['experiencia']}")
        print(f"Link: {perfil['link']}")
    print(f'\nTotal: {len(resultados)}')


def exportar_csv():
    if not resultados:
        print('Nenhum perfil estruturado para exportar.')
        return
    arquivo = Path(f"talenthunter_{datetime.now():%Y%m%d_%H%M%S}.csv")
    campos = ['fonte', 'nome', 'link', 'cidade', 'experiencia', 'area', 'repositorios']
    try:
        with arquivo.open('w', newline='', encoding='utf-8-sig') as saida:
            escritor = csv.DictWriter(saida, fieldnames=campos, delimiter=';')
            escritor.writeheader()
            escritor.writerows(resultados)
        print(f'Relatório exportado: {arquivo.resolve()}')
    except OSError as erro:
        print(f'Não foi possível salvar o CSV: {erro}')


def main():
    while True:
        print('\n' + '=' * 50)
        print('TALENTHUNTER 2.1')
        print('=' * 50)
        print('1 - Pesquisar automaticamente no GitHub')
        print('2 - Pesquisar perfis públicos do LinkedIn no Google')
        print('3 - Visualizar perfis registrados')
        print('4 - Exportar CSV dos perfis registrados')
        print('5 - Encerrar')
        try:
            opcao = input('\nEscolha uma opção: ').strip()
            if opcao == '1':
                pesquisar_github()
            elif opcao == '2':
                pesquisar_linkedin()
            elif opcao == '3':
                exibir_relatorio()
            elif opcao == '4':
                exportar_csv()
            elif opcao == '5':
                print('TalentHunter encerrado.')
                break
            else:
                print('Opção inválida.')
        except (KeyboardInterrupt, EOFError):
            print('\nExecução encerrada pelo usuário.')
            break


if __name__ == '__main__':
    main()
