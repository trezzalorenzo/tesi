import re
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


class Post:
    def __init__(self, testo: str, data: str):
        self.testo = testo
        self.data = data

    def get_testo(self):
        return self.testo

    def get_data(self):
        return self.data


# header per HTTP get per sembrare un umano e non un bot
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)'
                         'AppleWebKit 537.36 (KHTML, like Gecko) Chrome',
           'Accept': 'text/html,application/xhtml+xml,application/xml;'
                     'q=0.9,image/webp,*/*;q=0.8'}

LIST_EXCHANGER = ['huobi', 'bittrex', 'luno', 'poloniex', 'kraken',
                  'btc-e', 'bitzlato', 'bitstamp', 'localbitcoins',
                  'mercadobitcoin', 'cryptsy', 'binance',
                  'cex', 'btctrade', 'yobit', 'okcoin', 'coinspot',
                  'btcc', 'bx', 'hitbtc', 'maicoin', 'bter', 'hashnest',
                  'anxpro', 'bitbay', 'bleutrade', 'bitfinex', 'coinhako',
                  'coinmotion', 'matbea', 'bit-x', 'virwox', 'paxful',
                  'bitbargain', 'spectrocoin', 'cavirtex', 'c-cex',
                  'therocktrading', 'foxbit', 'vircurex', 'bitvc',
                  'exmo', 'btc38', 'igot', 'blocktrades', 'simplecoin',
                  'fybsg', 'campbx', 'cointrader', 'bitcurex', 'coinmate',
                  'korbit', 'vaultoro', 'exchanging', '796', 'happycoins',
                  'btcmarkets', 'chbtc', 'coins-e', 'litebit', 'coincafe',
                  'urdubit', 'btradeaustralia', 'mexbt', 'coinomat', 'orderbook',
                  'lakebtc', 'bitkonan', 'quadrigacx', 'banx', 'clevercoin',
                  'gatecoin', 'indacoin', 'coinarch', 'bitcoinvietnam',
                  'coinchimp', 'cryptonit', 'coingi', 'exchange-credit',
                  'bitcoinp2p', 'bitso', 'coinimal', 'empoex', 'ccedk',
                  'usecryptos', 'coinbroker']
# pagina iniziale

# TODO: da cambiare con https://bitcointalk.org/index.php
# URL = "https://bitcointalk.org/index.php?topic=78"
URL = "https://bitcointalk.org/index.php?topic=215.0"


# dato il riferimento ad un post ritorna la data,None se la data non è reperibile
def extract_date(post: BeautifulSoup):
    try:
        return post.parent.find('div', {'class': 'smalltext'}).getText()
    except:
        return None


# ritorna una lista oggetti di tipo Post
# o lista vuota altrimenti
def post_extract(page_source):
    date = None
    list_posts = []
    cosa_trovo = page_source.find_all('div', {'class': 'post'})
    for i in cosa_trovo:
        try:
            quoteheader = i.find('div', {'class': 'quoteheader'})
            quote = i.find('div', {'class': 'quote'})
            quoteheader.extract()
            quote.extract()
            date = extract_date(i)
        except:
            pass
        list_posts.append(Post(i.getText(), date))
    return list_posts


# TODO: la uso mai?
# elimina gli spazi bianchi
def is_blank(my_string: str):
    return not (my_string and my_string.strip())


# ritorna la lista di tutti gli elementi che rispettano la regex
# o lista vuota
def find_all(regex: str, text: str):
    match_list = []
    while True:
        match = re.search(regex, text)
        if match:
            match_list.append(match.group(0))
            text = text[match.end():]
        else:
            return match_list


# ritorna la lista di tutti gli address bitcoin presenti nel testo
# o lista vuota
def address_find(text: str):
    if text is not None:
        regex = "(bc1|[13])[a-km-zA-HJ-NP-Z1-9]{25,33}"
        return find_all(regex, text)
    else:
        return []


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


# cerca gli address e li salva in un csv cercando di capire a quale exchanger si riferiscono
# ritorna True se riesce con successo ad analizzare i post all'interno del topic
# False altrimenti
def scrape_topic_page(page_source, current_url):
    try:
        dataframe_csv = pd.read_csv("./BitcoinTalk.csv")
    except FileNotFoundError:
        dataframe_csv = pd.DataFrame(columns=["Id_Key", "Address", "Url", "Guessed_exchanger", "Post", "Data_post"])

    if page_source is None or dataframe_csv is None or current_url is None:
        return False
    list_post = post_extract(page_source)
    if len(list_post) == 0:
        return False
    # per ogni post trovato
    for i in list_post:
        # di prova
        coso = i.get_testo()
        address = address_find(i.get_testo())
        if len(address) == 0:
            continue
        else:
            guessed_exchanger = guess_exchanger(i.get_testo())
            if guessed_exchanger is not None:
                for j in address:
                    if i.get_data() is not None:
                        list_row = [len(dataframe_csv), j, current_url, guessed_exchanger, i.get_testo(),
                                    i.get_data().replace(",", "")]
                    else:
                        list_row = [len(dataframe_csv), j, current_url, guessed_exchanger, i.get_testo(), np.nan]
                    dataframe_csv.loc[len(dataframe_csv)] = list_row
            elif guessed_exchanger is None:
                for j in address:
                    if i.get_data() is not None:
                        list_row = [len(dataframe_csv), j, current_url, np.nan, i.get_testo(),
                                    i.get_data().replace(",", "")]
                    else:
                        list_row = [len(dataframe_csv), j, current_url, np.nan, i.get_testo(), np.nan]
                    dataframe_csv.loc[len(dataframe_csv)] = list_row
    try:
        dataframe_csv.to_csv('BitcoinTalk.csv', index=False)
    finally:
        return True


# cerca il link associato all' elemento » che porta alla pagina successiva del topic
# ritorna il link alla prossima pagine
# la stringa "" altimenti
def find_next_page(page_source):
    pages = page_source.find_all('a', {'class': 'navPages'})
    next_page = ""
    for i in pages:
        if i.getText() == "»":
            next_page = i
    if next_page == "":
        return ""
    else:
        return next_page.attrs['href']


# passando il link alla prima pagina dei un topic si occupa di ricercare gli address e li salva in un csv
# ritorna
def scrape_all_pages_topic(sessione, topic_url):
    check = 0
    # accedo al topic
    req = sessione.get(topic_url, headers=HEADERS)
    bs = BeautifulSoup(req.text, 'html.parser')
    scrape_topic_page(bs, topic_url)
    while check == 0:
        # cerco la prossima pagina su cui fare scraping
        next_page = find_next_page(bs)
        # se ho ultimato esco dal ciclo
        if next_page == "":
            check = 1
        else:
            # accedo alla prossima pagina e effetto lo scraping
            req = sessione.get(next_page, headers=HEADERS)
            bs = BeautifulSoup(req.text, 'html.parser')
            scrape_topic_page(bs, next_page)


# data una board ricava tutti i link ai topic
def find_all_topic(url: str, session):
    req = session.get(url, headers=HEADERS)
    bs = BeautifulSoup(req.text, 'html.parser')
    links = bs.find_all('a')
    link_epurati = []
    for i in links:
        try:
            if re.search("topic=", i.attrs['href']):
                if i.getText().isnumeric() or i == "All" or re.search("new$", i.attrs["href"]) or re.search("all$",
                                                                                                            i.attrs[
                                                                                                                "href"]):
                    continue
                else:
                    link_epurati.append(i.attrs['href'])
            else:
                continue
        except:
            pass
    return link_epurati


def scrape_all_topic(list_topic_link, session):
    j = 0
    for i in list_topic_link:
        j = j + 1
        print(f"{j}analizzo: {i}")
        scrape_all_pages_topic(session, i)
        time.sleep(5)


# data la pagine https://bitcointalk.org/index.php?board=1.0 analizza tutti i topic presenti
def scrape_board(url_board, session):
    url_parts = url_board.split(".")
    url_without_number = ".".join(url_parts[:-1])
    while True:
        i = 0
        try:
            scrape_all_topic(url_without_number.__add__(str(i)), session)
        except:
            break
        i = i + 40


def find_all_board():
    session = requests.Session()
    url_home = "https://bitcointalk.org/index.php"
    req = session.get(url_home, headers=HEADERS)
    bs = BeautifulSoup(req.text, 'html.parser')
    links = bs.find_all('a')
    link_epurati = []
    for i in links:
        try:
            if re.search("board=", i.attrs['href']):
                if re.search("unread", i.attrs['href']):
                    continue
                else:
                    if link_epurati.__contains__(i.attrs['href']):
                        continue
                    else:
                        link_epurati.append(i.attrs['href'])
            else:
                continue
        except:
            pass
    return link_epurati


def scrape_bitcoin_talk():
    session = requests.Session()
    for i in find_all_board():
        scrape_board(i, session)

topics = find_all_topic("https://bitcointalk.org/index.php?board=1.57680", session)
scrape_all_topic(topics, session)

