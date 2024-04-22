import time
import pandas as pd
from sklearn.cluster import DBSCAN


class SessionPreproc:
    def __init__(self, df) -> None:
        self.df = df

    def time_bsd_session(self, minutes: int = 10):
        session_df = self.df.copy()
        time_diff = session_df["Date"].diff()
        session_df["session"] = (
            time_diff > pd.Timedelta(minutes=minutes)
        ).cumsum()
        return session_df

    def volume_bsd_session(self):
        session_df = self.df.copy()
        catdate_df = self._calc_catdate_df(session_df)
        session_df = session_df.merge(
            catdate_df.reset_index().loc[:, ["CatDate", "session"]],
            on="CatDate",
        )
        session_df["session"] = session_df["session"].fillna(-1).astype(int)
        session_df.drop(columns=["CatDate"], inplace=True)
        return session_df

    def cluster_bsd_session(self, minute: int = 5, talk: int = 15):
        session_df = self.df.copy()
        clusters = self._calc_clusters(session_df, minute, talk)
        session_df["session"] = clusters
        return session_df

    def _calc_catdate_df(self, df):
        catdate_df = self._make_catdate_df(df)
        session_dict = self._calc_session_dict(catdate_df)
        catdate_df["session"] = catdate_df.index.map(session_dict)
        return catdate_df

    @staticmethod
    def _make_catdate_df(df):
        df["CatDate"] = df["Date"].dt.round("10T")
        catdate_cnt = df.groupby("CatDate").size()
        catdate_cnt_rolled = catdate_cnt.rolling(window=3).mean()
        catdate_cnt_rolled = catdate_cnt_rolled.fillna(catdate_cnt)
        catdate_df = pd.concat(
            [
                catdate_cnt_rolled < catdate_cnt,
                catdate_cnt_rolled > catdate_cnt,
            ],
            axis=1,
        )
        catdate_df.columns = ["session_st", "session_end"]
        return catdate_df

    @staticmethod
    def _calc_session_dict(catdate_df):
        is_session_on = 0
        current_session = 0
        session_dict = dict()
        for idx, row in catdate_df.iterrows():
            if not is_session_on:
                if row["session_st"] == True:
                    is_session_on = 1
                    session_dict[idx] = current_session
                    current_session += 1
            elif is_session_on:
                if row["session_end"] == False:
                    session_dict[idx] = current_session
                elif row["session_end"] == True:
                    is_session_on = 0
        return session_dict

    @staticmethod
    def _calc_clusters(df, minute, talk):
        time_series = df["Date"].apply(lambda x: time.mktime(x.timetuple()))
        model = DBSCAN(eps=60 * minute, min_samples=talk)
        clusters = model.fit_predict(time_series.to_frame())
        return clusters
