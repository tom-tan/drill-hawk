from datetime import datetime


def elapsed_sec(start_date, end_date):
    """
    end_data - start_date の秒数計算
    """
    start_timestamp = datetime.strptime(start_date[0:19], "%Y-%m-%dT%H:%M:%S")
    end_timestamp = datetime.strptime(end_date[0:19], "%Y-%m-%dT%H:%M:%S")
    elapsed_sec = (end_timestamp - start_timestamp).total_seconds()

    return int(elapsed_sec)
