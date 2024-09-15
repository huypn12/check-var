import pymupdf
import re
import pandas as pd

pdf_filepath = "/workspaces/check-var/data/Thong_tin_ung_ho_qua_TSK_VCB_0011001932418_tu_01_09_den10_09_2024.pdf"


class TransactionColumns():
    tx_date = "txdate"
    tx_no = "txno"
    amount = "amount"
    details = "details"


def read_page(page: pymupdf.Page) -> pd.DataFrame:
    text = page.get_text()
    lines = text.split("\n")
    buffer = []
    is_in_table = False
    i = 0
    for l in lines:
        if not is_in_table:
            if is_start_line(l):
                is_in_table = True
            continue
        if is_end_line(l):
            break

        buffer.append(l)
        i += 1

    pre_df = []
    i = 0
    while i < len(buffer):
        j = i + 1
        while j < len(buffer) and not is_date_line(buffer[j]):
            j += 1

        tx_date = buffer[i].lstrip().rstrip()
        tx_no = buffer[i + 1].lstrip().rstrip()
        amount = int(buffer[i + 2].lstrip().rstrip().replace('.', ''))
        details = ''.join(buffer[i + 3:j]).lstrip().rstrip()

        tx = {
            TransactionColumns.tx_date: tx_date,
            TransactionColumns.tx_no: tx_no,
            TransactionColumns.amount: amount,
            TransactionColumns.details: details
        }
        pre_df.append(tx)
        i = j

    df = pd.DataFrame.from_dict(pre_df)

    return df


def read_file(filepath: str):
    frames = []
    with pymupdf.open(filepath) as doc:  # open document
        for page in doc:
            page_df = read_page(page)
            frames.append(page_df)
    df = pd.concat(frames, ignore_index=True)
    df.to_csv("/workspaces/check-var/data/thong_tin_ung_ho.csv")
    df.to_hdf("/workspaces/check-var/data/thong_tin_ung_ho.h5", "df")


def is_date_line(s: str) -> bool:
    datetime_pattern = r'\d{2}/\d{2}/2024'
    return re.match(datetime_pattern, s) is not None


def is_start_line(s: str) -> bool:
    return "Transactions in detail" in s


def is_end_line(s: str) -> bool:
    end_pattern = r'Page\s*\d*\s*of\s*\d*'
    return re.match(end_pattern, s) is not None


read_file(pdf_filepath)
