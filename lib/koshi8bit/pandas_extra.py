import numpy as np
import pandas as pd


class PandasExtra:
    @staticmethod
    def df_to_str(df: pd.DataFrame, caption="", show_len: bool = True, indent: bool = True):
        message = "\n\n" if indent else ""
        if caption:
            message += f"### {caption} ###\n"

        desired_width = 1000
        pd.set_option('display.width', desired_width)
        np.set_printoptions(linewidth=desired_width)
        if isinstance(df, pd.DataFrame):
            pd.set_option('display.max_columns', df.shape[1] + 1)

        if isinstance(df, pd.Series):
            pd.set_option('display.max_columns', 2)

        pd.set_option('display.max_rows', df.shape[0] + 1)
        message += f"{str(df)}"
        if show_len:
            message += f"\nlen={len(df)}"
        # pd.set_option('display.max_rows', 20)
        # pd.set_option('display.max_columns', 20)
        return message

    @staticmethod
    def print(df: pd.DataFrame, caption: str = "", show_len: bool = True):
        print(PandasExtra.df_to_str(df, caption, show_len))

    @staticmethod
    def change_type(df: pd.DataFrame) -> pd.DataFrame:
        res = pd.DataFrame(df)
        return res.astype(dtype={'address_comment': 'string'})