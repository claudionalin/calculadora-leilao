from flask import Flask, request, jsonify, render_template
from Imóveis import CalculadoraLeilao
import os

app = Flask(__name__)
calculadora = CalculadoraLeilao()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    dados = request.json
    print("Dados recebidos:", dados)
    
    try:
        valor_lance = float(dados['valor_lance'])
        valor_mercado = float(dados['valor_mercado'])
        valor_condominio = float(dados['valor_condominio'])
        meses_ate_venda = int(dados['meses_ate_venda'])
        valor_iptu = float(dados['valor_iptu'])
        
        resultado = calculadora.calcular_viabilidade(
            valor_lance,
            valor_mercado,
            valor_condominio,
            meses_ate_venda,
            valor_iptu,
            dados.get('arrematantes', [])
        )
        
        # Garantir que o valor de mercado está no resultado
        resultado['valor_mercado'] = valor_mercado
        
        # Adicionar pontos para o gráfico
        pontos_vpl = calculadora.calcular_pontos_vpl(
            valor_lance,
            valor_mercado,
            valor_condominio,
            meses_ate_venda,
            valor_iptu
        )
        
        resultado['grafico_vpl'] = pontos_vpl
        
        return jsonify(resultado)
    except Exception as e:
        print(f"Erro no cálculo: {str(e)}")
        return jsonify({'erro': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)  # Modo debug ativado para desenvolvimento 
