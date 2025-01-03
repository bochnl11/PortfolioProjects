/*
Nashville Housing Data Cleanup
Purpose: Standardize and clean Nashville housing market data for analysis
Author: [Your name]
Last Updated: [Current date]
*/

-- SECTION 1: Initial Data Review
-- Quick look at full dataset to assess cleanup needs
SELECT *
FROM nashvillehousingdata;


-- SECTION 2: Date Standardization
-- Converting messy datetime strings to proper DATE format
SELECT sale_date
FROM nashvillehousingdata;

SELECT sale_date, sale_date::DATE AS converted_date
FROM nashvillehousingdata;

UPDATE nashvillehousingdata
SET sale_date = sale_date::DATE;


-- SECTION 3: Property Address Cleanup
-- Fill NULL property addresses using matching parcel IDs
-- First, identify NULL addresses
SELECT property_address 
FROM nashvillehousingdata
WHERE property_address IS NULL
ORDER BY parcel_id;

-- Match properties with same parcel_id to find missing addresses
SELECT a.parcel_id, a.property_address, b.parcel_id, b.property_address, COALESCE(a.property_address, b.property_address)
FROM nashvillehousingdata as a
JOIN nashvillehousingdata as b
    ON a.parcel_id = b.parcel_id
    AND a.unique_id <> b.unique_id
WHERE a.property_address IS NULL;

-- Update NULL addresses with matched values
UPDATE nashvillehousingdata AS a
SET property_address = COALESCE(a.property_address, b.property_address)
FROM nashvillehousingdata AS b
WHERE a.parcel_id = b.parcel_id
  AND a.unique_id <> b.unique_id
  AND a.property_address IS NULL;


-- SECTION 4: Address Component Separation
-- Break down property addresses into street and city
SELECT property_address
FROM nashvillehousingdata;

-- Test address splitting logic
SELECT 
    substring(property_address FROM 1 FOR position(',' IN property_address) - 1) AS address,
    substring(property_address FROM position(',' IN property_address) + 1) AS city
FROM nashvillehousingdata;

-- Create and populate street address column
ALTER TABLE nashvillehousingdata
    ADD property_streetaddr TEXT;

UPDATE nashvillehousingdata
SET property_streetaddr = substring(property_address FROM 1 FOR position(',' IN property_address) - 1);

-- Create and populate city column
ALTER TABLE nashvillehousingdata
    ADD property_city TEXT;

UPDATE nashvillehousingdata
SET property_city = substring(property_address FROM position(',' IN property_address) + 1);

-- Split owner addresses into components using alternate method
SELECT 
    SPLIT_PART(owner_address, ',', 1) AS streetAddr,
    SPLIT_PART(owner_address, ',', 2) AS cityAddr,
    SPLIT_PART(owner_address, ',', 3) AS stAddr
FROM nashvillehousingdata;

-- Create and populate owner address components
ALTER TABLE nashvillehousingdata
    ADD owner_streetaddr TEXT;

UPDATE nashvillehousingdata
SET owner_streetaddr = SPLIT_PART(owner_address, ',', 1);

ALTER TABLE nashvillehousingdata
    ADD owner_city TEXT;

UPDATE nashvillehousingdata
SET owner_city = SPLIT_PART(owner_address, ',', 2);

ALTER TABLE nashvillehousingdata
    ADD owner_st TEXT;

UPDATE nashvillehousingdata
SET owner_st = SPLIT_PART(owner_address, ',', 3);


-- SECTION 5: Data Standardization
-- Standardize 'Sold as Vacant' field values from Y/N to Yes/No
SELECT DISTINCT(sold_as_vacant), COUNT(sold_as_vacant)
from nashvillehousingdata
GROUP BY sold_as_vacant
ORDER BY 2;

-- Test standardization logic
SELECT sold_as_vacant,
CASE
    WHEN sold_as_vacant = 'N' THEN 'No'
    WHEN sold_as_vacant = 'Y' THEN 'Yes'
    ELSE
        sold_as_vacant
END
FROM nashvillehousingdata;

-- Apply standardization
UPDATE nashvillehousingdata
SET sold_as_vacant = 
    CASE
        WHEN sold_as_vacant = 'N' THEN 'No'
        WHEN sold_as_vacant = 'Y' THEN 'Yes'
        ELSE
            sold_as_vacant
    END;


-- SECTION 6: Duplicate Management
-- Identify duplicate records based on key fields
WITH RowNumCTE AS(
SELECT *,
    ROW_NUMBER() OVER (
        PARTITION BY parcel_id, property_address, sale_price, sale_date, legal_reference 
        ORDER BY unique_id
    ) AS row_num
FROM nashvillehousingdata
)

SELECT * 
FROM RowNumCTE
WHERE row_num > 1
ORDER BY property_address;

-- Get unique_ids of duplicates for potential deletion
WITH RowNumCTE AS (
    SELECT unique_id
    FROM (
        SELECT unique_id,
            ROW_NUMBER() OVER (
                PARTITION BY parcel_id, property_address, sale_price, sale_date, legal_reference 
                ORDER BY unique_id
            ) AS row_num
        FROM nashvillehousingdata
    ) subquery
    WHERE row_num > 1
)
SELECT *
FROM nashvillehousingdata
WHERE unique_id IN (SELECT unique_id FROM RowNumCTE);

-- Optional: Delete duplicate records
DELETE FROM nashvillehousingdata
WHERE unique_id IN (SELECT unique_id FROM RowNumCTE);

-- Alternative: Create view without duplicates
CREATE VIEW nashvillehousingdata_no_duplicates AS
WITH RowNumCTE AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY parcel_id, property_address, sale_price, sale_date, legal_reference 
            ORDER BY unique_id
        ) AS row_num
    FROM nashvillehousingdata
)
SELECT *
FROM RowNumCTE
WHERE row_num = 1;


-- SECTION 7: Cleanup
-- Remove redundant columns after data extraction
ALTER TABLE nashvillehousingdata
DROP COLUMN owner_address,
DROP COLUMN tax_district,
DROP COLUMN property_address;