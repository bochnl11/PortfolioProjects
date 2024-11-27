# R project to analyze world happiness data as downloaded from the World Happiness Report 2024



# Set working directory to the folder where the CSV file is located
setwd("/Users/nickbochette/Downloads/TableauPortfolioProject")  

# Read the data from the CSV file into a data frame
happiness_data <- read.csv("happinessData.csv")  

# View the first few rows of the dataset to make sure it loaded correctly
print(head(happiness_data))

# # Summary statistics to understand the data better
print(summary(happiness_data))

# # Check the structure of the data (column types, etc.)
str(happiness_data)


