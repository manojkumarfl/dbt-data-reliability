select min from {{ ref("numeric_column_anomalies") }} where min < 100
