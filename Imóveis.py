import numpy as np
import numpy_financial as npf
from datetime import datetime, timedelta

class CalculadoraLeilao:
    def __init__(self):
        self.valor_lance = 0
        self.valor_mercado = 0
        self.meses_ate_venda = 0
        self.taxa_selic = 0.1375  # Taxa Selic atual (13,75% ao ano)
        
    def calcular_custos_totais(self, valor_lance, valor_mercado, valor_condominio, meses_ate_venda, valor_iptu):
        """Calcula todos os custos envolvidos na aquisição do imóvel em leilão"""
        self.valor_lance = valor_lance
        self.valor_mercado = valor_mercado
        self.meses_ate_venda = meses_ate_venda
        
        # Custos principais
        custos = {
            'lance': valor_lance,
            'comissao_leiloeiro': self._calcular_comissao_leiloeiro(),
            'custas_cartorio': self._calcular_custas_cartorio(),
            'itbi': self._calcular_itbi(),
            'regularizacao': self._calcular_custos_regularizacao(),
            'advogado': self._calcular_honorarios_advogado(),
            'vistoria': 1500.00,  # Valor médio para vistoria técnica
            'condominio': self._calcular_custos_condominio(valor_condominio),
            'iptu': self._calcular_custos_iptu(valor_iptu)  # Novo custo de IPTU
        }
        
        return custos
    
    def _calcular_comissao_leiloeiro(self):
        """Comissão padrão do leiloeiro (5%)"""
        return self.valor_lance * 0.05
    
    def _calcular_custas_cartorio(self):
        """Custas aproximadas de cartório"""
        # Valor base para registro, escritura e certidões
        return 3500.00
    
    def _calcular_itbi(self):
        """Imposto de Transmissão de Bens Imóveis (2-3%)"""
        return self.valor_lance * 0.03
    
    def _calcular_custos_regularizacao(self):
        """Custos estimados para regularização"""
        return 5000.00  # Valor base para possíveis regularizações
    
    def _calcular_honorarios_advogado(self):
        """Honorários advocatícios estimados"""
        return 5000.00  # Valor base para assessoria jurídica
    
    def _calcular_custos_condominio(self, valor_condominio):
        """Calcula o custo total do condomínio durante o período de espera"""
        return valor_condominio * self.meses_ate_venda
    
    def _calcular_vpl(self, fluxo_caixa, taxa_mensal):
        """Calcula o Valor Presente Líquido"""
        return npf.npv(taxa_mensal, fluxo_caixa)
    
    def _calcular_tir(self, fluxo_caixa):
        """Calcula a Taxa Interna de Retorno"""
        try:
            return npf.irr(fluxo_caixa)
        except:
            return None
    
    def _calcular_payback(self, fluxo_caixa):
        """Calcula o período de payback simples"""
        saldo_acumulado = 0
        for i, valor in enumerate(fluxo_caixa):
            saldo_acumulado += valor
            if saldo_acumulado >= 0:
                return i
        return None
    
    def _calcular_custos_iptu(self, valor_iptu):
        """Calcula o custo total do IPTU durante o período de espera"""
        return valor_iptu * self.meses_ate_venda
    
    def calcular_viabilidade(self, valor_lance, valor_mercado, valor_condominio, meses_ate_venda, valor_iptu, arrematantes=None):
        """Analisa a viabilidade do negócio"""
        custos = self.calcular_custos_totais(valor_lance, valor_mercado, valor_condominio, meses_ate_venda, valor_iptu)
        custo_total = sum(custos.values())
        
        # Cálculo do lucro líquido
        lucro_bruto = valor_mercado - custo_total
        imposto_ganho_capital = lucro_bruto * 0.15 if lucro_bruto > 0 else 0
        lucro_liquido = lucro_bruto - imposto_ganho_capital
        
        # Novos indicadores de eficiência
        margem_liquida = (lucro_liquido / valor_mercado) * 100 if valor_mercado > 0 else 0
        retorno_sobre_custo = (lucro_liquido / custo_total) * 100 if custo_total > 0 else 0
        
        # Cálculo da rentabilidade
        rentabilidade = (lucro_liquido / custo_total) * 100 if custo_total > 0 else 0
        
        # Preparação do fluxo de caixa mensal
        taxa_mensal = (1 + self.taxa_selic) ** (1/12) - 1
        
        # Fluxo de caixa considerando:
        # Mês 0: Investimento inicial (custos totais)
        # Meses 1 a n-1: Pagamentos de condomínio e IPTU mensal
        fluxo_caixa = [-custo_total]
        for _ in range(meses_ate_venda - 1):
            fluxo_caixa.append(-(valor_condominio + (valor_iptu/12)))
        fluxo_caixa.append(valor_mercado - imposto_ganho_capital)
        
        # Cálculos financeiros avançados
        vpl = self._calcular_vpl(fluxo_caixa, taxa_mensal)
        tir_mensal = self._calcular_tir(fluxo_caixa)
        tir_anual = (1 + tir_mensal) ** 12 - 1 if tir_mensal else None
        payback = self._calcular_payback(fluxo_caixa)
        
        roi = (lucro_liquido / custo_total) * 100 if custo_total > 0 else 0
        
        # Cálculo por arrematante
        resultados_arrematantes = []
        if arrematantes:
            for arr in arrematantes:
                participacao = arr['participacao'] / 100
                
                # Cálculo do investimento (participação em todos os custos)
                investimento_lance = valor_lance * participacao
                outros_custos = (custo_total - valor_lance) * participacao
                investimento_total = investimento_lance + outros_custos
                
                # Cálculo do retorno (participação no valor de mercado menos impostos)
                retorno_bruto = valor_mercado * participacao
                imposto_proporcional = imposto_ganho_capital * participacao
                retorno_liquido = retorno_bruto - imposto_proporcional
                
                # Cálculo do lucro individual
                lucro_individual = retorno_liquido - investimento_total
                
                # Cálculo do ROI individual
                roi_individual = (lucro_individual / investimento_total * 100) if investimento_total > 0 else 0
                
                resultados_arrematantes.append({
                    'id': arr['id'],
                    'participacao': arr['participacao'],
                    'investimento_lance': investimento_lance,
                    'outros_custos': outros_custos,
                    'investimento_total': investimento_total,
                    'retorno_bruto': retorno_bruto,
                    'imposto': imposto_proporcional,
                    'retorno_liquido': retorno_liquido,
                    'lucro': lucro_individual,
                    'roi': roi_individual
                })
        
        return {
            'custo_total': custo_total,
            'lucro_bruto': lucro_bruto,
            'imposto_ganho_capital': imposto_ganho_capital,
            'lucro_liquido': lucro_liquido,
            'rentabilidade': rentabilidade,
            'vpl': vpl,
            'tir_mensal': tir_mensal,
            'tir_anual': tir_anual,
            'payback': payback,
            'roi': roi,
            'margem_liquida': margem_liquida,
            'retorno_sobre_custo': retorno_sobre_custo,
            'detalhamento_custos': custos,
            'resultados_arrematantes': resultados_arrematantes
        }

    def calcular_pontos_vpl(self, valor_lance_base, valor_mercado, valor_condominio, meses_ate_venda, valor_iptu):
        """Calcula pontos para o gráfico do VPL"""
        pontos = []
        # Calcula VPL para valores de lance de 50% a 150% do valor base
        for percentual in range(50, 151, 5):  # De 50% a 150% em steps de 5%
            valor_lance_temp = valor_lance_base * (percentual / 100)
            resultado = self.calcular_viabilidade(
                valor_lance_temp,
                valor_mercado,
                valor_condominio,
                meses_ate_venda,
                valor_iptu
            )
            pontos.append({
                'valor_lance': valor_lance_temp,
                'vpl': resultado['vpl']
            })
        
        # Encontrar o ponto onde VPL = 0 (interpolação linear)
        ponto_zero = None
        for i in range(len(pontos)-1):
            if (pontos[i]['vpl'] >= 0 and pontos[i+1]['vpl'] <= 0) or \
               (pontos[i]['vpl'] <= 0 and pontos[i+1]['vpl'] >= 0):
                # Interpolação linear
                x1, y1 = pontos[i]['valor_lance'], pontos[i]['vpl']
                x2, y2 = pontos[i+1]['valor_lance'], pontos[i+1]['vpl']
                # Fórmula: x = x1 + (0 - y1) * (x2 - x1) / (y2 - y1)
                valor_lance_zero = x1 + (0 - y1) * (x2 - x1) / (y2 - y1)
                ponto_zero = {
                    'valor_lance': valor_lance_zero,
                    'vpl': 0
                }
                break
        
        return {
            'pontos': pontos,
            'ponto_zero': ponto_zero
        }

def exibir_cabecalho():
    print("\n" + "=" * 50)
    print("CALCULADORA DE VIABILIDADE PARA LEILÃO DE IMÓVEIS")
    print("=" * 50 + "\n")

def obter_input_numerico(mensagem, tipo_numero='float'):
    """
    Obtém input numérico do usuário
    tipo_numero: 'float' ou 'int' para especificar o tipo de número esperado
    """
    while True:
        try:
            valor = float(input(mensagem))
            if valor < 0:
                print("Por favor, insira um valor positivo.")
                continue
            return int(valor) if tipo_numero == 'int' else valor
        except ValueError:
            print("Por favor, insira um valor numérico válido.")

def formatar_porcentagem(valor):
    """Formata um valor como porcentagem"""
    return f"{valor:.2f}%" if valor is not None else "N/A"

def formatar_meses(valor):
    """Formata o número de meses"""
    if valor is None:
        return "N/A"
    return f"{valor:.1f} meses"

def exibir_resultados(resultado):
    """Exibe os resultados da análise de forma organizada"""
    
    def print_secao(titulo):
        print("\n" + "=" * 50)
        print(titulo.center(50))
        print("=" * 50)
    
    def print_indicador(label, valor, formato="R$ {:,.2f}"):
        print(f"{label:<30} {formato.format(valor) if valor is not None else 'N/A'}")
    
    # Resumo do Investimento
    print_secao("RESUMO DO INVESTIMENTO")
    print_indicador("Valor do Lance:", resultado['detalhamento_custos']['lance'])
    print_indicador("Valor de Mercado:", resultado['valor_mercado'])
    
    # Custos e Resultados
    print_secao("CUSTOS E RESULTADOS")
    print_indicador("Custo Total:", resultado['custo_total'])
    print_indicador("Lucro Bruto:", resultado['lucro_bruto'])
    print_indicador("Imposto (Ganho Capital):", resultado['imposto_ganho_capital'])
    print_indicador("Lucro Líquido:", resultado['lucro_liquido'])
    
    # Indicadores de Rentabilidade
    print_secao("INDICADORES DE RENTABILIDADE")
    print_indicador("ROI (Retorno sobre Investimento):", resultado['roi'], "{:.2f}%")
    print_indicador("VPL (Valor Presente Líquido):", resultado['vpl'])
    if resultado['tir_mensal']:
        print_indicador("TIR Mensal:", resultado['tir_mensal'] * 100, "{:.2f}%")
        print_indicador("TIR Anual:", resultado['tir_anual'] * 100, "{:.2f}%")
    else:
        print_indicador("TIR Mensal:", None)
        print_indicador("TIR Anual:", None)
    print_indicador("Tempo de Payback:", resultado['payback'], "{:.1f} meses")
    
    # Detalhamento dos Custos
    print_secao("DETALHAMENTO DOS CUSTOS")
    for item, valor in resultado['detalhamento_custos'].items():
        nome_item = item.replace('_', ' ').title()
        print_indicador(nome_item + ":", valor)
    
    # Análise de Viabilidade
    print_secao("ANÁLISE DE VIABILIDADE")
    vpl_status = "POSITIVO ✓" if resultado['vpl'] > 0 else "NEGATIVO ✗"
    roi_status = "BOM ✓" if resultado['roi'] > 15 else "BAIXO ✗"
    
    print(f"\nVPL: {vpl_status}")
    print(f"ROI: {roi_status}")
    
    # Recomendação
    print("\nRECOMENDAÇÃO:")
    if resultado['vpl'] > 0 and resultado['roi'] > 15:
        print("✓ Investimento recomendado - Bons indicadores de retorno")
    elif resultado['vpl'] > 0:
        print("⚠ Investimento possível - Retorno positivo, mas considere outras opções")
    else:
        print("✗ Investimento não recomendado - Indicadores desfavoráveis")

def main():
    calc = CalculadoraLeilao()
    
    exibir_cabecalho()
    
    valor_lance = obter_input_numerico("Digite o valor do lance pretendido (R$): ")
    valor_mercado = obter_input_numerico("Digite o valor de mercado do imóvel (R$): ")
    valor_condominio = obter_input_numerico("Digite o valor mensal do condomínio (R$): ")
    valor_iptu = obter_input_numerico("Digite o valor anual do IPTU (R$): ")
    meses_ate_venda = obter_input_numerico("Digite o tempo estimado até a venda (meses): ", tipo_numero='int')
    
    resultado = calc.calcular_viabilidade(valor_lance, valor_mercado, valor_condominio, meses_ate_venda, valor_iptu)
    resultado['valor_mercado'] = valor_mercado
    
    exibir_resultados(resultado)

if __name__ == "__main__":
    main()
