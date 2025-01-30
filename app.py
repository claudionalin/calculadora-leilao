from flask import Flask, render_template, request, jsonify
from Imóveis import CalculadoraLeilao
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        dados = request.get_json()
        
        calc = CalculadoraLeilao()
        resultado = calc.calcular_viabilidade(
            float(dados['valor_lance']),
            float(dados['valor_mercado']),
            float(dados['valor_condominio']),
            int(dados['meses_ate_venda'])
        )
        
        resultado['valor_mercado'] = float(dados['valor_mercado'])
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 
