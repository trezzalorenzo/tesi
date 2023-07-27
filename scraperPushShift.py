# this is an example of loading and iterating over a single file
import re
import zstandard
import os
import json
import sys
from datetime import datetime
import logging.handlers
import pandas as pd

import winsound

def play_beep():
    duration = 500  # Durata del beep in millisecondi
    frequency = 440  # Frequenza del beep in hertz
    winsound.Beep(frequency, duration)

log = logging.getLogger("bot")
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


def find_all(regex: str, text: str):
    match_list = []
    while True:
        match = re.search(regex, text)
        if match:
            match_list.append(match.group(0))
            text = text[match.end():]
        else:
            return match_list

def address_find(text: str):
    if text is not None:
        regex = "(bc1|[13])[a-km-zA-HJ-NP-Z1-9]{25,33}"
        return find_all(regex, text)
    else:
        return []


def read_and_decode(reader, chunk_size, max_window_size, previous_chunk=None, bytes_read=0):
    chunk = reader.read(chunk_size)
    bytes_read += chunk_size
    if previous_chunk is not None:
        chunk = previous_chunk + chunk
    try:
        return chunk.decode()
    except UnicodeDecodeError:
        if bytes_read > max_window_size:
            raise UnicodeError(f"Unable to decode frame after reading {bytes_read:,} bytes")
        log.info(f"Decoding error with {bytes_read:,} bytes, reading another chunk")
        return read_and_decode(reader, chunk_size, max_window_size, chunk, bytes_read)


def read_lines_zst(file_name):
    with open(file_name, 'rb') as file_handle:
        buffer = ''
        reader = zstandard.ZstdDecompressor(max_window_size=2 ** 31).stream_reader(file_handle)
        while True:
            chunk = read_and_decode(reader, 2 ** 27, (2 ** 29) * 2)

            if not chunk:
                break
            lines = (buffer + chunk).split("\n")

            for line in lines[:-1]:
                yield line, file_handle.tell()

            buffer = lines[-1]

        reader.close()


if __name__ == "__main__":

    try:
        dataframe_csv = pd.read_csv("./bitcoin_subreddit.csv")
    except FileNotFoundError:
        dataframe_csv = pd.DataFrame(columns=["Id_Key", "Address", "Titolo", "Testo", "Data"])

    file_path = sys.argv[1]
    file_size = os.stat(file_path).st_size
    file_lines = 0
    file_bytes_processed = 0
    created = None
    field = "subreddit"
    value = "wallstreetbets"
    bad_lines = 0
    # try:
    for line, file_bytes_processed in read_lines_zst(file_path):
        try:
            obj = json.loads(line)
            if obj["subreddit"] == "bitcoin" or obj["subreddit"] == "Bitcoin" :
                address = address_find(obj["selftext"])
                address_nei_titoli = address_find(obj["title"])
                for i in address_nei_titoli:
                    address.append(i)
                if len(address) != 0:
                    for i in address:
                        #"Id_Key", "Address", "Titolo", "Testo", "Data", "Tipo" datetime.datetime.utcfromtimestamp(post['data']['created_utc'])
                        list_row = [len(dataframe_csv), i, obj["title"], obj["selftext"], datetime.utcfromtimestamp(int(obj['created_utc']))]
                        dataframe_csv.loc[len(dataframe_csv)] = list_row
                        #TODO: aggiungere qui il salvataggio in csv
                        print("------")
                        print(i)
            created = datetime.utcfromtimestamp(int(obj['created_utc']))
            temp = obj[field] == value
        except (KeyError, json.JSONDecodeError) as err:
            bad_lines += 1
        file_lines += 1
        if file_lines % 100000 == 0:
            log.info(
                f"{created.strftime('%Y-%m-%d %H:%M:%S')} : {file_lines:,} : {bad_lines:,} : {file_bytes_processed:,}:{(file_bytes_processed / file_size) * 100:.0f}%")
    dataframe_csv.to_csv('bitcoin_subreddit.csv', index=False)
    # except Exception as err:
    # 	log.info(err)

    log.info(f"Complete : {file_lines:,} : {bad_lines:,}")
    play_beep()
