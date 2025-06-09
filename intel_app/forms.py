import pandas as pd
import re
from datetime import datetime, timedelta


class ReadExcelLoad:
    def __init__(self, path):
        self.path = path

    def read_execl_data(self):
        return pd.read_excel(self.path)

    @staticmethod
    def get_status(por_commit, por_trend):
        current_dt = datetime.now().date()

        # Convert to date
        commit_date = ReadExcelLoad.ww_to_date(por_commit)
        trend_date = ReadExcelLoad.ww_to_date(por_trend)

        # Validate both dates
        if not commit_date or not trend_date:
            return 'None'

        # Compare
        if trend_date < current_dt:
            return 'Done'
        elif trend_date <= commit_date:
            return 'G'
        elif trend_date > commit_date + timedelta(days=14):
            return 'R'
        elif trend_date > commit_date + timedelta(days=7):
            return 'Y'
        return 'None'

    @staticmethod
    def ww_to_date(ww_string):
        match = re.match(r"ww(\d+(?:\.\d+)?)[ ]*'(\d+)", str(ww_string))
        if match:
            week = match.group(1)
            week = week if '.' in week else f"{week}.5"
            week_number = int(float(week))
            year_suffix = match.group(2)
            year = int(f"20{year_suffix}")
            return datetime.strptime(f"{year}-W{week_number:02d}-1", "%G-W%V-%u").date()
        return None

    @staticmethod
    def convert_ww_to_str(value):
        """
        Converts strings like ww12'25 or ww12.3'25 to '202512.5' (string)
        """
        if pd.isna(value):
            return None
        match = re.match(r"ww(\d+(?:\.\d+)?)[ ]*'(\d+)", str(value))
        if match:
            week = match.group(1)
            if '.' not in week:
                week = f"{week}.5"
            year = f"20{match.group(2)}"
            return f"{year}{week}"
        return None

    def extract_data(self):
        data = self.read_execl_data()

        # Find latest Trend WW column
        trend_cols = [col for col in data.columns if col.startswith('Trend WW')]
        sorted_trend_cols = sorted(trend_cols, key=lambda col: self.extract_week(col), reverse=True)
        print(sorted_trend_cols)

        # Step 2: Pick the first column that has at least one non-empty and non-NaN cell
        def has_valid_data(series):
            return series.astype(str).str.strip().replace('nan', '').ne('').any()

        latest_trend_col = None
        for col in sorted_trend_cols:
            if has_valid_data(data[col]):
                latest_trend_col = col
                break
        print(latest_trend_col)
        # Step 3: Fallback if no usable column found
        if not latest_trend_col:
            raise ValueError("No usable Trend WW column found with non-empty data.")

        # Select necessary columns
        base_cols = ['unique_id', 'task name', 'Drive To Date']
        final_cols = base_cols + [latest_trend_col]
        final_data = data[final_cols].copy()

        # Rename for consistency
        final_data.rename(columns={latest_trend_col: 'por_trend', 'Drive To Date': 'por_commit'}, inplace=True)

        # Store formatted versions in new columns
        final_data['por_commit_fmt'] = final_data['por_commit'].apply(self.convert_ww_to_str)
        final_data['por_trend_fmt'] = final_data['por_trend'].apply(self.convert_ww_to_str)

        # Calculate status using original 'ww' strings
        final_data['status'] = final_data.apply(
            lambda row: self.get_status(row['por_commit'], row['por_trend']), axis=1
        )

        # Print result
        print("Final dataset:")
        print(final_data[['task name', 'por_commit_fmt', 'por_trend_fmt', 'status']])

    @staticmethod
    def extract_week(col_name):
        match = re.search(r"Trend WW (\d+)'", col_name)
        return int(match.group(1)) if match else -1


# Usage
reader = ReadExcelLoad('Book1.xlsx')
reader.extract_data()
