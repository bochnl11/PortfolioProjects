# R project to analyze world happiness data as downloaded from the World Happiness Report 2024

if (!require("corrplot")) {
  install.packages("corrplot")
}
library(corrplot)

# Set working directory to the folder where the CSV file is located
setwd("/Users/nickbochette/Downloads/TableauPortfolioProject")  

# Read the data from the CSV file into a data frame
happiness_data <- read.csv("happinessData.csv")  

# # View the first few rows of the dataset to make sure it loaded correctly
# print(head(happiness_data))

# # # Summary statistics to understand the data better
# print(summary(happiness_data))

# # Check the structure of the data (column types, etc.)
str(happiness_data)
print("")


# -----Identifying factors that predict happiness via correlation
# Select numeric columns for correlation analysis
numeric_columns <- happiness_data[, sapply(happiness_data, is.numeric)]
correlations <- cor(numeric_columns$LifeLadder, numeric_columns, use = "complete.obs")
names(correlations) <- colnames(numeric_columns) # Assign variable names to the correlation vector

sorted_correlations <- sort(correlations, decreasing = TRUE)
print(sorted_correlations)


# Create a bar plot and save bar midpoints
bar_midpoints <- barplot(
  sorted_correlations,
  main = "Correlation with LifeLadder",
  xlab = "Variables",
  ylab = "Correlation Coefficient",
  col = "steelblue",
  names.arg = names(sorted_correlations),  # Add variable names as labels
  las = 2  # Rotate labels for readability
)


# # Calculate a full correlation matrix
# correlation_matrix <- cor(numeric_columns, use = "complete.obs")

# # Create a correlation heatmap
# corrplot(correlation_matrix, method = "color", type = "upper", tl.cex = 0.8)

















# 1. Identify Factors That Predict Happiness

# 	•	Objective: Determine which variables (e.g., LogGDPpc, SocialSupport, LifeExpectancy, etc.) have the strongest correlation with the happiness score (LifeLadder).
# 	•	Approach:
# 	•	Use correlation analysis to see how strongly each variable is associated with LifeLadder.
# 	•	Build a linear regression model to quantify how each factor impacts happiness.
# Example Tasks:
# 	•	Find the top 3 factors influencing happiness.
# 	•	Visualize relationships using scatter plots and trendlines.


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