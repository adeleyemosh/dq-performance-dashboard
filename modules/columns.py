import pandas as pd

def calculate_week_month(row):
    if pd.isnull(row['validated_date']):
        return "N/A"  # Handle missing dates
    week_number = row['validated_date'].week - (pd.to_datetime(row['validated_date']).to_period('M').start_time.week - 1)
    month_name = row['validated_date'].strftime('%B')
    return f"Week {week_number} - {month_name}"

def calculate_week_month_year(row):
    week_month = calculate_week_month(row)
    year = row['validated_date'].year
    return f"{week_month} {year}"