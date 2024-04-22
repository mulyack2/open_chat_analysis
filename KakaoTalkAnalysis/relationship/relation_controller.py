import pandas as pd


class RelationController:
    def __init__(self, session_df) -> None:
        self.df = session_df

    def calc_abs_score(self):
        """User가 참여한 Session 중 Session에 참여한 비율"""
        df = self.df.copy()
        users = set(df["User"])
        absolute_ratio_df = pd.concat(
            [
                self._calc_abs_user_ratio(
                    df, user, self._get_involved_sessions(df, user)
                )
                for user in users
            ],
            axis=1,
        )
        return absolute_ratio_df

    def calc_rel_score(self):
        """전체 참여 Session 중 User가 참여한 Session에 참여한 비율"""
        session_df = self.df.copy()
        users = set(session_df["User"])
        relative_ratio_df = pd.concat(
            [
                self._calc_rel_user_ratio(
                    session_df,
                    user,
                    self._get_involved_sessions(session_df, user),
                )
                for user in users
            ],
            axis=1,
        )
        return relative_ratio_df
    
    @staticmethod
    def format_score(abs_score, rel_score):
        ratio_df = pd.concat(
            [
                abs_score.unstack().to_frame(name="abs_score"),
                rel_score.unstack().to_frame(name="rel_score"),
            ],
            axis=1,
        )
        ratio_df = ratio_df.dropna()
        ratio_df["score"] = ratio_df["abs_score"] + ratio_df["rel_score"]
        ratio_df.reset_index(inplace=True)
        ratio_df.columns = ["subject", "object", "abs_score", "rel_score", "score"]
        return ratio_df
    

    @staticmethod
    def _get_user_involved_session(session_df):
        user_involved_session = (
            session_df.groupby("User")["session"].unique().apply(len)
        )
        return user_involved_session

    @staticmethod
    def _get_involved_sessions(session_df, user) -> set:
        sessions = set(session_df[session_df["User"] == user]["session"])
        return sessions

    @staticmethod
    def _calc_session_involved_cnt(session_df, user, sessions):
        _session_involved_cnt = (
            session_df[
                (session_df["session"].isin(sessions))
                & (session_df["User"] != user)
            ]
            .drop_duplicates(["User", "session"])["User"]
            .value_counts()
        )
        return _session_involved_cnt

    def _calc_abs_user_ratio(self, session_df, user, sessions):
        _session_involved_cnt = self._calc_session_involved_cnt(
            session_df, user, sessions
        )
        user_ratio = _session_involved_cnt / len(sessions)
        user_ratio = user_ratio.rename(user)
        return user_ratio

    def _calc_rel_user_ratio(self, session_df, user, sessions):
        user_involved_session = self._get_user_involved_session(session_df)
        _session_involved_cnt = self._calc_session_involved_cnt(
            session_df, user, sessions
        )
        ratio_v2 = (
            _session_involved_cnt.div(user_involved_session)
            .dropna()
            .sort_values(ascending=False)
        )
        ratio_v2 = ratio_v2.rename(user)
        return ratio_v2
