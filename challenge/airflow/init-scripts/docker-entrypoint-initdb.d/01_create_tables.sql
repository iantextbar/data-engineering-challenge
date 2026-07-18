CREATE TABLE IF NOT EXISTS raw_nyc_tlc_data (
    id SERIAL PRIMARY KEY,
    VendorID INT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count INT,
    trip_distance NUMERIC(10, 2),
    RatecodeID INT,
    store_and_fwd_flag VARCHAR(50),
    PULocationID INT,
    DOLocationID INT,
    payment_type INT,
    fare_amount NUMERIC(14, 2),
    extra NUMERIC(10, 2),
    mta_tax NUMERIC(10, 2),
    tip_amount NUMERIC(14, 2),
    tolls_amount NUMERIC(10, 2),
    improvement_surcharge NUMERIC(10, 2),
    total_amount NUMERIC(10, 2),
    congestion_surcharge NUMERIC(10, 2),
    airport_fee NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS trusted_nyc_tlc_data (
    id SERIAL PRIMARY KEY,
    VendorID INT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    trip_distance NUMERIC(10, 2)
);
