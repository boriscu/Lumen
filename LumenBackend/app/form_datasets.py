import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
from app.enums.room_indices_dict import room_dict, room_indices, room_column
import json


def form_room_occupancy(ds):
    room_counts = (
        ds.groupby(["stay_date", "room_category_id"])["room_cnt"]
        .sum()
        .reset_index(name="room_count")
    )
    new_dataset = room_counts.pivot(
        index="stay_date", columns="room_category_id", values="room_count"
    )
    new_dataset = new_dataset.fillna(0)
    new_dataset.columns = [f"room_type_{col}" for col in new_dataset.columns]
    new_dataset.reset_index(inplace=True)
    return new_dataset


def remove_anomalies_winsorization(column, lower_percentile=0, upper_percentile=0.95):
    lower_bound = column.quantile(lower_percentile)
    upper_bound = column.quantile(upper_percentile)

    column = np.where(column < lower_bound, lower_bound, column)
    column = np.where(column > upper_bound, upper_bound, column)

    return column


def one_hot_occupancy(ds, target_ds):
    for index, row in ds.iterrows():
        date = row[0]
        row = row[1:]
        for j in range(8):
            mask = [0 for _ in range(8)]
            new_row = mask
            mask[j] = 1
            for i in range(8):
                new_row[i] = row[i] if mask[i] == 1 else 0
            new_row.insert(0, date)
            target_ds = pd.concat(
                [target_ds, pd.DataFrame([new_row], columns=target_ds.columns)],
                ignore_index=True,
            )
    return target_ds


def one_hot_occupancy_separated(ds):
    for index, row in ds.iterrows():
        date = row[0]
        row_data = row[1:]
        row_data = row_data[:-1]
        res = -10
        for i in range(len(row_data)):
            if row_data[i] != 0:
                res = row_data[i]
                row_data[i] = 1
        if res == -10:
            row_data[index % 8] = 1
            res = 0
        row_data = [date] + list(row_data) + [res]
        ds.loc[index] = row_data
    return ds


def form_rank_days_of_week(week_day_dataset):
    ranked_days = pd.DataFrame(week_day_dataset)
    for column in ranked_days.columns:
        ranked_days[column] = week_day_dataset[column].rank(method="min")
    return ranked_days


def day_week_avg_column(ds, day_avg_data):
    for index, row in ds.iterrows():
        day_of_week = ds.at[index, "day_of_week"][0]
        week_avgs = [
            day_avg_data.at[day_of_week, f"room_type_{j}"] for j in room_indices
        ]
        ds.at[index, "week_day_avg"] = week_avgs
    return ds


def month_avg_column(ds, month_avg_data):
    for index, row in ds.iterrows():
        month = index.month
        monthly_avgs = [
            month_avg_data.at[month, f"room_type_{j}"] for j in room_indices
        ]
        ds.at[index, "month_avg"] = monthly_avgs
    return ds


def week_day_importance(ds, ranked_days):
    for index, row in ds.iterrows():
        l = [row[i] for i in range(len(room_column))]
        room_index = l.index(1)
        room_type = room_dict[room_index]
        day_of_week = ds.at[index, "day_of_week"][room_index]
        week_day_importance_value = ranked_days.at[
            day_of_week, f"room_type_{room_type}"
        ]
        ds.at[index, "week_day_importance"][room_index] = week_day_importance_value
    return ds


def load_events(datasets):

    separated_events_file = open("events/separated_events.json")

    separated_events = json.load(separated_events_file)
    og_events = pd.read_json("events/events.json")

    for i in range(len(datasets)):

        datasets[i]["event"] = 0
        ds = datasets[i]
        room_type = room_dict[i]

        room_type_events = separated_events[str(room_type)]

        for event_name in room_type_events:
            dates = dict(og_events[og_events["name"] == event_name]["date"])
            for values in dates.values():
                for value in values:
                    start_date = pd.to_datetime(value["start_date"])
                    finish_date = pd.to_datetime(value["finish_date"])
                    mask = (ds["stay_date_help"] >= start_date) & (
                        ds["stay_date_help"] <= finish_date
                    )
                    ds.loc[mask, "event"] += 1
        datasets[i] = ds

    return datasets


def form(dataset_path):

    dataset = pd.read_parquet(dataset_path)

    dataset.drop(
        [
            "guest_id",
            "resort_id",
            "price",
            "price_tax",
            "total_price",
            "total_price_tax",
            "food_price",
            "food_price_tax",
            "other_price",
            "other_price_tax",
            "sales_channel_id",
        ],
        axis="columns",
        inplace=True,
    )

    dataset["reservation_status"] = dataset["reservation_status"].replace(
        "No-show", "Cancelled"
    )

    dataset_without_cancelled = dataset[dataset["reservation_status"] != "Cancelled"]
    dataset_without_cancelled = dataset_without_cancelled.drop(
        ["cancel_date", "reservation_status", "guest_country_id"], axis="columns"
    )

    dataset_without_cancelled = dataset_without_cancelled.iloc[2:].reset_index(
        drop=True
    )

    occupancy = form_room_occupancy(dataset_without_cancelled)

    dataset = pd.DataFrame(columns=occupancy.columns)
    dataset = one_hot_occupancy(occupancy, dataset)

    occupancy.set_index("stay_date", inplace=True)
    occupancy_by_day_of_week = occupancy.groupby(occupancy.index.dayofweek).mean()
    occupancy_by_month = occupancy.groupby(occupancy.index.month).mean()

    dataset["occupancy"] = 0
    dataset = one_hot_occupancy_separated(dataset)

    dataset["stay_date_help"] = dataset["stay_date"]
    dataset.set_index("stay_date", inplace=True)
    dataset["day_of_week"] = dataset.index.dayofweek

    ranked_days_mask = form_rank_days_of_week(occupancy_by_day_of_week)

    dataset["week_day_avg"] = 0
    dataset["month_avg"] = 0
    dataset["week_day_importance"] = 0

    dataset = day_week_avg_column(dataset, occupancy_by_day_of_week)
    dataset = month_avg_column(dataset, occupancy_by_month)
    dataset = week_day_importance(dataset, ranked_days_mask)

    dataset_1 = dataset[dataset["room_type_1"] == 1]
    dataset_2 = dataset[dataset["room_type_2"] == 1]
    dataset_3 = dataset[dataset["room_type_3"] == 1]
    dataset_4 = dataset[dataset["room_type_4"] == 1]
    dataset_5 = dataset[dataset["room_type_5"] == 1]
    dataset_6 = dataset[dataset["room_type_6"] == 1]
    dataset_7 = dataset[dataset["room_type_7"] == 1]
    dataset_11 = dataset[dataset["room_type_11"] == 1]

    dataset_1.drop(
        columns=[
            "room_type_1",
            "room_type_2",
            "room_type_3",
            "room_type_4",
            "room_type_5",
            "room_type_6",
            "room_type_7",
            "room_type_11",
        ],
        inplace=True,
    )

    dataset_2.drop(
        columns=[
            "room_type_1",
            "room_type_2",
            "room_type_3",
            "room_type_4",
            "room_type_5",
            "room_type_6",
            "room_type_7",
            "room_type_11",
        ],
        inplace=True,
    )

    dataset_3.drop(
        columns=[
            "room_type_1",
            "room_type_2",
            "room_type_3",
            "room_type_4",
            "room_type_5",
            "room_type_6",
            "room_type_7",
            "room_type_11",
        ],
        inplace=True,
    )

    dataset_4.drop(
        columns=[
            "room_type_1",
            "room_type_2",
            "room_type_3",
            "room_type_4",
            "room_type_5",
            "room_type_6",
            "room_type_7",
            "room_type_11",
        ],
        inplace=True,
    )

    dataset_5.drop(
        columns=[
            "room_type_1",
            "room_type_2",
            "room_type_3",
            "room_type_4",
            "room_type_5",
            "room_type_6",
            "room_type_7",
            "room_type_11",
        ],
        inplace=True,
    )

    dataset_6.drop(
        columns=[
            "room_type_1",
            "room_type_2",
            "room_type_3",
            "room_type_4",
            "room_type_5",
            "room_type_6",
            "room_type_7",
            "room_type_11",
        ],
        inplace=True,
    )

    dataset_7.drop(
        columns=[
            "room_type_1",
            "room_type_2",
            "room_type_3",
            "room_type_4",
            "room_type_5",
            "room_type_6",
            "room_type_7",
            "room_type_11",
        ],
        inplace=True,
    )

    dataset_11.drop(
        columns=[
            "room_type_1",
            "room_type_2",
            "room_type_3",
            "room_type_4",
            "room_type_5",
            "room_type_6",
            "room_type_7",
            "room_type_11",
        ],
        inplace=True,
    )

    datasets = [
        dataset_1,
        dataset_2,
        dataset_3,
        dataset_4,
        dataset_5,
        dataset_6,
        dataset_7,
        dataset_11,
    ]

    i = 0

    for ds in datasets:

        for j in range(7):
            ds[f"occupancy_lag_{j+1}"] = ds["occupancy"].shift(j + 1)

        ds["mean_last_7"] = ds["occupancy"].shift(1).rolling(7).mean()
        ds["max_last_7"] = ds["occupancy"].shift(1).rolling(7).max()
        ds["min_last_7"] = ds["occupancy"].shift(1).rolling(7).min()

        min_since_day_one = ds["occupancy"].expanding().min()
        ds["min_last_7"] = ds["min_last_7"].fillna(min_since_day_one)

        max_since_day_one = ds["occupancy"].expanding().max()
        ds["max_last_7"] = ds["max_last_7"].fillna(max_since_day_one)

        mean_since_day_one = ds["occupancy"].expanding().mean()
        ds["mean_last_7"] = ds["mean_last_7"].fillna(mean_since_day_one)

        for j in range(7):
            ds[f"occupancy_lag_{j+1}"] = ds[f"occupancy_lag_{j+1}"].fillna(
                ds[f"occupancy_lag_{j+1}"].shift(-7)
            )

        ds["occupancy_1"] = ds["occupancy"].shift(-1)
        ds["occupancy_2"] = ds["occupancy"].shift(-2)
        ds["occupancy_3"] = ds["occupancy"].shift(-3)
        ds["occupancy_4"] = ds["occupancy"].shift(-4)
        ds["occupancy_5"] = ds["occupancy"].shift(-5)
        ds["occupancy_6"] = ds["occupancy"].shift(-6)

        ds["occupancy_1"] = ds["occupancy_1"].fillna(ds["occupancy_1"].shift(7))
        ds["occupancy_2"] = ds["occupancy_2"].fillna(ds["occupancy_2"].shift(7))
        ds["occupancy_3"] = ds["occupancy_3"].fillna(ds["occupancy_3"].shift(7))
        ds["occupancy_4"] = ds["occupancy_4"].fillna(ds["occupancy_4"].shift(7))
        ds["occupancy_5"] = ds["occupancy_5"].fillna(ds["occupancy_5"].shift(7))
        ds["occupancy_6"] = ds["occupancy_6"].fillna(ds["occupancy_6"].shift(7))

        datasets[i] = ds

        i += 1

    datasets = load_events(datasets)

    columns_to_normalize = [
        "week_day_avg",
        "month_avg",
        "week_day_importance",
        "mean_last_7",
        "max_last_7",
        "min_last_7",
        "event",
        "occupancy_lag_1",
        "occupancy_lag_2",
        "occupancy_lag_3",
        "occupancy_lag_4",
        "occupancy_lag_5",
        "occupancy_lag_6",
        "occupancy_lag_7",
    ]

    for i, dataset in enumerate(datasets):

        scaler = RobustScaler()
        dataset[columns_to_normalize] = scaler.fit_transform(
            dataset[columns_to_normalize]
        )

        dataset.to_csv(f"datasets/dataset_room_type_{room_dict[i]}.csv")

    return
