import re
import pandas as pd

start_phrase = "joined this chatroom"
# bot_name = "팬다 Jr."
bot_name = "오픈채팅봇"


class GeneralPreproc:
    def __init__(self, raw_df):
        self.raw_df = raw_df

    def __call__(self, min_chat=None):
        raw_df = self.raw_df.copy()
        filtered_df = self.__Filters()(raw_df, min_chat)
        renamed_df = self.__RenameUser()(filtered_df)
        renamed_df["Date"] = pd.to_datetime(renamed_df["Date"])
        return renamed_df

    class __Filters:
        @staticmethod
        def _filter_start_phrase(df, start_phrase):
            filtered_df = df[~df["Message"].str.contains(start_phrase)]
            return filtered_df

        @staticmethod
        def _filter_bot_name(df, bot_name):
            filtered_df = df[df["User"] != bot_name]
            return filtered_df

        @staticmethod
        def _filter_min_chat(df, min_chat):
            filtered_df = df
            if min_chat:
                _vc = df["User"].value_counts()
                users = _vc[_vc > min_chat].index
                filtered_df = df[df["User"].isin(users)]
            return filtered_df

        def __call__(self, df, min_chat):
            filtered_df = self._filter_start_phrase(df, start_phrase)
            filtered_df = self._filter_bot_name(filtered_df, bot_name)
            filtered_df = self._filter_min_chat(filtered_df, min_chat)
            return filtered_df

    class __RenameUser:
        @staticmethod
        def _filter_etcs(users):
            _pattern = "[^A-Za-z0-9가-힣ㄱ-ㅣ()]"
            _rename_func = lambda x: re.sub(_pattern, "", x)
            rn_users = map(_rename_func, users)
            return rn_users

        @staticmethod
        def _filter_brackets(users):
            _pattern = r"\(.*?\)"
            _rename_func = lambda x: re.sub(_pattern, "", x)
            rn_users = map(_rename_func, users)
            return rn_users

        @staticmethod
        def get_rename_dict(users, rn_users):
            rename_dict = {
                raw: preproc for raw, preproc in zip(users, rn_users)
            }
            return rename_dict

        def __call__(self, df):
            renamed_df = df.copy()
            users = set(renamed_df["User"])

            rn_users = self._filter_etcs(users)
            rn_users = self._filter_brackets(rn_users)
            rename_dict = self.get_rename_dict(users, rn_users)

            renamed_df["User"] = renamed_df["User"].map(rename_dict)
            return renamed_df