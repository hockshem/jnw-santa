from discord import Interaction
from discord.ui import Modal, TextInput
import pandas as pd

class WalletSubmitForm(Modal, title='提交钱包 🧧'):
    wallet_address = TextInput(
        label='钱包地址',
        placeholder='所有本次活动抽中的白名单将默认使用这个钱包地址'
    )

    async def on_submit(self, interaction: Interaction):
        user_id = interaction.user.id
        wallet_address = self.wallet_address.value
        _add_wallet(user_id, wallet_address)
        await interaction.response.send_message(f"<@{user_id}>，钱包地址更新成功！🎉 ")

wallet_df = pd.read_csv("./csv_data/wallets.csv")

def _add_wallet(user_id, wallet):
    global wallet_df
    
    if wallet_df.loc[wallet_df["Discord ID"] == user_id, "Wallet"].count() > 0:
        wallet_df.loc[wallet_df["Discord ID"] == user_id, "Wallet"] = wallet
    else:
        new_df = pd.Series([user_id, wallet], index=wallet_df.columns).to_frame().T
        wallet_df = pd.concat([wallet_df, new_df], ignore_index=True)
    
    _flush_wallets_data()

def _flush_wallets_data():
    wallet_df.to_csv("./csv_data/wallets.csv", index=False)