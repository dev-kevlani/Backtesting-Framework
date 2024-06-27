import pandas as pd
import matplotlib.pyplot as plt

def process_results(results):
    """
    Process trading results and create a DataFrame summarizing trade data.

    Args:
    - results (list): List of tuples where each tuple contains day_trades (list of trades)
                      and uncounted_trades (list of uncounted trades).

    Returns:
    - df_combined (DataFrame): Combined DataFrame containing all trade data.
    - total_trades (int): Total number of trades processed.
    - count_positive (int): Number of trades with positive net profit.
    - accuracy (float): Percentage of trades with positive net profit.
    """
    all_trade_dicts = []

    for result in results:
        if result is not None:
            day_trades, uncounted_trades = result
            if day_trades is not None:
                for trade in day_trades:
                    # Create a dictionary for each trade containing trade details
                    trade_dict = {
                        'entry_timestamp': trade['entry_timestamp'],
                        'exit_timestamp': trade['exit_timestamp'],
                        'margin_used': trade['margin_used'],
                        'entry_premium': trade['entry_premium'],
                        'exit_premium': trade['exit_premium'],
                        'strategy_type': trade['strategy_type'], 
                        'exit_reason': trade['exit_reason'],
                        'pnl': trade['pnl'],
                        'transaction_cost': trade['transaction_cost'],
                        'uncounted_trades': uncounted_trades
                    }
                    
                    # Add details for each leg of the trade
                    for i, leg in enumerate(trade['legs']):
                        for key, value in leg.items():
                            trade_dict[f"leg_{i+1}_{key}"] = value
                    
                    all_trade_dicts.append(trade_dict)

    # Create a DataFrame from the list of trade dictionaries
    df_combined = pd.DataFrame(all_trade_dicts)

    # Calculate additional metrics
    df_combined['net_pnl'] = df_combined['pnl'] - df_combined['transaction_cost']
    df_combined['percentage_return'] = df_combined['net_pnl'] / abs(df_combined['margin_used'])
    df_combined['percentage_return'] = df_combined['percentage_return'] * 100
    df_combined['cumulative_pnl'] = df_combined['percentage_return'].cumsum()
    df_combined['max_drawdown'] = df_combined['cumulative_pnl'].cummax() - df_combined['cumulative_pnl']
    df_combined['max_drawdown'] = df_combined['max_drawdown'] * -1
    df_combined['entry_timestamp'] = pd.to_datetime(df_combined['entry_timestamp'])
    df_combined.set_index('entry_timestamp', inplace=True)
    df_combined.rename_axis('Timestamp', inplace=True)
    
    # Calculate trading accuracy
    count_positive = (df_combined['net_pnl'] > 0).sum()
    accuracy = count_positive / df_combined.shape[0]
    
    return df_combined, df_combined.shape[0], count_positive, accuracy

def visualizeAndSave(df):
    """
    Visualize trading performance metrics and save the plot as a PNG file.

    Args:
    - df (DataFrame): DataFrame containing trading performance metrics.

    Returns:
    - None
    """
    # Create a figure and axis object
    fig, ax = plt.subplots(figsize=(20, 10))
    
    # Plot cumulative P&L and max drawdown
    df['cumulative_pnl'].plot(label='Cumulative P&L', ax=ax, color='blue')
    df['max_drawdown'].plot(label='Max Drawdown', ax=ax, linestyle='dashed', color='red')
    
    # Add horizontal lines for min drawdown, mean drawdown, and total return
    min_drawdown = df['max_drawdown'].min()
    ax.axhline(y=min_drawdown, color='green', linestyle='-', label=f'Min Drawdown: {min_drawdown:.2f}')
    mean_drawdown = df['max_drawdown'].mean()
    ax.axhline(y=mean_drawdown, color='purple', linestyle='-', label=f'Mean Drawdown: {mean_drawdown:.2f}')
    total_return = df['percentage_return'].cumsum().iloc[-1]
    ax.axhline(y=total_return, color='orange', linestyle='-', label=f'Total Return: {total_return:.2f}')

    # Set plot title, labels, legend, and grid
    ax.set_title('Cumulative P&L, Drawdown, Max & Mean Return per Trade Over Time')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Percentage Return')
    ax.legend()
    ax.grid(True)

    # Ensure tight layout and display the plot
    plt.tight_layout()
    plt.savefig('pnl_drawdown_plot.png')  # Save the plot as a PNG file
    plt.show()

# Example usage:
# Assuming 'results' is the input list of trade results
# df_combined, total_trades, positive_trades, accuracy = process_results(results)
# visualizeAndSave(df_combined)
