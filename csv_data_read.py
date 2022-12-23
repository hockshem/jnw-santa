import pandas as pd
import numpy as np

points_df = pd.DataFrame(pd.read_csv('member_points_data.csv', index_col=0))
points_df.fillna("")

def register_new_usr(user_id):
    if user_id not in points_df.index:
        new_df = pd.Series([0, 0, "", ""], index=points_df.columns).to_frame().T
        new_df.index = [user_id]
        return pd.concat([points_df, new_df])

    return points_df

def get_pts_bal(user_id):
    return points_df.loc[user_id]["Balance"]

def get_pts_acc(user_id):
    return points_df.loc[user_id]["Accumulated Points"]

def increase_pts(user_id, amount):
    points_df.loc[user_id]["Accumulated Points"] += amount
    points_df.loc[user_id]["Balance"] += amount
    
def decrease_pts(user_id, amount):
    points_df.loc[user_id]['Balance'] -= amount


points_df = register_new_usr(5678)
print(points_df)

points_df = register_new_usr(9999)
print(points_df)

points_df = register_new_usr(9999)
print(points_df)

new_points_df = points_df.reset_index(names="Discord ID")
print(new_points_df)
new_points_df.to_csv("new_member_points_data.csv", index=False)
