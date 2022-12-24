import pandas as pd
import numpy as np
import time

from member_points import get_pts_bal, decrease_pts

prize_pool_df = pd.read_csv("./csv_data/prize_pool.csv", index_col="Tier")
prize_pool_df = prize_pool_df.fillna("")
# print(prize_df)


wish_req_df = pd.read_csv("./csv_data/wish_info.csv", index_col="Tier")
wish_req_df = wish_req_df.fillna(0)
wish_req_df["Required Role"] = wish_req_df["Required Role"].astype(np.int64)
# print(wish_req_df)

wish_records_df = pd.read_csv("./csv_data/wish_records.csv")
wish_records_df = wish_records_df.fillna("")
# print(wish_records_df)

def is_wishable(user_id, user_roles, tier):
    cost = wish_req_df.loc[tier, "Cost"]
    req_role = wish_req_df.loc[tier, "Required Role"]
    user_bal = get_pts_bal(user_id)

    if req_role not in user_roles or cost > user_bal: 
        return False

    return True

def get_prize_name(item_id):
    return prize_pool_df.loc[prize_pool_df["Item ID"] == item_id, "Item Name"].values[0]

def claim_gift_exchange(user_id, user_roles):
    pass

def premium_wish(user_id, user_roles):
    if is_wishable(user_id, user_roles, 1):
        wish_result = _wish(1)
        prize_name = get_prize_name(wish_result)

        cost = wish_req_df.loc[1, "Cost"]
        decrease_pts(user_id, cost)
        update_wish_record(user_id, wish_result, prize_name)
        update_prize_pool(wish_result, -1)
        
        return {
            "Prize ID": wish_result,
            "Prize Name": prize_name
        }

    return None
    

def standard_wish(user_id, user_roles):
    if is_wishable(user_id, user_roles, 2):
        wish_result = _wish(2)
        prize_name = get_prize_name(wish_result)

        cost = wish_req_df.loc[2, "Cost"]
        decrease_pts(user_id, cost)
        update_wish_record(user_id, wish_result, prize_name)

        if not str(prize_name).lower() == "nothing":
            update_prize_pool(wish_result, -1)

        return {
            "Prize ID": wish_result,
            "Prize Name": prize_name
        }

    return None

def _wish(tier):
    tiered_prize_pool = []

    rng = np.random.default_rng()
    rand_int = rng.integers(1, 100, endpoint=True)
    
    if tier == 1:
        if rand_int <= 25:
            tier = 2
    elif tier == 2:
        if rand_int > 95:
            tier = 1
        elif rand_int <= 25:
            tier = 3

    if len(prize_pool_df.loc[tier].shape) > 1:
        for item, remaining in zip(prize_pool_df.loc[tier, "Item ID"], prize_pool_df.loc[tier, "Remaining"]):
            tiered_prize_pool += [item] * remaining
    else: 
        tiered_prize_pool = [prize_pool_df.loc[tier, "Item ID"]]

    wish_result_id = rng.choice(tiered_prize_pool)
    
    return wish_result_id
    

def update_prize_pool(item_id, amount):
    prize_pool_df.loc[prize_pool_df["Item ID"] == item_id, "Remaining"] += amount
    _flush_prize_pool_data()

def update_wish_record(user_id, item_id, item_name):
    global wish_records_df
    timestamp = time.time()
    # TODO: add contributor
    print([timestamp, user_id, item_id, item_name, "", ""])
    new_df = pd.Series([timestamp, user_id, item_id, item_name, "", ""], index=wish_records_df.columns).to_frame().T
    print(new_df)
    wish_records_df = pd.concat([wish_records_df, new_df], ignore_index=True)
    _flush_wish_records()

def _flush_prize_pool_data():
    new_prize_pool = prize_pool_df.reset_index(names="Tier")
    new_prize_pool.to_csv("./csv_data/prize_pool.csv", index=False)

def _flush_wish_records():
    wish_records_df.to_csv("./csv_data/wish_records.csv", index=False)

# TODO: add handling when the prize pool has nothing else
# print(standard_wish(955688670428549120, [1027076134669660190, 1049961153712889856]))
# print(premium_wish(955688670428549120, [1027076134669660190, 1049961153712889856]))
# print(wish_records_df)
