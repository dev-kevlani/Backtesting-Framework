import pandas as pd
import matplotlib.pyplot as plt

def process_results(results):
    all_trade_dicts = []

    for day_trades in results:
        if day_trades is not None:
            for trade in day_trades:
                trade_dict = {
                    'entry_timestamp': trade['entry_timestamp'],
                    'exit_timestamp': trade['exit_timestamp'],
                    'pnl': trade['pnl']
                }
                
                for i, leg in enumerate(trade['legs']):
                    for key, value in leg.items():
                        trade_dict[f"leg_{i+1}_{key}"] = value
                
                all_trade_dicts.append(trade_dict)

    df_combined = pd.DataFrame(all_trade_dicts)

    df_combined['total_margin'] = df_combined.filter(like='margin_used').sum(axis=1)
    df_combined['percentage_return'] = df_combined['pnl'] / abs(df_combined['total_margin'])
    df_combined['percentage_return'] = df_combined['percentage_return'] * 100
    df_combined['cumulative_pnl'] = df_combined['percentage_return'].cumsum()
    df_combined['max_drawdown'] = df_combined['cumulative_pnl'].cummax() - df_combined['cumulative_pnl']
    df_combined['max_drawdown'] = df_combined['max_drawdown'] * -1
    df_combined['entry_timestamp'] = pd.to_datetime(df_combined['entry_timestamp'])
    df_combined.set_index('entry_timestamp', inplace=True)
    df_combined.rename_axis('Timestamp', inplace=True)

    return df_combined

def visualizeAndSave(df):
    
    fig, ax = plt.subplots(figsize=(20, 10))
    
    df['pnl'].cumsum().plot(label='Cumulative P&L', ax=ax, color='blue')
    df['max_drawdown'].plot(label='Max Drawdown', ax=ax, linestyle='dashed', color='red')
    min_drawdown = df['max_drawdown'].min()
    ax.axhline(y=min_drawdown, color='green', linestyle='-', label=f'Min Drawdown: {min_drawdown:.2f}')
    mean_drawdown = df['max_drawdown'].mean()
    ax.axhline(y=mean_drawdown, color='purple', linestyle='-', label=f'Mean Drawdown: {mean_drawdown:.2f}')
    total_return = df['percentage_return'].cumsum().iloc[-1]
    ax.axhline(y=total_return, color='orange', linestyle='-', label=f'Total Return: {total_return:.2f}')

    ax.set_title('Cumulative P&L, Drawdown, Max & Mean Return per Trade Over Time')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Percentage Return')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.show()