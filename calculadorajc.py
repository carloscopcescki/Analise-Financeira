import streamlit as st

def calcular_juros_compostos(capital, taxa_juros, tempo_anos, aporte_mensal):
    meses = tempo_anos * 12
    montante = capital
    for _ in range(meses):
        montante *= 1 + (taxa_juros / 100) / 12
        montante += aporte_mensal
    valor_juros_total = montante - capital - (aporte_mensal * meses)
    return montante, valor_juros_total

st.header("Calculadora de Juros Compostos com Aporte Mensal")

capital = st.number_input("Valor Inicial:", min_value=0.0)
taxa_juros = st.number_input("Taxa de Juros (ao ano):", min_value=0.0, step=0.5, format="%g")
tempo_anos = st.number_input("Tempo (anos):", min_value=1, step=1)
aporte_mensal = st.number_input("Aporte Mensal:", min_value=0.0)

if st.button("Calcular"):
    montante_final, valor_juros_total = calcular_juros_compostos(capital, taxa_juros, tempo_anos, aporte_mensal)
    st.write(f"**Montante Final:** R$ {montante_final:.2f}")
    st.write(f"**Valor Total de Juros:** R$ {valor_juros_total:.2f}")