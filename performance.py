import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
# Load the data
data = pd.read_csv("final_data.csv")

def prepare_data(data):
    # Count the unique teams per player per season
    team_counts = data.groupby(['Player', 'Season'])['Team'].nunique()

    # Filter to get only those with exactly two teams
    valid_transfers = team_counts[team_counts == 2].reset_index()

    # Merge this back with the original data to filter it
    filtered_data = pd.merge(data, valid_transfers, on=['Player', 'Season'], how='inner')

    # Sort the data to ensure the correct sequence of events for each player within each season
    filtered_data.sort_values(by=['Player', 'Season'], inplace=True)

    # Add a column to identify pre-trade and post-trade rows
    filtered_data['Transfer_Order'] = filtered_data.groupby(['Player', 'Season']).cumcount() + 1

    # Separate the pre-trade and post-trade data, using copy() to avoid SettingWithCopyWarning
    pre_trade_data = filtered_data[filtered_data['Transfer_Order'] == 1].copy()
    post_trade_data = filtered_data[filtered_data['Transfer_Order'] == 2].copy()

    # Drop the 'Transfer_Order' column as it is no longer needed
    pre_trade_data.drop(columns=['Transfer_Order'], inplace=True)
    post_trade_data.drop(columns=['Transfer_Order'], inplace=True)
    # List of columns that should remain only in the pre-trade data
    constant_columns = ['Height', 'Weight', 'Birth Date', 'Country', 'Years Experience', 'College',
                        'Player URL', 'Draft Round', 'Draft Pick in Round', 'Draft Overall Pick']

    # Rename columns in post_trade_data for differentiation
    post_trade_data.columns = ['Post_' + col if col not in ['Player', 'Season'] else col for col in
                               post_trade_data.columns]

    # Drop these columns from the post-trade data
    post_trade_data.drop(columns=['Post_' + col for col in constant_columns], inplace=True)

    # Merge pre-trade and post-trade data on Player and Season
    comparison_data = pd.merge(pre_trade_data, post_trade_data, on=['Player', 'Season'])
    # Include team information in the final output
    comparison_data['Team_From'] = comparison_data['Team_x']
    comparison_data['Team_To'] = comparison_data['Post_Team_x']

    return comparison_data

comparison_data = prepare_data(data)

def compare_stats_by_position(comparison_data):
    # Calculate differences in performance metrics
    comparison_data['Diff_Points'] = comparison_data['Post_Points'] - comparison_data['Points']
    comparison_data['Diff_Rebounds'] = comparison_data['Post_Rebounds'] - comparison_data['Rebounds']
    comparison_data['Diff_Assists'] = comparison_data['Post_Assists'] - comparison_data['Assists']
    comparison_data['Diff_Turnovers'] = comparison_data['Post_Turnovers'] - comparison_data['Turnovers']
    comparison_data['Diff_Blocks'] = comparison_data['Post_Blocks'] - comparison_data['Blocks']
    comparison_data['Diff_Steals'] = comparison_data['Post_Steals'] - comparison_data['Steals']

    # Group by position and calculate mean differences
    grouped_by_position_mean = comparison_data.groupby('Position').mean(numeric_only=True)[
        ['Diff_Points', 'Diff_Rebounds', 'Diff_Assists', 'Diff_Turnovers', 'Diff_Blocks', 'Diff_Steals']]

    # Group by position and calculate median differences
    grouped_by_position_median = comparison_data.groupby('Position').median(numeric_only=True)[
        ['Diff_Points', 'Diff_Rebounds', 'Diff_Assists', 'Diff_Turnovers', 'Diff_Blocks', 'Diff_Steals']]

    # Group by position and calculate standard deviation
    grouped_by_position_std = comparison_data.groupby('Position').std(numeric_only=True)[
        ['Diff_Points', 'Diff_Rebounds', 'Diff_Assists', 'Diff_Turnovers', 'Diff_Blocks', 'Diff_Steals']]
    # # Visualize the differences
    # # Plot the average performance differences by position
    # grouped_by_position_mean.plot(kind='bar', figsize=(12, 6), title='Average Performance Differences by Position')
    # plt.xlabel('Position')
    # plt.ylabel('Average Difference')
    # plt.grid(True)
    # plt.show()
    #
    # # Plot the median performance differences by position
    # grouped_by_position_median.plot(kind='bar', figsize=(12, 6), title='Median Performance Differences by Position')
    # plt.xlabel('Position')
    # plt.ylabel('Median Difference')
    # plt.grid(True)
    # plt.show()
    #
    # # Plot the standard deviation of performance differences by position
    # grouped_by_position_std.plot(kind='bar', figsize=(12, 6),
    #                              title='Standard Deviation of Performance Differences by Position')
    # plt.xlabel('Position')
    # plt.ylabel('Standard Deviation')
    # plt.grid(True)
    # plt.show()
    return ['Diff_Points', 'Diff_Rebounds', 'Diff_Assists', 'Diff_Turnovers', 'Diff_Blocks', 'Diff_Steals']
def compare_gamescore_by_position(compration_data):
    # Calculate differences in W/L metrics
    comparison_data['Diff_Total_Wins'] = comparison_data['Post_Total Wins'] - comparison_data['Total Wins']
    comparison_data['Diff_Total_Losses'] = comparison_data['Post_Total Losses'] - comparison_data['Total Losses']
    comparison_data['Diff_Wfirst5'] = comparison_data['Post_Wfirst5'] - comparison_data['Wfirst5']
    comparison_data['Diff_Lfirst5'] = comparison_data['Post_Lfirst5'] - comparison_data['Lfirst5']
    comparison_data['Diff_Wfirst10'] = comparison_data['Post_Wfirst10'] - comparison_data['Wfirst10']
    comparison_data['Diff_Lfirst10'] = comparison_data['Post_Lfirst10'] - comparison_data['Lfirst10']
    comparison_data['Diff_Wfirst15'] = comparison_data['Post_Wfirst15'] - comparison_data['Wfirst15']
    comparison_data['Diff_Lfirst15'] = comparison_data['Post_Lfirst15'] - comparison_data['Lfirst15']

    # Group by position and calculate mean, median, and standard deviation differences
    metrics = ['Diff_Total_Wins', 'Diff_Total_Losses', 'Diff_Wfirst5', 'Diff_Lfirst5', 'Diff_Wfirst10', 'Diff_Lfirst10',
               'Diff_Wfirst15', 'Diff_Lfirst15']
    grouped_by_position_mean = comparison_data.groupby('Position').mean(numeric_only=True)[metrics]
    grouped_by_position_median = comparison_data.groupby('Position').median(numeric_only=True)[metrics]
    grouped_by_position_std = comparison_data.groupby('Position').std(numeric_only=True)[metrics]

    # Visualize the differences
    # Plot the average W/L differences by position
    # grouped_by_position_mean.plot(kind='bar', figsize=(12, 6), title='Average W/L Differences by Position')
    # plt.xlabel('Position')
    # plt.ylabel('Average Difference')
    # plt.grid(True)
    # plt.show()
    #
    # # Plot the median W/L differences by position
    # grouped_by_position_median.plot(kind='bar', figsize=(12, 6), title='Median W/L Differences by Position')
    # plt.xlabel('Position')
    # plt.ylabel('Median Difference')
    # plt.grid(True)
    # plt.show()
    #
    # # Plot the standard deviation of W/L differences by position
    # grouped_by_position_std.plot(kind='bar', figsize=(12, 6), title='Standard Deviation of W/L Differences by Position')
    # plt.xlabel('Position')
    # plt.ylabel('Standard Deviation')
    # plt.grid(True)
    # plt.show()
    return ['Diff_Total_Wins', 'Diff_Total_Losses', 'Diff_Wfirst5', 'Diff_Lfirst5', 'Diff_Wfirst10', 'Diff_Lfirst10',
            'Diff_Wfirst15', 'Diff_Lfirst15']
def compare_stats_by_experience(comparison_data):
    # Calculate differences in performance metrics
    comparison_data['Diff_Points'] = comparison_data['Post_Points'] - comparison_data['Points']
    comparison_data['Diff_Rebounds'] = comparison_data['Post_Rebounds'] - comparison_data['Rebounds']
    comparison_data['Diff_Assists'] = comparison_data['Post_Assists'] - comparison_data['Assists']
    comparison_data['Diff_Turnovers'] = comparison_data['Post_Turnovers'] - comparison_data['Turnovers']
    comparison_data['Diff_Blocks'] = comparison_data['Post_Blocks'] - comparison_data['Blocks']
    comparison_data['Diff_Steals'] = comparison_data['Post_Steals'] - comparison_data['Steals']

    # Group by years of experience and calculate mean differences
    grouped_by_experience_mean = comparison_data.groupby('Years Experience').mean(numeric_only=True)[
        ['Diff_Points', 'Diff_Rebounds', 'Diff_Assists', 'Diff_Turnovers', 'Diff_Blocks', 'Diff_Steals']]

    # Group by years of experience and calculate median differences
    grouped_by_experience_median = comparison_data.groupby('Years Experience').median(numeric_only=True)[
        ['Diff_Points', 'Diff_Rebounds', 'Diff_Assists', 'Diff_Turnovers', 'Diff_Blocks', 'Diff_Steals']]

    # Group by years of experience and calculate standard deviation
    grouped_by_experience_std = comparison_data.groupby('Years Experience').std(numeric_only=True)[
        ['Diff_Points', 'Diff_Rebounds', 'Diff_Assists', 'Diff_Turnovers', 'Diff_Blocks', 'Diff_Steals']]

    # Visualize the differences
    # Plot the average performance differences by years of experience
    grouped_by_experience_mean.plot(kind='bar', figsize=(12, 6), title='Average Performance Differences by Experience')
    plt.xlabel('Years of Experience')
    plt.ylabel('Average Difference')
    plt.grid(True)
    plt.show()

    # Plot the median performance differences by years of experience
    grouped_by_experience_median.plot(kind='bar', figsize=(12, 6), title='Median Performance Differences by Experience')
    plt.xlabel('Years of Experience')
    plt.ylabel('Median Difference')
    plt.grid(True)
    plt.show()

    # Plot the standard deviation of performance differences by years of experience
    grouped_by_experience_std.plot(kind='bar', figsize=(12, 6), title='Standard Deviation of Performance Differences by Experience')
    plt.xlabel('Years of Experience')
    plt.ylabel('Standard Deviation')
    plt.grid(True)
    plt.show()

    return ['Diff_Points', 'Diff_Rebounds', 'Diff_Assists', 'Diff_Turnovers', 'Diff_Blocks', 'Diff_Steals']
def compare_gamescore_by_experience(comparison_data):
    # Calculate differences in W/L metrics
    comparison_data['Diff_Total_Wins'] = comparison_data['Post_Total Wins'] - comparison_data['Total Wins']
    comparison_data['Diff_Total_Losses'] = comparison_data['Post_Total Losses'] - comparison_data['Total Losses']
    comparison_data['Diff_Wfirst5'] = comparison_data['Post_Wfirst5'] - comparison_data['Wfirst5']
    comparison_data['Diff_Lfirst5'] = comparison_data['Post_Lfirst5'] - comparison_data['Lfirst5']
    comparison_data['Diff_Wfirst10'] = comparison_data['Post_Wfirst10'] - comparison_data['Wfirst10']
    comparison_data['Diff_Lfirst10'] = comparison_data['Post_Lfirst10'] - comparison_data['Lfirst10']
    comparison_data['Diff_Wfirst15'] = comparison_data['Post_Wfirst15'] - comparison_data['Wfirst15']
    comparison_data['Diff_Lfirst15'] = comparison_data['Post_Lfirst15'] - comparison_data['Lfirst15']

    # Group by years of experience and calculate mean, median, and standard deviation differences
    metrics = ['Diff_Total_Wins', 'Diff_Total_Losses', 'Diff_Wfirst5', 'Diff_Lfirst5', 'Diff_Wfirst10', 'Diff_Lfirst10',
               'Diff_Wfirst15', 'Diff_Lfirst15']
    grouped_by_experience_mean = comparison_data.groupby('Years Experience').mean(numeric_only=True)[metrics]
    grouped_by_experience_median = comparison_data.groupby('Years Experience').median(numeric_only=True)[metrics]
    grouped_by_experience_std = comparison_data.groupby('Years Experience').std(numeric_only=True)[metrics]

    # Visualize the differences
    # Plot the average W/L differences by years of experience
    grouped_by_experience_mean.plot(kind='bar', figsize=(12, 6), title='Average W/L Differences by Experience')
    plt.xlabel('Years of Experience')
    plt.ylabel('Average Difference')
    plt.grid(True)
    plt.show()

    # Plot the median W/L differences by years of experience
    grouped_by_experience_median.plot(kind='bar', figsize=(12, 6), title='Median W/L Differences by Experience')
    plt.xlabel('Years of Experience')
    plt.ylabel('Median Difference')
    plt.grid(True)
    plt.show()

    # Plot the standard deviation of W/L differences by years of experience
    grouped_by_experience_std.plot(kind='bar', figsize=(12, 6), title='Standard Deviation of W/L Differences by Experience')
    plt.xlabel('Years of Experience')
    plt.ylabel('Standard Deviation')
    plt.grid(True)
    plt.show()

    return ['Diff_Total_Wins', 'Diff_Total_Losses', 'Diff_Wfirst5', 'Diff_Lfirst5', 'Diff_Wfirst10', 'Diff_Lfirst10',
            'Diff_Wfirst15', 'Diff_Lfirst15']

def regression(comparison_data):
    # Select only the relevant columns for stats and W/L metrics
    stats_columns = compare_stats_by_experience(comparison_data)
    wl_columns = compare_gamescore_by_experience(comparison_data)

    # Generate interaction terms
    for i, col1 in enumerate(stats_columns):
        for col2 in stats_columns[i+1:]:
            interaction_term = f"{col1}:{col2}"
            comparison_data[interaction_term] = comparison_data[col1] * comparison_data[col2]

    # Combine stats and W/L metrics into a single DataFrame
    interaction_terms = [f"{col1}:{col2}" for i, col1 in enumerate(stats_columns) for col2 in stats_columns[i+1:]]
    analysis_data = comparison_data[stats_columns + interaction_terms + wl_columns]

    # Calculate the correlation matrix
    correlation_matrix = analysis_data.corr()

    # Function to perform regression analysis
    def perform_regression(dependent_var, independent_vars, data):
        X = data[independent_vars]
        y = data[dependent_var]
        X = sm.add_constant(X)  # Adds a constant term to the predictor
        model = sm.OLS(y, X).fit()
        return model.summary(), model.params

    # Perform regression for each W/L metric
    regression_results = {}
    betas = {}
    for dependent_var in wl_columns:
        regression_summary, beta_params = perform_regression(dependent_var, stats_columns + interaction_terms, analysis_data)
        regression_results[dependent_var] = regression_summary
        betas[dependent_var] = beta_params

    return correlation_matrix, regression_results, betas

# Prepare the comparison data
comparison_data = prepare_data(data)

# Execute the analysis
correlation_matrix, regression_results, betas = regression(comparison_data)

# Display the correlation matrix
print("Correlation Matrix:")
print(correlation_matrix)

# Display regression results
for metric, result in regression_results.items():
    print(f"\nRegression analysis for {metric}:")
    print(result)

# Display the betas
for metric, beta in betas.items():
    print(f"\nBeta coefficients for {metric}:")
    print(beta)