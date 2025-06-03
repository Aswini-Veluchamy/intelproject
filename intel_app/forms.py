import pandas as pd
import re

class ReadExcelLoad:
    def __init__(self, path):
        self.path = path

    def read_execl_data(self):
        return pd.read_excel(self.path)

    def extract_data(self):
        data = self.read_execl_data()
        trend_cols = [col for col in data.columns if col.startswith('Trend WW')]
        latest_trend_col = max(trend_cols, key=lambda col: self.extract_week(col))
        base_cols = ['unique_id', 'task name', 'Drive To Date', 'status']
        final_cols = base_cols + [latest_trend_col]
        final_data = data[final_cols].copy()
        final_data.rename(columns={latest_trend_col: 'trend date'}, inplace=True)
        final_data['Drive To Date'] = final_data['Drive To Date'].apply(self.convert_ww_format)
        final_data['trend date'] = final_data['trend date'].apply(self.convert_ww_format)
        # Print the final dataset
        print("Final dataset:")
        print(final_data)

    @staticmethod
    def extract_week(col_name):
        match = re.search(r"Trend WW (\d+)'", col_name)
        return int(match.group(1)) if match else -1

    @staticmethod
    def convert_ww_format(value):
        if pd.isna(value):
            return value
        match = re.match(r"ww(\d+(?:\.\d+)?)'(\d+)", str(value))
        if match:
            week = match.group(1)
            if '.' not in week:
                week = f"{week}.5"  # Add default .5
            year_suffix = match.group(2)
            year_full = f"20{year_suffix}"
            return f"{year_full}{week}"
        return value


reader = ReadExcelLoad('Book1.xlsx')
reader.extract_data()