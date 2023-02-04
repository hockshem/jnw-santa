import pandas as pd

wish_records = pd.read_csv("./csv_data/wish_records.csv")

prizes = pd.read_csv('./csv_data/prize_pool.csv')

wallets = pd.read_csv("./csv_data/wallets.csv")
merged = wish_records.merge(wallets, how='left', on='Discord ID')

output_dir = './winner_data'

merged = merged.set_index("Item ID").fillna("")
# print(merged)

for i, row in prizes[['Item ID', 'Item Name']].iterrows():
    id, name = row
    merged.loc[[id], ['Discord ID', 'Wallet']].to_csv(f'{output_dir}/{id}_{name}.csv', index=False)

