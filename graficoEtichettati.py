import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("C:\\Users\\loren\\Desktop\\Address\\marged\\final.csv")

# Calcola il numero di valori NaN e non-NaN nella colonna 'Exchange'
nan_count = df['Exchanger'].isnull().sum()
non_nan_count = df['Exchanger'].notnull().sum()

# Crea il grafico a torta
labels = ['Non etichettati', 'Etichettati']
sizes = [nan_count, non_nan_count]
plt.pie(sizes, labels=labels, autopct='%1.1f%%')

# Imposta opzioni aggiuntive
plt.axis('equal')
plt.title('Valori etichettati')

# Mostra il grafico
plt.show()