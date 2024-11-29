# R project to analyze world happiness data as downloaded from the World Happiness Report 2024

if (!require("corrplot")) {
  install.packages("corrplot")
}
library(corrplot)

# Set working directory to the folder where the CSV file is located
setwd("/Users/nickbochette/Downloads/TableauPortfolioProject")  

# Read the data from the CSV file into a data frame
happiness_data <- read.csv("happinessData.csv")  

# View the first few rows of the dataset to make sure it loaded correctly
print(head(happiness_data))
print(summary(happiness_data))

# # Check the structure of the data (column types, etc.)
str(happiness_data)
cat("\n")


# -----Identifying factors that predict happiness via correlation
# Select numeric columns for correlation analysis
numeric_columns <- happiness_data[, sapply(happiness_data, is.numeric)]
correlations <- cor(numeric_columns$LifeLadder, numeric_columns, use = "complete.obs")
names(correlations) <- colnames(numeric_columns) # Assign variable names to the correlation vector
sorted_correlations <- sort(correlations, decreasing = TRUE)
print(sorted_correlations)


# Create a bar plot to visualize the correlation between each variable and 'LifeLadder'.
# The plot helps identify which factors have the strongest relationship with happiness.
dev.new()
bar_midpoints <- barplot(
  sorted_correlations,  # The vector of sorted correlation coefficients.
  main = "Correlation with LifeLadder",  # Title of the plot.
  xlab = "Variables",  # X-axis label.
  ylab = "Correlation Coefficient",  # Y-axis label.
  col = "steelblue",  # Bar color.
  names.arg = names(sorted_correlations),  # Add variable names as x-axis labels.
  las = 2  # Rotate labels for better readability.
)

# Calculate the full correlation matrix of all numeric columns to understand relationships between variables.
# This will allow us to explore how each variable is correlated with every other variable.
correlation_matrix <- cor(numeric_columns, use = "complete.obs")  # Compute correlation matrix excluding missing data.

# Generate a heatmap of the correlation matrix to visually display the relationships between numeric variables.
# The heatmap provides an intuitive view of which variables are strongly or weakly correlated.
dev.new()
corrplot(correlation_matrix,  # Correlation matrix.
         method = "color",  # Use color to represent correlation strength.
         type = "upper",  # Display only the upper triangle of the matrix.
         tl.cex = 0.8)  # Adjust text label size for better readability.

# -----Build a linear regression model to quantify how each factor impacts happiness.
# Remove rows with missing values
cleaned_data <- na.omit(numeric_columns)

# Build the linear regression model
happiness_model <- lm(LifeLadder ~ ., data = cleaned_data)

# Display the model summary table
print("Linear Model Summary")
print(summary(happiness_model))

# ---Using coefficient table to make predictions
# Predict LifeLadder scores using the model
predicted_happiness <- predict(happiness_model, newdata = cleaned_data)
cleaned_data$PredictedLifeLadder <- predicted_happiness # Add predictions to the original dataset

# ---Check our model
# Plot Actual vs. Predicted LifeLadder scores
# Plot a scatterplot of actual vs. predicted happiness scores (LifeLadder vs. PredictedLifeLadder) to visually assess the model's prediction accuracy.
# The red reference line represents perfect predictions, where actual and predicted values are equal, helping to identify how well the model performs.
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
abline(a = 0, b = 1, col = "red", lwd = 2) # Add a reference line for perfect predictions


# Calculate Mean Squared Error (MSE) to quantify the average squared difference between actual and predicted happiness scores.
mse <- mean((cleaned_data$LifeLadder - cleaned_data$PredictedLifeLadder)^2)
# Calculate Root Mean Squared Error (RMSE) to provide a more interpretable measure of prediction accuracy by taking the square root of MSE.
rmse <- sqrt(mse) 

# Print performance metrics
cat("\nMean Squared Error (MSE):", mse, "\n")
cat("Root Mean Squared Error (RMSE):", rmse, "\n")


# ---Create a residual plot:
# Residuals (differences between actual and predicted values)
residuals <- cleaned_data$LifeLadder - cleaned_data$PredictedLifeLadder

# Plot residuals
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










#  2. Analyze Trends in Happiness Over Time

# 	•	Objective: Examine how happiness scores (LifeLadder) have changed across years for different countries or regions.
# 	•	Approach:
# 	•	Group the data by Year and calculate the average happiness score for each year.
# 	•	Analyze trends for individual countries or compare regions (e.g., continents).
# Example Tasks:
# 	•	Plot a time series of global average happiness over the years.
# 	•	Highlight countries with the largest increase or decrease in happiness over time.


#  3. Study the Impact of Economic Factors on Happiness

# 	•	Objective: Investigate how economic indicators, such as LogGDPpc, relate to happiness.
# 	•	Approach:
# 	•	Segment countries into income groups (low, middle, high) based on LogGDPpc and compare average LifeLadder scores.
# 	•	Explore whether diminishing returns exist (e.g., does GDP have less impact on happiness in wealthier countries?).
# Example Tasks:
# 	•	Create a boxplot comparing LifeLadder across income groups.
# 	•	Fit a nonlinear regression model to explore diminishing returns of GDP.


# 4. Compare Regional Happiness Levels

# 	•	Objective: Identify regional differences in happiness and other variables.
# 	•	Approach:
# 	•	Add a region column (manually or using a mapping) to group countries by continent or region.
# 	•	Compare average LifeLadder and other variables (e.g., SocialSupport, PercievedCorruption) across regions.
# Example Tasks:
# 	•	Create a bar plot showing average happiness by region.
# 	•	Find regions with the lowest and highest scores for key variables like Generosity or ChoiceFreedom.


# 5. Explore Relationships Between Positive and Negative Affect

# 	•	Objective: Analyze how PositiveAffect and NegativeAffect interact and whether they influence happiness differently.
# 	•	Approach:
# 	•	Calculate correlations between affect variables and LifeLadder.
# 	•	Visualize the distribution of PositiveAffect and NegativeAffect by region or income level.
# Example Tasks:
# 	•	Plot PositiveAffect vs. NegativeAffect and color points by region or income.
# 	•	Determine which is more strongly correlated with LifeLadder.