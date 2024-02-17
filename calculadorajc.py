import streamlit as st

st.header("Calculadora de Juros Compostos")

capital = st.text_input("Valor Inicial:")
capital = float(capital) if capital else 0.0
juros = st.number_input("Taxa de Juros:", min_value=0.5, step=0.5, format="%g")
tempo = st.number_input("Tempo (ano):", min_value=1, step=1)

montante = capital * (1 + (juros / 100) ** tempo)
valor_juros = montante - capital

st.write(f"**Montante:** R$ {montante:.2f}")
st.write(f"**Valor de juros:** R$ {valor_juros:.2f}")
