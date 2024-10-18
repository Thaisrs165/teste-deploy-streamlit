from flask import Flask, request, make_response, json
import pandas as pd

# Inicializando a aplicação Flask
app = Flask(__name__)

# Carregando o banco de dados (CSV) de imóveis em um DataFrame do pandas
df_imoveis = pd.read_csv('banco_de_dados.csv')

# Definindo a rota para buscar imóveis (com ou sem filtros)
@app.route('/imoveis', methods=['GET'])
def buscar_imoveis():
    """
    Rota para buscar imóveis.
    Se não forem fornecidos parâmetros, retorna todos os imóveis.
    Se houver parâmetros na requisição, aplica filtros e retorna os imóveis filtrados.
    """
    # 1. Captura os parâmetros da URL (query string)
    tipo_imovel = request.args.get('tipo_imovel')  # Exemplo: ?tipo_imovel=Apartamento
    preco_min = request.args.get('preco_min')      # Exemplo: ?preco_min=200000
    preco_max = request.args.get('preco_max')      # Exemplo: ?preco_max=500000
    cep = request.args.get('cep')                  # Exemplo: ?cep=12345-678

    # 2. Construindo a lista de condições
    condicoes = []  # Lista para armazenar condições de filtragem

    # Filtro por tipo de imóvel
    if tipo_imovel:
        condicoes.append(df_imoveis['Tipo de Imóvel'] == tipo_imovel)

    # Filtro por faixa de preço (preço mínimo e preço máximo)
    try:
        if preco_min:
            preco_min = int(preco_min)
            condicoes.append(df_imoveis['Preço'] >= preco_min)
        if preco_max:
            preco_max = int(preco_max)
            condicoes.append(df_imoveis['Preço'] <= preco_max)
    except ValueError:
        # Se os valores de preço não forem válidos (não são inteiros), retorna um erro 400
        return make_response(json.dumps({
            "status": "error",
            "message": "Os valores de preço mínimo ou máximo são inválidos."
        }), 400)

    # Filtro por CEP
    if cep:
        condicoes.append(df_imoveis['CEP'] == cep)

    # 3. Aplicar as condições no DataFrame
    if condicoes:
        # Se houver condições, aplicamos todas elas combinadas com "E" lógico
        filtro_final = condicoes[0]  # Começa com a primeira condição
        for cond in condicoes[1:]:   # Aplica as outras condições
            filtro_final &= cond
        imoveis_filtrados = df_imoveis[filtro_final]
    else:
        # Se não houver filtros, retornamos todos os imóveis
        imoveis_filtrados = df_imoveis

    # 4. Converter o resultado para uma lista de dicionários (JSON)
    imoveis_filtrados = imoveis_filtrados.to_dict(orient='records')

    # 5. Verificar se há imóveis filtrados e preparar a resposta
    if imoveis_filtrados:
        resposta = {
            "status": "success",
            "filtros": {
                "tipo_imovel": tipo_imovel if tipo_imovel else "Todos",
                "preco_min": preco_min if preco_min else "Nenhum",
                "preco_max": preco_max if preco_max else "Nenhum",
                "cep": cep if cep else "Nenhum"
            },
            "resultados": {
                "quantidade": len(imoveis_filtrados),
                "imoveis": imoveis_filtrados
            }
        }
        # Retorna a resposta com status 200 (OK)
        return make_response(json.dumps(resposta), 200)
    else:
        # Se nenhum imóvel foi encontrado com os filtros, retornamos uma resposta de erro
        resposta_erro = {
            "status": "no_results",
            "message": "Nenhum imóvel encontrado com os filtros aplicados."
        }
        return make_response(json.dumps(resposta_erro), 404)

# Rodar a aplicação Flask no modo debug
if __name__ == '__main__':
    app.run(debug=True)

