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
        if pd.isna(por_commit) and pd.isna(por_trend):
            return 'None'
        elif pd.isna(por_commit) or pd.isna(por_trend):
            return 'None'
        elif por_trend and por_commit:
            por_commit_one_week_later = por_commit + timedelta(days=7)
            por_commit_two_week_later = por_commit + timedelta(days=14)
            if por_trend < current_dt:
                return 'Done'
            elif (por_commit == por_trend) or (por_trend < por_commit):
                return 'G'
            elif por_trend > por_commit_two_week_later:
                return 'R'
            elif por_trend > por_commit_one_week_later:
                return 'Y'
        return 'None'

    def extract_data(self):
        data = self.read_execl_data()

        # Find latest Trend WW column
        trend_cols = [col for col in data.columns if col.startswith('Trend WW')]
        latest_trend_col = max(trend_cols, key=lambda col: self.extract_week(col))

        # Select necessary columns
        base_cols = ['unique_id', 'task name', 'Drive To Date']
        final_cols = base_cols + [latest_trend_col]
        final_data = data[final_cols].copy()

        # Rename latest trend col
        final_data.rename(columns={latest_trend_col: 'trend date'}, inplace=True)

        # Convert to datetime format
        final_data['por_commit'] = final_data['Drive To Date'].apply(self.convert_ww_to_date)
        final_data['por_trend'] = final_data['trend date'].apply(self.convert_ww_to_date)

        # Calculate status for each row
        final_data['status'] = final_data.apply(
            lambda row: self.get_status(row['por_commit'], row['por_trend']), axis=1
        )

        # Print result
        print("Final dataset:")
        print(final_data)

    @staticmethod
    def extract_week(col_name):
        match = re.search(r"Trend WW (\d+)'", col_name)
        return int(match.group(1)) if match else -1

    @staticmethod
    def convert_ww_to_date(value):
        """
        Converts a string like ww12'25 or ww12.3'25 to a datetime.date object.
        """
        if pd.isna(value):
            return None
        match = re.match(r"ww(\d+(?:\.\d+)?)[ ]*'(\d+)", str(value))
        if match:
            week = match.group(1)
            if '.' not in week:
                week = f"{week}.5"
            week_num = int(float(week))
            year_suffix = match.group(2)
            year_full = int(f"20{year_suffix}")
            # Approximate conversion: assume Monday of the week
            return datetime.strptime(f'{year_full}-W{week_num:02d}-1', "%Y-W%W-%w").date()
        return None


# Usage
reader = ReadExcelLoad('Book1.xlsx')
reader.extract_data()

#
# sql = f"INSERT INTO {SCHEDULE_TABLE} (display, milestone, por_commit, por_trend, status, comments, schedule_id,\
#             user, project, deleted, deleted_by, deleted_on, task_id, work_type, ww_psd, milestone_ent, task_group_ent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
# val = (display, milestone, por_commit, por_trend, status, comments, schedule_id, user, proj, deleted, deleted_by,
#        deleted_on, task_id, work_type, ww_psd, milestone_ent, task_group_ent)
# cursor.execute(sql, val)