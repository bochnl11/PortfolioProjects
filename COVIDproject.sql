--Create a view to store data for later visualizations 
CREATE VIEW PercentPopulationVaccinated AS
    SELECT dea.continent, dea.location, dea.date, CAST(dea.population AS bigint), vax.newVaxes, 
            SUM(newVaxes) OVER (PARTITION BY dea.location ORDER BY dea.location, dea.date) as RollingPplVaccinated
    FROM coviddeaths dea
    JOIN covidvaccinationdata vax
        ON dea.location = vax.location
        AND dea.date = vax.date
    WHERE dea.continent IS NOT NULL
    --WHERE dea.location = 'Canada'
    --ORDER BY 1,2,3