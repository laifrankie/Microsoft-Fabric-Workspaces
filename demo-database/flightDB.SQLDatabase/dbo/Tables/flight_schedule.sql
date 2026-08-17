CREATE TABLE [dbo].[flight_schedule] (
    [flight_id]         BIGINT          IDENTITY (1, 1) NOT NULL,
    [flight_number]     VARCHAR (10)    NOT NULL,
    [departure_airport] CHAR (3)        NOT NULL,
    [arrival_airport]   CHAR (3)        NOT NULL,
    [departure_time]    DATETIME2 (7)   NOT NULL,
    [arrival_time]      DATETIME2 (7)   NOT NULL,
    [aircraft_type]     VARCHAR (50)    NULL,
    [base_fare]         DECIMAL (10, 2) NOT NULL,
    [seat_capacity]     INT             NOT NULL,
    [status]            VARCHAR (20)    DEFAULT ('Scheduled') NOT NULL,
    [created_at]        DATETIME2 (7)   DEFAULT (getdate()) NOT NULL,
    PRIMARY KEY CLUSTERED ([flight_id] ASC),
    CONSTRAINT [chk_airports_diff] CHECK ([departure_airport]<>[arrival_airport]),
    CONSTRAINT [chk_capacity_positive] CHECK ([seat_capacity]>(0)),
    CONSTRAINT [chk_fare_nonnegative] CHECK ([base_fare]>=(0))
);


GO

CREATE NONCLUSTERED INDEX [idx_flight_schedule_number_time]
    ON [dbo].[flight_schedule]([flight_number] ASC, [departure_time] ASC);


GO

