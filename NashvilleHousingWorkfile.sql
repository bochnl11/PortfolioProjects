------------------------------------
--Data cleaning housing data project
------------------------------------

SELECT *
FROM nashvillehousingdata;


--Standardize date format
SELECT sale_date
FROM nashvillehousingdata;

SELECT sale_date, sale_date::DATE AS converted_date
FROM nashvillehousingdata;

UPDATE nashvillehousingdata
SET sale_date = sale_date::DATE;


--Populate property address
SELECT property_address 
FROM nashvillehousingdata;
WHERE property_address IS NULL
ORDER BY parcel_id

SELECT a.parcel_id, a.property_address, b.parcel_id, b.property_address, COALESCE(a.property_address, b.property_address)
FROM nashvillehousingdata as a
JOIN nashvillehousingdata as b
    ON a.parcel_id = b.parcel_id
    AND a.unique_id <> b.unique_id
WHERE a.property_address IS NULL;


--Update not requiring joins
UPDATE nashvillehousingdata AS a
SET property_address = COALESCE(a.property_address, b.property_address)
FROM nashvillehousingdata AS b
WHERE a.parcel_id = b.parcel_id
  AND a.unique_id <> b.unique_id
  AND a.property_address IS NULL;


--Breaking out address into individual columns
SELECT property_address
FROM nashvillehousingdata;

SELECT 
    substring(property_address FROM 1 FOR position(',' IN property_address) - 1) AS address,
    substring(property_address FROM position(',' IN property_address) + 1) AS city
FROM nashvillehousingdata;

ALTER TABLE nashvillehousingdata
    ADD property_streetaddr TEXT;

UPDATE nashvillehousingdata
SET property_streetaddr = substring(property_address FROM 1 FOR position(',' IN property_address) - 1);


ALTER TABLE nashvillehousingdata
    ADD property_city TEXT;

UPDATE nashvillehousingdata
SET property_city = substring(property_address FROM position(',' IN property_address) + 1);

    --alternate delimiting select query
SELECT 
    SPLIT_PART(owner_address, ',', 1) AS streetAddr,
	SPLIT_PART(owner_address, ',', 2) AS cityAddr,
	SPLIT_PART(owner_address, ',', 3) AS stAddr
FROM nashvillehousingdata;

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


--Normalize format of Sold as Vacant field
SELECT DISTINCT(sold_as_vacant), COUNT(sold_as_vacant)
from nashvillehousingdata
GROUP BY sold_as_vacant
ORDER BY 2;

SELECT sold_as_vacant,
CASE
    WHEN sold_as_vacant = 'N' THEN 'No'
    WHEN sold_as_vacant = 'Y' THEN 'Yes'
    ELSE
        sold_as_vacant
END
FROM nashvillehousingdata

UPDATE nashvillehousingdata
SET sold_as_vacant = 
    CASE
        WHEN sold_as_vacant = 'N' THEN 'No'
        WHEN sold_as_vacant = 'Y' THEN 'Yes'
        ELSE
            sold_as_vacant
    END



--Remove duplicates
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


    --Using unique_id to group duplicates
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

    --If full-on deletion is required
DELETE FROM nashvillehousingdata
WHERE unique_id IN (SELECT unique_id FROM RowNumCTE);


    --Alternatively, create a custom view with no duplicates:
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


--Delete unused columns
ALTER TABLE nashvillehousingdata
DROP COLUMN owner_address,
DROP COLUMN tax_district,
DROP COLUMN property_address;