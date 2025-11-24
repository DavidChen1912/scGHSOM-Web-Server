import pandas as pd
import csv
import numpy as np

def format_ghsom_input_vector(name, file, index, label, subnum):
    """
    name : dataset name (string)
    file : application folder name (data-t1-t2)
    index : user-provided index column (string or None)
    label : user-provided label column (string or None)
    subnum : subsample number (int or None)
    """

    print(subnum)

    # ============================
    # 讀 raw-data（新版）
    # ============================
    df = pd.read_csv(f'./raw-data/{name}.csv', encoding='utf-8')

    # ============================
    # 補 NA → 0（保持舊版邏輯）
    # ============================
    df = df.fillna(0)

    # ============================
    # Subsample（舊版一致）
    # ============================
    if subnum is not None:
        df = df.sample(n=subnum)

    # ============================
    # 處理 index（使用者有填才 drop）
    # ============================
    if index is not None and index in df.columns:
        print(f"[INFO] Dropping index column: {index}")
        df = df.drop(columns=[index])

    # ============================
    # 處理 label（使用者有填才 drop）
    # ============================
    if label is not None and label in df.columns:
        print(f"[INFO] Dropping label column: {label}")
        df = df.drop(columns=[label])

    # ============================
    # printing info（舊版格式）
    # ============================
    rows_amount = df.shape[0]
    columns_amount = df.shape[1]
    df[index] = range(0,rows_amount)

    print('rows=', rows_amount)
    print('columns=', columns_amount)

    # ============================
    # 寫出 GHSOM input CSV（完全照舊版）
    # ============================
    ghsom_csv_path = f'./applications/{file}/GHSOM/data/{name}_ghsom.csv'
    df.to_csv(ghsom_csv_path, sep=' ', index=False, header=False)

    # ============================
    # 寫出 .in 檔（完全照舊版）
    # ============================
    ghsom_in_path = f'./applications/{file}/GHSOM/data/{name}_ghsom.in'

    data_type = 'inputvec'
    x_dim = rows_amount
    y_dim = 1
    vec_dim = columns_amount

    with open(ghsom_in_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([f'$TYPE {data_type}'])
        writer.writerow([f'$XDIM {x_dim}'])
        writer.writerow([f'$YDIM {y_dim}'])
        writer.writerow([f'$VECDIM {vec_dim}'])

        with open(ghsom_csv_path, 'r', newline='', encoding='utf-8') as rawfile:
            rows = csv.reader(rawfile)
            writer.writerow([])

            for row in rows:
                writer.writerow(row)
        

    print("[OK] GHSOM input formatting completed (final version).")










