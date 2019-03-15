import sys
import os

def extract_ts_from_step_report(report_path, txn_type, metric_type):
    """ Retrieving thr time series for txn of a certain type"""
    txn_index = -1
    if txn_type == "Read-only Lite":
        txn_index = 0
    elif txn_type == "Read-only Medium":
        txn_index = 1
    elif txn_type == "Read-only Heavy":
        txn_index = 2
    elif txn_type == "Update Lite":
        txn_index = 3
    elif txn_type == "Update Heavy":
        txn_index = 4
    elif txn_type == "Insert Lite":
        txn_index = 5
    elif txn_type == "Insert Heavy":
        txn_index = 6
    elif txn_type == "Delete":
        txn_index = 7
    elif txn_type == "CPU Heavy":
        txn_index = 8

    metric_index = -1
    if metric_type == "Count":
        metric_index = 0
    elif metric_type == "MinRT":
        metric_index = 1
    elif metric_type == "AvgRT":
        metric_index = 2
    elif metric_type == "MaxRT":
        metric_index = 3

    timestamp = []
    value = []
    header_line_num = 11
    with open(report_path, "r", encoding="utf-16le") as data:
        header_line_cnt = 0
        for line in data:
            if header_line_cnt >= header_line_num:
                fields = line.split(" ")
                fields = list(filter(lambda x : len(x) > 0, fields))
                if len(fields) < 2:
                    continue
                timestamp.append(fields[0] + " " + fields[1])
                if txn_type != "All":                   
                    value.append(float(fields[txn_index * 4 + metric_index + 2]))
                else:
                    agg_value = 0
                    if metric_type == "Count":
                        agg_value = 0
                        for i in range(9):
                            agg_value = agg_value + float(fields[2 + metric_index + i * 4])
                    elif metric_type == "MinRT":
                        agg_value = sys.float_info.max
                        for i in range(9):
                            if agg_value > float(fields[2 + metric_index + i * 4]):
                                agg_value = float(fields[2 + metric_index + i * 4])
                    elif metric_type == "AvgRT":
                        agg_value = 0
                        cnt = 0
                        for i in range(9):
                            cnt = cnt + float(fields[2 + i * 4])
                            agg_value = agg_value + float(fields[2 + i * 4]) * float(fields[2 + metric_index + i * 4])
                        if cnt != 0:
                            agg_value = agg_value / cnt
                    elif metric_type == "MaxRT":
                        agg_value = sys.float_info.min
                        for i in range(9):
                            if agg_value < float(fields[2 + metric_index + i * 4]):
                                agg_value = float(fields[2 + metric_index + i * 4])
                    value.append(agg_value)
            else:
                header_line_cnt = header_line_cnt + 1
    return timestamp, value