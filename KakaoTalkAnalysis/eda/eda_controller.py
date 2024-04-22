import pandas as pd


class EdaController:
    # def __init__(self, df: pd.DataFrame) -> None:
    #     self.df = df

    def info_dict(self, df) -> dict:
        info_dict = {
            "start_date": self.start_date(df),
            "end_date": self.end_date(df),
            "total_user": self.total_user(df),
            "total_talk": self.total_talk(df),
        }
        return info_dict

    def info_print(self, df) -> None:
        print("start_date :", self.start_date(df))
        print("end_date   :", self.end_date(df))
        print("total_user :", self.total_user(df))
        print("total_talk :", self.total_talk(df))
        return None

    @staticmethod
    def start_date(df):
        min_date = df["Date"].min().strftime("%Y-%m-%d %H:%M")
        return min_date

    @staticmethod
    def end_date(df):
        max_date = df["Date"].max().strftime("%Y-%m-%d %H:%M")
        return max_date

    @staticmethod
    def total_user(df):
        total_user = len(set(df["User"]))
        return total_user

    @staticmethod
    def total_talk(df):
        total_talk = len(df)
        return total_talk
