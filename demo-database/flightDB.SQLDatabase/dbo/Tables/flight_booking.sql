CREATE TABLE [dbo].[flight_booking] (
    [booking_id]        BIGINT          IDENTITY (1, 1) NOT NULL,
    [flight_id]         BIGINT          NOT NULL,
    [customer_id]       BIGINT          NOT NULL,
    [booking_reference] VARCHAR (12)    NOT NULL,
    [booking_status]    VARCHAR (20)    NOT NULL,
    [booking_channel]   VARCHAR (30)    NOT NULL,
    [seat_number]       VARCHAR (5)     NULL,
    [fare_paid]         DECIMAL (10, 2) NOT NULL,
    [taxes_and_fees]    DECIMAL (10, 2) DEFAULT ((0.00)) NOT NULL,
    [currency]          CHAR (3)        DEFAULT ('USD') NOT NULL,
    [payment_method]    VARCHAR (20)    NOT NULL,
    [created_at]        DATETIME2 (7)   DEFAULT (getdate()) NOT NULL,
    PRIMARY KEY CLUSTERED ([booking_id] ASC),
    CONSTRAINT [chk_fare_nonnegative_b] CHECK ([fare_paid]>=(0)),
    CONSTRAINT [chk_taxes_nonnegative_b] CHECK ([taxes_and_fees]>=(0)),
    CONSTRAINT [fk_booking_customer] FOREIGN KEY ([customer_id]) REFERENCES [dbo].[customers] ([customer_id]) ON UPDATE CASCADE,
    CONSTRAINT [fk_booking_flight] FOREIGN KEY ([flight_id]) REFERENCES [dbo].[flight_schedule] ([flight_id]) ON UPDATE CASCADE,
    UNIQUE NONCLUSTERED ([booking_reference] ASC)
);


GO

CREATE NONCLUSTERED INDEX [idx_booking_customer]
    ON [dbo].[flight_booking]([customer_id] ASC);


GO

CREATE NONCLUSTERED INDEX [idx_booking_flight]
    ON [dbo].[flight_booking]([flight_id] ASC);


GO

CREATE NONCLUSTERED INDEX [idx_booking_status]
    ON [dbo].[flight_booking]([booking_status] ASC);


GO

