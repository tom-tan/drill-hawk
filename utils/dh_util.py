from datetime import datetime


def elapsed_sec(start_date, end_date):
    """
    end_data - start_date の秒数計算
    """

    # yyyy-MM-dd HH:mm:ss -> yyyy-MM-ddTHH:mm:ss
    start_date_formated = start_date[0:19].replace(" ", "T")
    end_date_formated = end_date[0:19].replace(" ", "T")
    start_timestamp = datetime.strptime(start_date_formated, "%Y-%m-%dT%H:%M:%S")
    end_timestamp = datetime.strptime(end_date_formated, "%Y-%m-%dT%H:%M:%S")
    elapsed_sec = (end_timestamp - start_timestamp).total_seconds()

    return int(elapsed_sec)
