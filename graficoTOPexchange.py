import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# Leggi il file CSV utilizzando Pandas
df = pd.read_csv("C:\\Users\\loren\\Desktop\\Address\\marged\\final.csv")
# Conta il numero di occorrenze dei valori nella colonna "exchanger"
exchange_counts = df['Exchanger'].value_counts()
print(exchange_counts)
exchange_percentages = exchange_counts / len(df) * 100
threshold = 1.5
exchange_counts_filtered = exchange_counts[exchange_percentages >= threshold]
#exchange_counts_filtered['Altro'] = exchange_counts[exchange_percentages < threshold].sum()
plt.figure(figsize=(8, 6))
plt.bar(exchange_counts_filtered.index, exchange_counts_filtered)
plt.yscale('log')  # Aggiungi scala logaritmica all'asse y se necessario
plt.xlabel('Exchange')
plt.ylabel('Address')
plt.title('Classifica exchange per numero di address')
plt.xticks(rotation=45, ha='right', fontsize=8)  # Imposta la rotazione, allineamento orizzontale e dimensione del testo delle etichette
plt.tight_layout()  # Aggiungi questo comando per gestire il layout e prevenire sovrapposizioni
plt.subplots_adjust(top=0.85)
plt.show()



