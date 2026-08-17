CREATE TABLE [dbo].[customers] (
    [customer_id]   BIGINT        IDENTITY (1, 1) NOT NULL,
    [first_name]    VARCHAR (50)  NOT NULL,
    [last_name]     VARCHAR (50)  NOT NULL,
    [email]         VARCHAR (255) NOT NULL,
    [phone]         VARCHAR (30)  NULL,
    [date_of_birth] DATE          NULL,
    [loyalty_tier]  VARCHAR (20)  DEFAULT ('Basic') NULL,
    [created_at]    DATETIME2 (7) DEFAULT (getdate()) NOT NULL,
    PRIMARY KEY CLUSTERED ([customer_id] ASC),
    UNIQUE NONCLUSTERED ([email] ASC)
);


GO

