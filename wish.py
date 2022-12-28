import pandas as pd
import numpy as np
import time

from member_points import get_pts_bal, decrease_pts

# TODO: add handling when the prize pool has nothing else

prize_pool_df = pd.read_csv("./csv_data/prize_pool.csv", index_col="Tier")
prize_pool_df = prize_pool_df.fillna("")

wish_req_df = pd.read_csv("./csv_data/wish_info.csv", index_col="Tier")
wish_req_df = wish_req_df.fillna(0)
wish_req_df["Required Role"] = wish_req_df["Required Role"].astype(np.int64)

wish_records_df = pd.read_csv("./csv_data/wish_records.csv")
wish_records_df = wish_records_df.fillna("")

def is_wishable(user_id, user_roles, tier):
    cost = wish_req_df.loc[tier, "Cost"]
    req_role = wish_req_df.loc[tier, "Required Role"]
    user_bal = get_pts_bal(user_id)

    if req_role not in user_roles or cost > user_bal: 
        return False

    return True

def get_prize_name(item_id):
    return prize_pool_df.loc[prize_pool_df["Item ID"] == item_id, "Item Name"].values[0]

def get_contributor(item_id):
    return prize_pool_df.loc[prize_pool_df["Item ID"] == item_id, "Contributor"].values[0]

def get_twitter(item_id):
    return prize_pool_df.loc[prize_pool_df["Item ID"] == item_id, "Twitter Link"].values[0]

def get_image_name(item_id):
    return prize_pool_df.loc[prize_pool_df["Item ID"] == item_id, "Image Name"].values[0]

def premium_wish(user_id, user_roles):
    if is_wishable(user_id, user_roles, 1):
        prize_id, status = _wish(1)
        prize_name = get_prize_name(prize_id)

        cost = wish_req_df.loc[1, "Cost"]
        decrease_pts(user_id, cost)
        _update_wish_record(user_id, prize_id, prize_name)
        update_prize_pool(prize_id, -1)
        
        return {
            "Name": prize_name,
            "Status": status,
            "Twitter": get_twitter(prize_id),
            "Image": get_image_name(prize_id),
            "Contributor": get_contributor(prize_id)
        }

    return None

def standard_wish(user_id, user_roles):
    if is_wishable(user_id, user_roles, 2):
        prize_id, status = _wish(2)
        prize_name = get_prize_name(prize_id)

        cost = wish_req_df.loc[2, "Cost"]
        decrease_pts(user_id, cost)
        _update_wish_record(user_id, prize_id, prize_name)

        if not status == -1:
            update_prize_pool(prize_id, -1)

        return {
            "Name": prize_name,
            "Status": status,
            "Twitter": get_twitter(prize_id),
            "Image": get_image_name(prize_id),
            "Contributor": get_contributor(prize_id)
        }

    return None

def get_prize_pool():
    prize_pool_dict = {}
    
    for i in prize_pool_df.index.unique():
        prize_pool_dict[i] = []
    
    for i, id, name, left in zip(prize_pool_df.index, prize_pool_df["Item ID"], prize_pool_df["Item Name"], prize_pool_df["Remaining"]):
        prize_pool_dict[i].append([id, name, left])

    return prize_pool_dict

def get_wish_record(user_id):
    return wish_records_df.loc[wish_records_df["Discord ID"] == user_id, ["Item ID", "Item Name"]].to_numpy()

def add_to_prize_pool(tier, item_name, total, contributor, twitter, image_name=""):
    global prize_pool_df

    items_num = get_item_count_in_tier(tier)
    next_item = items_num + 1
    prefix = ''

    if tier == 1:
        prefix = 'A'
    elif tier == 2:
        prefix = 'B'

    next_id = f"{prefix}{str(next_item).zfill(4)}"
    
    new_prize_df = pd.Series([next_id, item_name, total, total, contributor, twitter, image_name], index=prize_pool_df.columns).to_frame().T
    new_prize_df.index = [tier]
    prize_pool_df = pd.concat([prize_pool_df, new_prize_df]).sort_values(by=["Item ID"])
    _flush_prize_pool_data()
    
def get_item_count_in_tier(tier):
    return prize_pool_df.loc[tier, "Item ID"].count()

def _wish(tier):
    tiered_prize_pool = []

    rng = np.random.default_rng()
    rand_int = rng.integers(1, 100, endpoint=True)
    
    if tier == 1:
        luck_status = 1
        if rand_int <= 40:
            tier = 2
            luck_status = 0
    elif tier == 2:
        luck_status = 0
        if rand_int > 90:
            tier = 1
            luck_status = 1
        elif rand_int <= 25:
            tier = 3
            luck_status = -1
            
    if len(prize_pool_df.loc[tier].shape) > 1:
        for item, remaining in zip(prize_pool_df.loc[tier, "Item ID"], prize_pool_df.loc[tier, "Remaining"]):
            tiered_prize_pool += [item] * remaining
    else: 
        tiered_prize_pool = [prize_pool_df.loc[tier, "Item ID"]]

    wish_result_id = rng.choice(tiered_prize_pool)
    
    return wish_result_id, luck_status

def update_prize_pool(item_id, amount):
    prize_pool_df.loc[prize_pool_df["Item ID"] == item_id, "Remaining"] += amount
    _flush_prize_pool_data()

def _update_wish_record(user_id, item_id, item_name):
    global wish_records_df
    timestamp = time.time()
    # TODO: add contributor
    new_df = pd.Series([timestamp, user_id, item_id, item_name], index=wish_records_df.columns).to_frame().T
    wish_records_df = pd.concat([wish_records_df, new_df], ignore_index=True)
    _flush_wish_records()
    
def _flush_prize_pool_data():
    new_prize_pool = prize_pool_df.reset_index(names="Tier")
    new_prize_pool.to_csv("./csv_data/prize_pool.csv", index=False)

def _flush_wish_records():
    wish_records_df.to_csv("./csv_data/wish_records.csv", index=False)