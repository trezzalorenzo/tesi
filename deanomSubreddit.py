import csv
import re
import pandas as pd
import numpy as np
#reddit_path = "C:\\Users\\loren\\Desktop\\d\\redditaddress.csv"
reddit_path = "./bitcoin_subreddit.csv"
LIST_EXCHANGER = ['huobi', 'bittrex', 'luno', 'poloniex', 'kraken',
                  'btc-e', 'bitzlato', 'bitstamp', 'localbitcoins',
                  'mercadobitcoin', 'cryptsy', 'binance',
                  'cex', 'btctrade', 'yobit', 'okcoin', 'coinspot',
                  'btcc.com', 'bx.in.th', 'hitbtc', 'maicoin', 'bter', 'hashnest',
                  'anxpro', 'bitbay', 'bleutrade', 'bitfinex', 'coinhako',
                  'coinmotion', 'matbea', 'bit-x', 'virwox', 'paxful',
                  'bitbargain', 'spectrocoin', 'cavirtex', 'c-cex',
                  'therocktrading', 'foxbit', 'vircurex', 'bitvc',
                  'exmo', 'btc38', 'igot', 'blocktrades', 'simplecoin',
                  'fybsg', 'campbx', 'cointrader', 'bitcurex', 'coinmate',
                  'korbit', 'vaultoro', 'exchanging', '796.com', 'happycoins',
                  'btcmarkets', 'chbtc', 'coins-e', 'litebit', 'coincafe',
                  'urdubit', 'btradeaustralia', 'mexbt', 'coinomat', 'orderbook',
                  'lakebtc', 'bitkonan', 'quadrigacx', 'banx', 'clevercoin',
                  'gatecoin', 'indacoin', 'coinarch', 'bitcoinvietnam',
                  'coinchimp', 'cryptonit', 'coingi', 'exchange-credit',
                  'bitcoinp2p', 'bitso', 'coinimal', 'empoex', 'ccedk',
                  'usecryptos', 'coinbroker', '1coin.com', 'banx', 'cryptonit',
                  'excangemycoins', 'gatecoin', 'zyado']

LIST_SPECIAL_WORDS = ['hotwallet', 'coldwallet']


# dato il nome di un exchanger torna vero se è presente nel testo
# false altrimenti
# TODO si potrebbe tornare true se è presente nel testo come soggetto...
def exchanger_is_present(text, name_exchanger):
    if text is None or name_exchanger is None:
        return False
    text.lower()
    exchanger = re.search(name_exchanger, text)
    if exchanger is None:
        return False
    else:
        return True


# scorre una lista di exchanger ritorna il primo che si trova nel testo
# TODO: aggiungere logica:cercare di capire quale è l'argomento del post per determinare di quale exchanger si sta parlando
def guess_exchanger(text):
    for i in LIST_EXCHANGER:
        if exchanger_is_present(text, i):
            return i
    return None

def guess_type(text):
    for i in LIST_SPECIAL_WORDS:
        if exchanger_is_present(text, i):
            return i
    return None

def lenghtcsv(path:str):
    returner = 0
    with open(path,newline="",encoding="ISO-8859-1") as filecsv:
        lettore = csv.reader(filecsv,delimiter=";")
        for i in lettore:
            returner = returner+1
    return returner

try:
    df_dean = pd.read_csv("./deanAddressReddit.csv")
except FileNotFoundError:
    df_dean = pd.DataFrame(columns=["Id_Key", "Address", "Titolo", "Testo", "Data", "Exchanger", "Tipo"])

try:
    df_unk = pd.read_csv("./unknownAddressReddit.csv")
except FileNotFoundError:
    df_unk = pd.DataFrame(columns=["Id_Key", "Address", "Titolo", "Testo", "Data"])

with open(reddit_path, newline="", encoding="ISO-8859-1") as filecsv:
    lettore = csv.reader(filecsv,delimiter=",")
    mese = 0
    next(lettore)
    for i in lettore:
        la_data = i[4]
        data = la_data.split(" ")

        try:
            token = data[0].split("-")
        except:
            print(f"errore nel recuper data: {i[4]}")
        nuovo_mese = token[1]
        if nuovo_mese != mese:
            mese = nuovo_mese
            print(f"sono a riga: {i[0]} data:{token[1]}/{token[0]}")
        type = guess_type(i[2])
        if type is None:
            type = guess_type(i[3])

        guessed_exchanger = guess_exchanger(i[2])
        if guessed_exchanger is None:
            guessed_exchanger = guess_exchanger(i[3])

        if guessed_exchanger is None and type is None:
            list_row = [len(df_unk), i[1], i[2], i[3], i[4]]
            df_unk.loc[len(df_unk)] = list_row
        elif guessed_exchanger is not None and type is None:
            list_row = [len(df_dean), i[1], i[2], i[3], i[4], guessed_exchanger, np.nan]
            df_dean.loc[len(df_dean)] = list_row
        elif guessed_exchanger is not None and guessed_exchanger is not None:
            list_row = [len(df_dean), i[1], i[2], i[3], i[4], guessed_exchanger, type]
            df_dean.loc[len(df_dean)] = list_row
df_dean.to_csv('deanAddressReddit.csv', index=False)
df_unk.to_csv('unknownAddressReddit.csv', index=False)

