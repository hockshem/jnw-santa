import pandas as pd

points_df = pd.read_csv("./csv_data/member_points.csv", index_col=0)
points_df = points_df.fillna("")

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
    return points_df.loc[user_id, "Accumulated Points"]

def increase_pts(user_id, amount):
    points_df.loc[user_id, "Accumulated Points"] += amount
    points_df.loc[user_id, "Balance"] += amount
    flush_member_points_data()
    
def decrease_pts(user_id, amount):
    points_df.loc[user_id, "Balance"] -= amount
    flush_member_points_data()

def flush_member_points_data():
    new_points_df = points_df.reset_index(names="Discord ID")
    new_points_df.to_csv("./csv_data/member_points.csv", index=False)

print(points_df)
register_new_usr(9999)
print(points_df)