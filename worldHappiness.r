# World Happiness Analysis
# Author: Nick Bochette
# Analysis of World Happiness Report 2024 data to identify
# factors influencing global happiness scores
# Last updated: January 2025

# --- Library Management ---------------------------------------------
# Install required packages if not already present
if (!require("corrplot")) install.packages("corrplot")
if (!require("countrycode")) install.packages("countrycode")

# Load necessary libraries
library(countrycode)
library(corrplot)
library(dplyr)
library(ggplot2)

# --- Data Import & Initial Exploration ----------------------------------
# Set working directory to data location
setwd("/Users/nickbochette/Downloads/TableauPortfolioProject")

# Import happiness dataset
happiness_data <- read.csv("happinessData.csv")

# Perform initial data checks
print(head(happiness_data))
print(summary(happiness_data))
str(happiness_data)
cat("\n")

# --- Correlation Analysis -------------------------------------------------
# Extract numeric columns for correlation analysis
numeric_columns <- happiness_data[, sapply(happiness_data, is.numeric)]

# Calculate correlations with Life Ladder (happiness score)
correlations <- cor(
  numeric_columns$LifeLadder,
  numeric_columns,
  use = "complete.obs"
)
names(correlations) <- colnames(numeric_columns)
sorted_correlations <- sort(correlations, decreasing = TRUE)
print(sorted_correlations)

# Visualize correlations with happiness scores
dev.new()
bar_midpoints <- barplot(
  sorted_correlations,
  main = "Correlation with LifeLadder",
  xlab = "Variables",
  ylab = "Correlation Coefficient",
  col = "steelblue",
  names.arg = names(sorted_correlations),
  las = 2
)

# Generate correlation matrix heatmap for all variables
correlation_matrix <- cor(numeric_columns, use = "complete.obs")
dev.new()
corrplot(
  correlation_matrix,
  method = "color",
  type = "upper",
  tl.cex = 0.8
)

# --- Linear Regression Analysis -----------------------------------------
# Prepare data by removing missing values
cleaned_data <- na.omit(numeric_columns)

# Build and evaluate regression model
happiness_model <- lm(LifeLadder ~ ., data = cleaned_data)
print("Linear Model Summary")
print(summary(happiness_model))

# Generate predictions using the model
predicted_happiness <- predict(happiness_model, newdata = cleaned_data)
cleaned_data$PredictedLifeLadder <- predicted_happiness

# --- Model Evaluation ---------------------------------------------------------
# Create actual vs predicted values scatter plot
dev.new()
plot(
  cleaned_data$LifeLadder,
  cleaned_data$PredictedLifeLadder,
  main = "Actual vs. Predicted Happiness Scores",
  xlab = "Actual Happiness (LifeLadder)",
  ylab = "Predicted Happiness",
  col = "steelblue",
  pch = 16
)
abline(a = 0, b = 1, col = "red", lwd = 2)

# Calculate error metrics
mse <- mean((cleaned_data$LifeLadder - cleaned_data$PredictedLifeLadder)^2)
rmse <- sqrt(mse)
cat("\nMean Squared Error (MSE):", mse, "\n")
cat("Root Mean Squared Error (RMSE):", rmse, "\n")

# Generate residual plot for model diagnostics
residuals <- cleaned_data$LifeLadder - cleaned_data$PredictedLifeLadder
dev.new()
plot(
  cleaned_data$PredictedLifeLadder,
  residuals,
  main = "Residual Plot",
  xlab = "Predicted Happiness",
  ylab = "Residuals",
  col = "darkorange",
  pch = 16
)
abline(h = 0, col = "red", lwd = 2)

# --- Temporal Analysis --------------------------------------------------------
# Calculate yearly happiness averages
average_happiness_by_year <- happiness_data %>%
  group_by(Year) %>%
  summarize(AverageHappiness = mean(LifeLadder, na.rm = TRUE))
print(average_happiness_by_year)

# Calculate country-specific happiness averages
average_happiness_by_country <- happiness_data %>%
  group_by(Country) %>%
  summarize(AverageHappiness = mean(LifeLadder, na.rm = TRUE))
print(head(average_happiness_by_country))

# --- Country Comparison Analysis ----------------------------------------------
# Compare happiness trends for selected countries
selected_countries <- happiness_data %>%
  filter(Country %in% c(
    "United States",
    "Canada",
    "Germany",
    "Brazil",
    "Australia"
  ))

# Visualize country-specific trends
print(
  ggplot(selected_countries, aes(x = Year, y = LifeLadder, color = Country)) +
    geom_line() +
    geom_point() +
    labs(
      title = "Happiness Trends in Selected Countries",
      x = "Year",
      y = "Happiness Score"
    ) +
    theme_minimal() +
    theme(plot.margin = margin(1, 1, 1.5, 1, "cm"))
)

# --- Regional Analysis -------------------------------------------------------
# Add continent classification to dataset
suppressWarnings({
  happiness_data$Continent <- countrycode(
    happiness_data$Country,
    origin = "country.name",
    destination = "continent"
  )
})

# Check for unmatched countries
missing_continents <- happiness_data[is.na(happiness_data$Continent), ]
print(missing_continents)

# Verify continent assignments
if (any(is.na(happiness_data$Continent))) {
  missing_continents <- happiness_data[is.na(happiness_data$Continent), ]
  print("Unmatched countries after manual correction:")
  print(missing_continents)
} else {
  print("All countries successfully assigned to continents!")
}

# Calculate and visualize regional metrics
regional_averages <- happiness_data %>%
  group_by(Continent) %>%
  summarize(
    AvgHappiness = mean(LifeLadder, na.rm = TRUE),
    AvgGDP = mean(LogGDPpc, na.rm = TRUE)
  )

# Create regional comparison plot
print(
  ggplot(
    regional_averages,
    aes(x = Continent, y = AvgHappiness, fill = Continent)
  ) +
    geom_bar(stat = "identity") +
    labs(
      title = "Average Happiness by Continent",
      x = "Continent",
      y = "Average Happiness Score"
    ) +
    theme_minimal()
)

# Generate Europe-specific correlation analysis
europe_data <- happiness_data %>% filter(Continent == "Europe")
cor_matrix <- cor(
  europe_data %>% select(-Country, -Continent, -Year),
  use = "complete.obs"
)
corrplot(
  cor_matrix,
  method = "color",
  type = "upper",
  title = "Correlation Heatmap (Europe)"
)