import pandas as pd

from time import time, strftime, localtime

points_df = pd.read_csv("./csv_data/member_points.csv", index_col=0)
points_df = points_df.fillna("")

daily_df = pd.read_csv("./csv_data/daily_claim.csv")
daily_df = daily_df.fillna("")

def register_new_usr(user_id):
    global points_df
    if user_id not in points_df.index:
        new_df = pd.Series([0, 0], index=points_df.columns).to_frame().T
        new_df.index = [user_id]
        points_df = pd.concat([points_df, new_df])
        flush_member_points_data()

def get_pts_bal(user_id):
    if user_id not in points_df.index: 
        register_new_usr(user_id)
    return points_df.loc[user_id, "Balance"]

def get_pts_acc(user_id):
    if user_id not in points_df.index: 
        register_new_usr(user_id)
    return points_df.loc[user_id, "Accumulated Points"]

def increase_pts(user_id, amount):
    if user_id not in points_df.index: 
        register_new_usr(user_id)
    points_df.loc[user_id, "Accumulated Points"] += amount
    points_df.loc[user_id, "Balance"] += amount
    flush_member_points_data()
    
def decrease_pts(user_id, amount):
    if user_id not in points_df.index: 
        register_new_usr(user_id)
    points_df.loc[user_id, "Balance"] -= amount
    flush_member_points_data()

def _can_claim_daily(user_id):
    if user_id in daily_df["Discord ID"].values:
        last_record = daily_df.loc[daily_df["Discord ID"] == user_id, "Daily Claim"].values[0]
        
        if last_record != "":
            current_epoch = time()
            local_time_now = localtime(current_epoch)
            date_now = strftime("%Y-%m-%d", local_time_now)
            local_time_recorded = localtime(last_record)
            date_recorded = strftime("%Y-%m-%d", local_time_recorded)
            
            if date_now == date_recorded:
                return False
    
    return True

def claim_daily(user_id):
    global daily_df
    daily_pts = 10
    
    result = {
        'status': False,
        'points': 0
    }

    if _can_claim_daily(user_id):
        if user_id not in daily_df["Discord ID"].values:
            new_df = pd.Series([user_id, time()], index=daily_df.columns).to_frame().T
            daily_df = pd.concat([daily_df, new_df])
        
        daily_df.loc[daily_df["Discord ID"] == user_id, "Daily Claim"] = time()
        increase_pts(user_id, daily_pts)
        flush_daily_claim_data()
        result["status"] = True
        result["points"] = daily_pts
            
    return result

def flush_daily_claim_data():
    daily_df.to_csv("./csv_data/daily_claim.csv", index=False)

def flush_member_points_data():
    new_points_df = points_df.reset_index(names="Discord ID")
    new_points_df.to_csv("./csv_data/member_points.csv", index=False)
