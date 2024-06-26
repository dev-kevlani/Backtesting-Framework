# Customized Backtesting Framework for Options
## Overview

This backtesting framework is designed to evaluate options trading strategies. It supports complex multi-leg strategies and allows the user to define custom instruments with actions. The framework is built to handle large datasets and can efficiently simulate trading scenarios over a specified period.

### Key Features
- **Comprehensive Strategy Support**: Test a wide array of strategies, including delta hedging, gamma hedging, long and short volatility strategies, and complex multi-leg strategies like butterfly spreads.
- **Signal Generation**: Integrate custom trading signals like indicators based on OHLC data or indicators derived from greeks of options data.
- **Position Management**: Track and manage open positions with stop-loss and target profit conditions (percentage or point based).
- **Parallel Processing**: Utilize multiprocessing for faster data processing ( multiple legs - under 4 minutes for 1 year, single leg - under 50 seconds for 1 year).
- **Flexible Configuration**: Customize trading parameters such as strike price parts, option types, actions, and lots and much more
- **Ongoing Development**: A wrapper function is being built to enable backtesting of multiple strategies by inputting strategy specifications and data directories. Iterative optimization through Hyperopt integration is also being explored and developed.


# Contributing

Contributions are welcome! Please create a pull request with a detailed description of your changes.


# Contact

For any questions or suggestions, please reach out to devkevlani99@gmail.com
