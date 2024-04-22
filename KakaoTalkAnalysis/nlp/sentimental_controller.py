import pandas as pd


class SentimentalController:
    def __init__(self, session_df, sentimental_dict) -> None:
        self.session_df = session_df
        self.sentimental_dict = sentimental_dict
        self.sentimental_df = self.__make_sentimental_df()

    def calc_total_ratio(self):
        sentimental_df = self.sentimental_df.copy()
        total_sentimental_ratio = (
            sentimental_df[["negative", "positive", "neutral"]].sum(axis=0)
            / sentimental_df[["negative", "positive", "neutral"]]
            .sum(axis=0)
            .sum()
        )
        return total_sentimental_ratio

    def calc_user_ratio(self):
        sentimental_df = self.sentimental_df.copy()
        session_user_ratio_df = self.__calc_session_user_ratio_df()
        user_sentimental_df = session_user_ratio_df.merge(
            sentimental_df.loc[
                :, ["session", "negative", "positive", "neutral"]
            ].drop_duplicates(),
            on=["session"],
        )
        user_sentimental_df.loc[:, ["negative", "positive", "neutral"]] = (
            user_sentimental_df.loc[
                :, ["negative", "positive", "neutral"]
            ].mul(user_sentimental_df["user_ratio"], axis=0)
        )

        user_sentimental_sum = user_sentimental_df.groupby("User")[
            ["negative", "positive", "neutral"]
        ].sum()
        user_ratio_df = user_sentimental_sum.div(
            user_sentimental_sum.sum(axis=1), axis=0
        )
        return user_ratio_df

    def __make_sentimental_df(self):
        sentimental_dict = self.sentimental_dict.copy()
        sentimental_df = pd.DataFrame(sentimental_dict).T
        # preproc
        sentimental_df = sentimental_df.dropna(subset=["document"])
        sentimental_df = sentimental_df["document"].apply(pd.Series)
        sentimental_df = pd.concat(
            [
                sentimental_df.drop(columns=["confidence"]),
                sentimental_df["confidence"].apply(pd.Series),
            ],
            axis=1,
        )
        sentimental_df = sentimental_df.reset_index(names="session")
        return sentimental_df

    def __calc_session_user_ratio_df(self):
        session_df = self.session_df.copy()
        _session_user_cnt_df = (
            session_df.groupby(["session", "User"])
            .size()
            .rename("user_cnt")
            .reset_index()
        )
        _session_cnt_df = (
            session_df.groupby(["session"])
            .size()
            .rename("session_cnt")
            .reset_index()
        )
        session_user_ratio_df = _session_user_cnt_df.merge(
            _session_cnt_df, on="session"
        )
        session_user_ratio_df["user_ratio"] = (
            session_user_ratio_df["user_cnt"]
            / session_user_ratio_df["session_cnt"]
        )

        return session_user_ratio_df
