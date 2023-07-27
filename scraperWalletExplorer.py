from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
import pandas as pd
import datetime

WALLET_EXPLORER = "https://www.walletexplorer.com/"


# recupera gli url agli exchanger
# ritorna None nel caso altrimenti
def get_name_exchanger():
    # avvio il driver
    driver = webdriver.Chrome()
    try:
        # http get alla pagina iniziale del sito
        driver.get(WALLET_EXPLORER)
        exchanger = []
        # recupero i tag 'a' presenti nella colonna "Exchanger"
        li = driver.find_elements(By.XPATH, '/html/body/div[2]/table/tbody/tr/td[1]/ul/li/a')
        # salvo nella lista exchanger i link agli exchanger
        for i in li:
            exchanger.append(i.get_attribute("href"))
        return exchanger
    except:
        return None
    finally:
        # chiudo il driver
        driver.close()


# recupera tutti gli address di tutti gli exchanger salvandoli in un file csv
# prametro sleep_time per impostare l'intervallo di tempo tra due http get
def scrape_walletexplorer(sleep_time: int):
    data_attuale = datetime.datetime.now()
    data_formattata = data_attuale.strftime("%m/%d/%Y")
    address = []
    driver = webdriver.Chrome()
    # apro il csv in cui salvare le informazioni se non esiste ne crea uno nuovo
    try:
        df = pd.read_csv("./WalletExplorerAddress.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Id_Key", "Exchanger", "Address", "Date"])
    # recupero il link a tutti gli exchanger
    link_exchanger = get_name_exchanger()
    for i in link_exchanger:
        time.sleep(sleep_time)
        # accedo alla pagina relativa agli address dell'exchanger
        try:
            driver.get(i.__add__("/addresses"))
        except:
            print("errore nell'accesso alla pagine degli address")
        while True:
            try:
                address = driver.find_elements(By.XPATH, '//a[contains(@href, "/addresses/")]')
            except:
                break
            for j in address:
                list_row = [len(df), string.split("/")[-1].replace(".", "_"), j.text, data_formattata]
                df.loc[len(df)] = list_row
            try:
                driver.find_element(By.XPATH, '//a[text()="Next…"]').click()
            except:
                try:
                    driver.find_element(By.XPATH, '//a[text()="Last"]').click()
                except:
                    break
    df.to_csv('WalletExplorerAddress.csv', index=False)


if __name__ == "__main__":
    if sys.argv[1] > 0:
        scrape_walletexplorer(sys.argv[1])
    else:
        scrape_walletexplorer(10)
