--  0   VendorID               int64         
--  1   tpep_pickup_datetime   datetime64[us]
--  2   tpep_dropoff_datetime  datetime64[us]
--  3   passenger_count        float64       
--  4   trip_distance          float64       
--  5   RatecodeID             float64       
--  6   store_and_fwd_flag     str           
--  7   PULocationID           int64         
--  8   DOLocationID           int64         
--  9   payment_type           int64         
--  10  fare_amount            float64       
--  11  extra                  float64       
--  12  mta_tax                float64       
--  13  tip_amount             float64       
--  14  tolls_amount           float64       
--  15  improvement_surcharge  float64       
--  16  total_amount           float64       
--  17  congestion_surcharge   float64       
--  18  airport_fee            float64

CREATE TABLE IF NOT EXISTS raw_nyc_tlc_data (
    id SERIAL PRIMARY KEY,
    VendorID INT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count INT,
    trip_distance NUMERIC,
    RatecodeID INT,
    store_and_fwd_flag VARCHAR(50),
    PULocationID INT,
    DOLocationID INT,
    payment_type INT,
    fare_amount NUMERIC(10, 2),
    extra NUMERIC,
    mta_tax NUMERIC,
    tip_amount NUMERIC(10, 2),
    tolls_amount NUMERIC(10, 2),
    improvement_surcharge NUMERIC(10, 2),
    total_amount NUMERIC(10, 2),
    congestion_surcharge NUMERIC(10, 2),
    airport_fee NUMERIC(10, 2)
)
