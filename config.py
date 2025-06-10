# config.py

TICKERS = [
    'MSFT', 'NVDA', 'AAPL', 'AMZN', 'GOOGL', 'GOOG', 'META', 'AVGO', 'BRK-B', 'TSLA',
    'WMT', 'JPM', 'LLY', 'V', 'MA', 'NFLX', 'ORCL', 'XOM', 'COST', 'PG',
    'JNJ', 'HD', 'BAC', 'ABBV', 'PLTR', 'KO', 'PM', 'UNH', 'TMUS', 'GE',
    'CSCO', 'CRM', 'IBM', 'WFC', 'CVX', 'MCD', 'LIN', 'NOW', 'DIS', 'ACN',
    'T', 'ISRG', 'MRK', 'UBER', 'GS', 'INTU', 'VZ', 'AMD', 'ADBE', 'RTX',
    'PEP', 'BKNG', 'TXN', 'QCOM', 'PGR', 'CAT', 'SPGI', 'AXP', 'MS', 'BSX',
    'BA', 'TMO', 'SCHW', 'TJX', 'NEE', 'AMGN', 'HON', 'BLK', 'C', 'UNP',
    'GILD', 'CMCSA', 'AMAT', 'ADP', 'PFE', 'SYK', 'DE', 'LOW', 'ETN', 'GEV',
    'PANW', 'DHR', 'COF', 'MMC', 'VRTX', 'COP', 'ADI', 'MDT', 'CB', 'CRWD',
    'MU', 'LRCX', 'APH', 'KLAC', 'CME', 'MO', 'BX', 'ICE', 'AMT', 'LMT',
    'SO', 'PLD', 'ANET', 'BMY', 'TT', 'SBUX', 'ELV', 'FI', 'DUK', 'WELL',
    'MCK', 'CEG', 'INTC', 'CDNS', 'CI', 'AJG', 'WM', 'PH', 'MDLZ', 'EQIX',
    'SHW', 'MMM', 'KKR', 'TDG', 'ORLY', 'CVS', 'SNPS', 'AON', 'CTAS', 'CL',
    'MCO', 'ZTS', 'MSI', 'PYPL', 'NKE', 'WMB', 'GD', 'UPS', 'DASH', 'CMG',
    'HCA', 'PNC', 'USB', 'HWM', 'ECL', 'EMR', 'ITW', 'FTNT', 'AZO', 'NOC',
    'JCI', 'BK', 'REGN', 'ADSK', 'EOG', 'TRV', 'ROP', 'APD', 'NEM', 'MAR',
    'HLT', 'RCL', 'CSX', 'APO', 'CARR', 'WDAY', 'ABNB', 'AEP', 'COIN', 'FCX',
    'AOS', 'ABT', 'AES', 'AFL', 'A', 'AKAM', 'ALB', 'ARE', 'ALGN', 'ALLE',
    'LNT', 'ALL', 'AEE', 'AIG', 'AWK', 'AMP', 'AME', 'ANSS', 'APA', 'IVZ',
    'JBL', 'K', 'KDP', 'KEX', 'KEY', 'KHC', 'KIM', 'KMB', 'KMI', 'KMX',
    'KR', 'KVUE', 'L', 'LDOS', 'LEN', 'LH', 'LHX', 'LKQ', 'LULU', 'LUV',
    'LVS', 'LW', 'LYB', 'LYV', 'MAA', 'MAS', 'MCHP', 'MHK', 'MKC', 'MKTX',
    'MLM', 'MNST', 'MOS', 'MPC', 'MPWR', 'MRNA', 'MTB', 'MTD', 'NCLH', 'NDAQ',
    'NDSN', 'NI', 'NRS', 'NSC', 'NTAP', 'NTRS', 'NUE', 'NVR', 'NWS', 'NWSA',
    'NXPI', 'O', 'ODFL', 'OKE', 'OMC', 'ON', 'OTIS', 'OXY', 'PAYX', 'PCAR',
    'PCG', 'PEAK', 'PEG', 'PFG', 'PHM', 'PKG', 'PNR', 'PNW', 'PODD', 'POOL',
    'PPG', 'PPL', 'PRU', 'PSA', 'PSX', 'PTC', 'PWR', 'PXD', 'QRVO', 'REG',
    'RF', 'RHI', 'RJF', 'RL', 'RMD', 'ROK', 'ROL', 'ROST', 'RSG', 'SBAC',
    'SEDG', 'SEE', 'SJM', 'SLB', 'SNA', 'SRE', 'STE', 'STLD', 'STT', 'STX',
    'STZ', 'SWK', 'SWKS', 'SYF', 'SYY', 'TAP', 'TDY', 'TECH', 'TER', 'TFC'
]

TIMEFRAMES = {
    'Short_Term_Analysis': {'period': '6mo', 'interval': '1d'},
    'Medium_Term_Analysis': {'period': '2y', 'interval': '1d'},
    'Long_Term_Analysis': {'period': '5y', 'interval': '1wk'}
}