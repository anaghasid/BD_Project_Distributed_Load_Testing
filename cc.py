import pandas as pd



def weighted_metrics(df):
    test_id = df["test_id"]
    # Aggregate metrics
    total_requests = df['number_of_requests'].sum()
    latency_mean = (df['mean_latency'] * df['number_of_requests']).sum() / total_requests
    latency_min = (df['min_latency']).min()
    latency_median = (df['median_latency']).median()
    latency_max = (df['max_latency']).max() 
    return pd.Series({
        'mean_Latency': latency_mean,
        'min_Latency': latency_min,
        'max_Latency': latency_max,
        'median_latency': latency_median,
        'number_of_request':total_requests
    })

    # Group by 'node_id' and calculate the weighted metrics

    # print(driver_aggregate)


def aggregated_driver():
    df = pd.read_csv('gg.csv')
   
    aggregated_driver = df.groupby(['test_id','node_id']).apply(weighted_metrics).reset_index()

    # aggregated_driver = pd.merge(df[['test_id', 'node_id']], aggregated_driver, on='test_id')
    
    print(aggregated_driver)
    
    total_aggregate = df.groupby('test_id').apply(weighted_metrics)
    print(total_aggregate)

aggregated_driver()