-- COVID-19 Data Analysis Project
-- Last Updated: 2024.11.17
-- Purpose: Analysis of global COVID-19 case data, vaccination rates, and demographic correlations

-- =============================================
-- Database Schema and Table Creation
-- =============================================

-- Main table for COVID death statistics and demographic data
CREATE TABLE CovidDeaths (
    isocode text, 
    continent text, 
    location text, 
    date date,
    totalTests real,
    newTests real,
    ttPerThousand real,
    ntPerThousand real,
    nt_smoothed real,
    ntPerThousand_smoothed real,
    positiveRate real,
    testsPerCase real,
    testsUnits real,
    totalVaxes real,
    peopleVaxxed real,
    peopleFullyVaxxed real,
    totalBoosters real,
    newVaxes real,
    newvaxxes_smoothed real,
    totalVaxesPerHundred real,
    pplVaxxedPerHundred real,
    pplFullyVaxxedPerHundred real,
    totalBoostersPerHundred real,
    newVaxesPerMillion_smoothed real,
    newPplVaxxed_smoothed real,
    newPplVaxxedPerHundred_smoothed real,
    stringencyIndex real,
    populationDensity real,
    medianAge real,
    aged65plus real,
    aged70plus real,
    gdpPerCapita real,
    extremePoverty real,
    cardiovascDeathRate real,
    diabetesPrevelance real,
    femaleSmokers real,
    maleSmokers real,
    handwashingFacilities real,
    hospitalBedsPerThousand real,
    lifeExpectancy real,
    humanDevelopmentIndex real,
    excess_mortality_cumulative_absolute real,
    excess_mortality_cumulative real,
    excess_mortality real,
    excess_mortality_cumulative_per_million real
)

-- Separate table for vaccination tracking
CREATE TABLE CovidVax (
    isocode text,
    continent text,
    location text,
    date date,
    population integer,
    totalCases integer,
    newCases integer,
    newCases_smoothed real,
    totalDeaths integer,
    newDeaths integer,
    newDeaths_smoothed real,
    totalCasesPerMillion real, 
    newCasesPerMillion real,
    newCasesPerMillion_smoothed real,
    totalDeathsPerMillion real,
    newDeathsPerMillion real,
    ndpm_smoothed real,
    reproductionRate real,
    icuPatients integer,
    icuPatientsPerMillion real,
    hospPatients integer,
    hpPerMillion real,
    weeklyIcuAdmissions real,
    wIcuaPerMillion real,
    weeklyHospitalAdmissions real,
    whaPerMillion real,
    totalTests integer
)

-- =============================================
-- Data Type Modifications
-- =============================================

-- Updating data types for accuracy and consistency
ALTER TABLE covidvaccinations
ALTER COLUMN testsUnits TYPE text

ALTER TABLE CovidDeaths
ALTER COLUMN totalCases TYPE real,
ALTER COLUMN newCases TYPE real,
ALTER COLUMN totalDeaths TYPE real,
ALTER COLUMN newDeaths TYPE real,
ALTER COLUMN icuPatients TYPE real,
ALTER COLUMN hospPatients TYPE real,
ALTER COLUMN totalTests TYPE real;

-- =============================================
-- Basic Data Analysis Queries
-- =============================================

-- Initial data overview
SELECT location, date, totalCases, newCases, totalDeaths, population
FROM coviddeaths 
ORDER BY 1,2;

-- Death rate calculation by location
SELECT location, date, totalCases, totalDeaths, 
    (totalDeaths::numeric / totalCases::numeric) * 100 as DeathPercentage
FROM coviddeaths
ORDER BY 1, 2;

-- US-specific death rate analysis
SELECT location, date, totalCases, totalDeaths, 
    (totalDeaths::numeric / totalCases::numeric) * 100 as DeathPercentage
FROM coviddeaths
WHERE location like '%States%'
ORDER BY 1, 2;

-- Infection rate relative to population
SELECT location, date, population, totalCases, 
    (totalCases / population) * 100 as InfectionRate
FROM coviddeaths
WHERE location like '%States'
ORDER BY 1, 2;

-- =============================================
-- Advanced Analytics
-- =============================================

-- Identifying highest infection rates globally
SELECT location, population, 
    MAX(totalCases) AS highestInfectionCount,
    MAX((totalCases / population)) * 100 as PercentPopulationInfected
FROM coviddeaths
GROUP BY location, population
ORDER BY PercentPopulationInfected desc;

-- Death counts by country (excluding null data)
SELECT location, CAST(population AS bigint),
    MAX(CAST(totalDeaths AS bigint)) AS maxDeathCount
FROM coviddeaths
WHERE continent IS NOT NULL AND totalDeaths IS NOT NULL
GROUP BY location, population
ORDER BY maxDeathCount desc;

-- Continental analysis including socioeconomic groupings
SELECT location, MAX(CAST(totalDeaths AS bigint)) AS maxDeathCount
FROM coviddeaths
WHERE continent IS NULL
GROUP BY location
ORDER BY maxDeathCount desc;

-- Pure continental analysis (excluding socioeconomic groupings)
SELECT location, MAX(CAST(totalDeaths AS bigint)) AS maxDeathCount
FROM coviddeaths
WHERE continent IS NULL 
    AND location NOT IN ('High income', 'Upper middle income', 'Lower middle income','Low income')
GROUP BY location
ORDER BY maxDeathCount desc;

-- =============================================
-- Global Statistics
-- =============================================

-- Daily global statistics
SELECT date, SUM(newCases), SUM(newDeaths),
    (SUM(newDeaths) / SUM(newCases)) * 100 AS GlobalDeathRate
FROM coviddeaths
WHERE continent IS NOT NULL
GROUP BY date
ORDER BY 1, 2;

-- Overall global totals
SELECT SUM(newCases), SUM(newDeaths),
    (SUM(newDeaths) / SUM(newCases)) * 100 AS GlobalDeathRate
FROM coviddeaths
WHERE continent IS NOT NULL
ORDER BY 1, 2;

-- =============================================
-- Vaccination Analysis
-- =============================================

-- Join validation between death and vaccination data
SELECT * 
FROM coviddeaths dea
JOIN covidvaccinationdata vax
    ON dea.location = vax.location
    AND dea.date = vax.date;

-- Vaccination progress tracking
SELECT dea.continent, dea.location, dea.date,
    CAST(dea.population AS bigint), vax.newVaxes
FROM coviddeaths dea
JOIN covidvaccinationdata vax
    ON dea.location = vax.location
    AND dea.date = vax.date
WHERE dea.continent IS NOT NULL
ORDER BY 1,2,3;

-- Running vaccination totals by location
SELECT dea.continent, dea.location, dea.date,
    CAST(dea.population AS bigint), vax.newVaxes,
    SUM(newVaxes) OVER (PARTITION BY dea.location ORDER BY dea.location, dea.date) as RollingPplVaccinated
FROM coviddeaths dea
JOIN covidvaccinationdata vax
    ON dea.location = vax.location
    AND dea.date = vax.date
WHERE dea.continent IS NOT NULL
ORDER BY 1,2,3;

-- =============================================
-- Population Vaccination Analysis
-- =============================================

-- Using CTE for vaccination percentage calculation
WITH PopVsVax (continent, location, date, population, newVaxes, RollingPplVaccinated)
AS
(
    SELECT dea.continent, dea.location, dea.date,
        CAST(dea.population AS bigint), vax.newVaxes,
        SUM(newVaxes) OVER (PARTITION BY dea.location ORDER BY dea.location, dea.date) as RollingPplVaccinated
    FROM coviddeaths dea
    JOIN covidvaccinationdata vax
        ON dea.location = vax.location
        AND dea.date = vax.date
    WHERE dea.continent IS NOT NULL
)
SELECT *, (RollingPplVaccinated/population)*100 AS VaxRatioByPop
FROM PopVsVax;

-- Using temp table for vaccination percentage calculation
DROP TABLE IF EXISTS PercentPopulationVaccinated;
CREATE TEMPORARY TABLE PercentPopulationVaccinated
(
    continent text,
    location text,
    date date,
    population real,
    newVaxes real,
    RollingPplVaccinated real
);

INSERT INTO PercentPopulationVaccinated
SELECT dea.continent, dea.location, dea.date,
    CAST(dea.population AS bigint), vax.newVaxes,
    SUM(newVaxes) OVER (PARTITION BY dea.location ORDER BY dea.location, dea.date) as RollingPplVaccinated
FROM coviddeaths dea
JOIN covidvaccinationdata vax
    ON dea.location = vax.location
    AND dea.date = vax.date
WHERE dea.continent IS NOT NULL;

SELECT *, (RollingPplVaccinated/population)*100 AS VaxRatioByPop
FROM PercentPopulationVaccinated;

-- =============================================
-- View Creation for Visualization
-- =============================================

-- Basic vaccination progress view
CREATE VIEW PercentPopulationVaccinated AS
SELECT dea.continent, dea.location, dea.date,
    CAST(dea.population AS bigint), vax.newVaxes,
    SUM(newVaxes) OVER (PARTITION BY dea.location ORDER BY dea.location, dea.date) as RollingPplVaccinated
FROM coviddeaths dea
JOIN covidvaccinationdata vax
    ON dea.location = vax.location
    AND dea.date = vax.date
WHERE dea.continent IS NOT NULL;

-- Continental case tracking (2023 onwards)
SELECT continent, location, date,
    cast(population AS bigint),
    CAST(totalcases AS BIGINT),
    CAST(totaldeaths AS BIGINT),
    totalcasespermillion,
    newdeathspermillion
FROM coviddeaths
WHERE continent is NULL
    AND totalcases is not NULL
    AND date>='2023-01-01'::date
ORDER BY location, date;

-- Comprehensive location-based analysis view
CREATE VIEW Deaths_and_Vaccinations_by_Location AS
SELECT dea.continent, dea.location, dea.date,
    cast(dea.population AS bigint),
    vax.populationDensity,
    CAST(dea.totalcases AS BIGINT),
    CAST(dea.totaldeaths AS BIGINT),
    dea.totalcasespermillion,
    dea.newdeathspermillion,
    vax.totalTests,
    (vax.ttPerThousand * 1000) AS totaltestspermillion,
    vax.positiveRate,
    vax.testsPerCase,
    CAST(vax.totalVaxes AS BIGINT),
    CAST(vax.peopleVaxxed AS BIGINT),
    CAST(vax.peopleFullyVaxxed AS BIGINT),
    CAST(vax.totalBoosters AS BIGINT),
    vax.gdpPerCapita,
    vax.femaleSmokers,
    vax.maleSmokers,
    vax.lifeExpectancy,
    vax.humanDevelopmentIndex
FROM coviddeaths dea
JOIN covidvaccinationdata vax
    ON dea.location = vax.location
    AND dea.date = vax.date
WHERE dea.continent is not NULL
    AND dea.totalcases is not NULL;

-- =============================================
-- Tableau Visualization Queries
-- =============================================

-- Global summary statistics
SELECT CAST(SUM(newCases) AS BIGINT) as total_cases,
    CAST(SUM(newDeaths) AS BIGINT) as total_deaths,
    (SUM(newDeaths) / SUM(newCases)) * 100 AS GlobalDeathRate
FROM coviddeaths
WHERE continent IS NOT NULL
ORDER BY 1, 2;

-- Continental death totals (excluding aggregate categories)
SELECT location,
    CAST(SUM(newDeaths) AS BIGINT) AS TotalGlobalDeaths
FROM coviddeaths
WHERE continent IS NULL
    AND location NOT IN ('World', 'European Union', 'International',
        'High income', 'Upper middle income', 'Lower middle income', 'Low income')
GROUP BY location
ORDER BY TotalGlobalDeaths desc;

-- Peak infection rates by location
SELECT location,
    CAST(population as BIGINT),
    CAST(MAX(totalcases) AS BIGINT) as highest_infection_count,
    MAX((totalcases/population))*100 as percent_population_infected
FROM coviddeaths
GROUP BY location, population
ORDER BY percent_population_infected DESC;

-- Temporal infection rates by location
SELECT location,
    CAST(population as BIGINT),
    date,
    CAST(MAX(totalcases) AS BIGINT) as highest_infection_count,
    MAX((totalcases/population))*100 as percent_population_infected
FROM coviddeaths
WHERE totalcases IS NOT NULL
GROUP BY location, population, date
ORDER BY percent_population_infected DESC;