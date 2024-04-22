import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class Visualizer:
    @staticmethod    
    def draw_pieplot(ratio_df):
        ratio_series = ratio_df.squeeze()
        plt.pie(
            x=ratio_series.values,
            labels=ratio_series.index,
            autopct="%.1f%%",
            colors=sns.color_palette("Set2"),
        )
        plt.tight_layout()
        plt.show()
        return None
