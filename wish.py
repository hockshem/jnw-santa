import pandas as pd
import numpy as np

from member_points import get_pts_bal, decrease_pts

prize_df = pd.read_csv("./csv_data/prize_pool.csv", index_col="Tier")
prize_df = prize_df.fillna("")
# print(prize_df)


wish_req_df = pd.read_csv("./csv_data/wish_info.csv", index_col="Tier")
wish_req_df = wish_req_df.fillna(0)
wish_req_df["Required Role"] = wish_req_df["Required Role"].astype(np.int64)
# print(wish_req_df)


def claim_gift_exchange(user_id, user_roles):
    gift_id = wish(user_id, user_roles, 0)


def premium_wish(user_id, user_roles):
    gift_id = wish(user_id, user_roles, 1)
    if gift_id is not None or gift_id != "":
        update_prize_pool()

def standard_wish(user_id, user_roles):
    gift_id = wish(user_id, user_roles, 2)


def wish(user_id, user_roles, tier):
    # TODO: move this to somewhere else 
    cost = wish_req_df.loc[tier]["Cost"]
    req_role = wish_req_df.loc[tier]["Required Role"]
    user_bal = get_pts_bal(user_id)

    if req_role not in user_roles or cost > user_bal: 
        return None

    rng = np.random.default_rng(None)
    rand_int = rng.integers(1, 100, endpoint=True)
    # print(rand_int)
    
    tiered_prize_pool = []
    
    if tier == 1:
        if rand_int <= 25:
            tier = 2
    elif tier == 2:
        if rand_int > 95:
            tier = 1
        elif rand_int <= 25:
            tier = 3

    if len(prize_df.loc[tier].shape) > 1:
        for item, remaining in zip(prize_df.loc[tier]["Item ID"], prize_df.loc[tier]["Remaining"]):
            tiered_prize_pool += [item] * remaining
    else: 
        tiered_prize_pool = [prize_df.loc[tier]["Item ID"]]

    wish_result_id = rng.choice(tiered_prize_pool)
    
    # tiered_prize_df = prize_df.loc[tier]
    # wish_result_name = tiered_prize_df[tiered_prize_df["Item ID"] == wish_result_id]["Item Name"].values[0]
    # return wish_result_name
    
    return wish_result_id
    

def update_prize_pool(tier, item_id, amount):
    pass

def flush_prize_pool_data():
    pass


print(wish(955688670428549120, [1027076134669660190, 1049961153712889856], 1))
# print(wish(955688670428549120, [1027076134669660190, 1049961153712889856], 1))
# print(wish(955688670428549120, [1027076134669660190, 1049961153712889856], 1))
# print(wish(955688670428549120, [1027076134669660190, 1049961153712889856], 1))
# print(wish(955688670428549120, [1027076134669660190, 1049961153712889856], 1))

# print(wish(955688670428549120, [1027076134669660190, 1049961153712889856], 2))
# print(wish(955688670428549120, [1027076134669660190, 1049961153712889856], 2))
# print(wish(955688670428549120, [1027076134669660190, 1049961153712889856], 2))
# print(wish(955688670428549120, [1027076134669660190, 1049961153712889856], 2))
# print(wish(955688670428549120, [1027076134669660190, 1049961153712889856], 2))


# rng = np.random.default_rng(None)
# rand_int = rng.integers(1, 100, endpoint=True)
# print(rand_int)