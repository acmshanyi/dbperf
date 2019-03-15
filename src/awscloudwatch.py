import boto3
import datetime
import time
import datapoint as dp
import operator

class AWSClient:
    def __init__(self, key, secret, region):
        self.key = key
        self.secret = secret
        self.region = region
        self.cloudwatch = boto3.client(
            'cloudwatch',
            aws_access_key_id = self.key,
            aws_secret_access_key = self.secret,
            region_name = self.region
        )
    
    def get_rds_metric(self, starttime, endtime, metricname, namespace, dbclusterid, statistic, period):
        datapoints = self.cloudwatch.get_metric_statistics(
            Period=period,
            StartTime=datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S"),
            EndTime=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S"),
            MetricName=metricname,
            Namespace=namespace,
            Dimensions=[{'Name':'DBClusterIdentifier', 'Value':dbclusterid}],
            Statistics = [statistic]
        )['Datapoints']

        datapoint_list = []
        for i in datapoints:
            datapoint_list.append(dp.DataPoint(i["Timestamp"].strftime("%Y-%m-%dT%H:%M:%S"), float(i["Average"])))

        datapoint_list.sort(key = operator.attrgetter('timestamp'))
        
        timestamp = []
        value = []
        
        for i in datapoint_list:
            timestamp.append(i.timestamp)
            value.append(i.value)
        
        return timestamp, value