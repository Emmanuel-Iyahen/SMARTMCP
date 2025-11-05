

# daily_stock_forecast_dag.py
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.models import Variable
import os
import warnings
warnings.filterwarnings('ignore')

# Snowflake configuration from environment variables
def get_snowflake_config():
    """Get Snowflake configuration from environment variables with fallbacks"""
    return {
        'account': os.getenv('SNOWFLAKE_ACCOUNT', Variable.get('SNOWFLAKE_ACCOUNT', default_var='your_account.region')),
        'user': os.getenv('SNOWFLAKE_USER', Variable.get('SNOWFLAKE_USER', default_var='your_username')),
        'password': os.getenv('SNOWFLAKE_PASSWORD', Variable.get('SNOWFLAKE_PASSWORD', default_var='your_password')),
        'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', Variable.get('SNOWFLAKE_WAREHOUSE', default_var='your_warehouse')),
        'database': os.getenv('SNOWFLAKE_DATABASE', Variable.get('SNOWFLAKE_DATABASE', default_var='your_database')),
        'schema': os.getenv('SNOWFLAKE_SCHEMA', Variable.get('SNOWFLAKE_SCHEMA', default_var='your_schema')),
        'role': os.getenv('SNOWFLAKE_ROLE', Variable.get('SNOWFLAKE_ROLE', default_var='your_role'))
    }

def create_snowflake_connection():
    """Create Snowflake connection using environment variables"""
    config = get_snowflake_config()
    
    # Create connection string for hook
    conn_id = 'snowflake_default'
    
    # Ensure connection exists or create it
    try:
        hook = SnowflakeHook(snowflake_conn_id=conn_id)
        # Test connection
        conn = hook.get_conn()
        print("✅ Using existing Snowflake connection")
        return hook
    except:
        print("🔄 Creating new Snowflake connection from environment variables")
        # Connection will be created by the hook with the provided config
        pass
    
    return SnowflakeHook(
        snowflake_conn_id=conn_id,
        account=config['account'],
        user=config['user'],
        password=config['password'],
        warehouse=config['warehouse'],
        database=config['database'],
        schema=config['schema'],
        role=config['role']
    )

default_args = {
    'owner': 'stock_analytics',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 4),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=30)
}

def extract_stock_data():
    """Extract latest 30 days of stock data from Snowflake"""
    try:
        hook = create_snowflake_connection()
        
        query = """
        SELECT 
            TIMESTAMP,
            SYMBOL,
            COMPANY_NAME,
            OPEN,
            HIGH,
            LOW,
            CLOSE,
            VOLUME
        FROM uk_stocks 
        WHERE TIMESTAMP >= DATEADD(day, -30, CURRENT_DATE())
        ORDER BY TIMESTAMP ASC, SYMBOL ASC
        """
        
        df = hook.get_pandas_df(query)
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
        
        print(f"📊 Extracted {len(df)} records from Snowflake")
        print(f"🏢 Stocks: {df['SYMBOL'].unique().tolist()}")
        print(f"📅 Date range: {df['TIMESTAMP'].min().date()} to {df['TIMESTAMP'].max().date()}")
        
        return df.to_json(date_format='iso', orient='split')
        
    except Exception as e:
        print(f"❌ Error extracting data from Snowflake: {str(e)}")
        raise

def generate_advanced_forecasts(**context):
    """Generate advanced statistical forecasts using your proven method"""
    ti = context['ti']
    df_json = ti.xcom_pull(task_ids='extract_stock_data')
    df = pd.read_json(df_json, orient='split')
    
    print("🔮 GENERATING ADVANCED STATISTICAL FORECASTS...")
    advanced_forecasts = {}

    for symbol in df['SYMBOL'].unique():
        print(f"   Analyzing {symbol}...")
        
        try:
            stock_data = df[df['SYMBOL'] == symbol].copy().sort_values('TIMESTAMP')
            company_name = stock_data['COMPANY_NAME'].iloc[0]
            prices = stock_data['CLOSE'].values
            
            if len(prices) < 10:
                print(f"   ⚠️  Not enough data for {symbol}")
                continue
            
            # Method 1: Exponential Smoothing (best for short-term forecasts)
            model_es = ExponentialSmoothing(
                prices, 
                trend='add', 
                seasonal='add', 
                seasonal_periods=5  # Weekly pattern
            )
            fitted_es = model_es.fit()
            forecast_es = fitted_es.forecast(7)
            
            # Method 2: Linear Regression with trend
            X = np.array(range(len(prices))).reshape(-1, 1)
            model_lr = LinearRegression()
            model_lr.fit(X, prices)
            future_X = np.array(range(len(prices), len(prices) + 7)).reshape(-1, 1)
            forecast_lr = model_lr.predict(future_X)
            
            # Method 3: Moving Average momentum
            momentum = (prices[-1] - prices[-5]) / prices[-5] if prices[-5] != 0 else 0
            
            # Combine methods with weights (Exponential Smoothing gets highest weight)
            combined_forecast = (
                forecast_es * 0.6 + 
                forecast_lr * 0.3 + 
                (prices[-1] * (1 + momentum * 0.5)) * 0.1
            )
            
            # Calculate confidence intervals based on recent volatility
            recent_volatility = np.std(prices[-10:]) if len(prices) >= 10 else np.std(prices)
            confidence_range = recent_volatility * 1.96  # 95% confidence
            
            # Generate future dates
            last_date = stock_data['TIMESTAMP'].iloc[-1]
            future_dates = [last_date + pd.Timedelta(days=i+1) for i in range(7)]
            
            # Store results
            advanced_forecasts[symbol] = {
                'company': company_name,
                'last_price': float(prices[-1]),
                'last_date': last_date.strftime('%Y-%m-%d'),
                'forecast_dates': [d.strftime('%Y-%m-%d') for d in future_dates],
                'forecast_prices': [round(float(price), 2) for price in combined_forecast],
                'confidence_lower': [round(max(0, float(price) - confidence_range), 2) for price in combined_forecast],
                'confidence_upper': [round(float(price) + confidence_range, 2) for price in combined_forecast],
                'trend': 'BULLISH' if combined_forecast[-1] > prices[-1] else 'BEARISH',
                'expected_change_pct': float((combined_forecast[0] - prices[-1]) / prices[-1] * 100),
                'volatility_pct': float(recent_volatility / prices[-1] * 100),
                'methods_used': ['Exponential Smoothing', 'Linear Regression', 'Momentum']
            }
            
            print(f"   ✅ Advanced forecast completed for {symbol}")
            
        except Exception as e:
            print(f"   ❌ Error with {symbol}: {str(e)}")
            continue

    print(f"✅ Advanced forecasts generated for {len(advanced_forecasts)} stocks!")
    return advanced_forecasts

def generate_trading_signals(**context):
    """Generate trading signals from forecasts using your proven logic"""
    ti = context['ti']
    forecasts = ti.xcom_pull(task_ids='generate_advanced_forecasts')
    
    print("🎯 GENERATING TRADING SIGNALS FROM FORECASTS...")
    trading_signals = []

    for symbol, forecast in forecasts.items():
        last_price = forecast['last_price']
        next_day_forecast = forecast['forecast_prices'][0]
        seven_day_forecast = forecast['forecast_prices'][-1]
        confidence_width = forecast['confidence_upper'][0] - forecast['confidence_lower'][0]
        
        # Calculate key metrics
        next_day_change_pct = forecast['expected_change_pct']
        seven_day_change_pct = ((seven_day_forecast - last_price) / last_price * 100)
        confidence_pct = (confidence_width / last_price * 100)
        
        # Trading logic
        signal = "HOLD"
        confidence = "LOW"
        reasoning = []
        
        # STRONG SELL signals
        if (next_day_change_pct < -1.0 or 
            seven_day_change_pct < -2.0 or
            (next_day_change_pct < -0.5 and seven_day_change_pct < -1.0)):
            signal = "STRONG_SELL"
            confidence = "HIGH"
            reasoning.append("Significant downward pressure")
            
        # SELL signals  
        elif next_day_change_pct < -0.3 and seven_day_change_pct < -0.5:
            signal = "SELL"
            confidence = "MEDIUM"
            reasoning.append("Moderate downward trend")
        
        # STRONG BUY signals
        elif (next_day_change_pct > 1.0 or 
              seven_day_change_pct > 2.0 or
              (next_day_change_pct > 0.5 and seven_day_change_pct > 1.0)):
            signal = "STRONG_BUY"
            confidence = "HIGH"
            reasoning.append("Strong upward momentum")
            
        # BUY signals
        elif next_day_change_pct > 0.3 and seven_day_change_pct > 0.5:
            signal = "BUY"
            confidence = "MEDIUM"
            reasoning.append("Positive trend established")
        
        # HOLD with reasons
        else:
            if abs(next_day_change_pct) < 0.1:
                reasoning.append("Minimal expected movement")
            if confidence_pct > 1.0:
                reasoning.append("High uncertainty in forecast")
            if next_day_change_pct > 0 and seven_day_change_pct < 0:
                reasoning.append("Mixed signals - short gain vs long loss")
            elif next_day_change_pct < 0 and seven_day_change_pct > 0:
                reasoning.append("Short dip expected before recovery")
        
        # Risk assessment
        risk_level = "LOW"
        if confidence_pct > 2.0:
            risk_level = "HIGH"
        elif confidence_pct > 1.0:
            risk_level = "MEDIUM"
        
        trading_signals.append({
            'symbol': symbol,
            'company': forecast['company'],
            'current_price': last_price,
            'signal': signal,
            'confidence': confidence,
            'risk': risk_level,
            'next_day_change_pct': next_day_change_pct,
            'seven_day_change_pct': seven_day_change_pct,
            'trend': forecast['trend'],
            'reasoning': ' | '.join(reasoning) if reasoning else "Stable, no clear trend",
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    print(f"✅ Generated {len(trading_signals)} trading signals")
    return trading_signals

def save_results_to_snowflake(**context):
    """Save forecasts and trading signals to Snowflake"""
    ti = context['ti']
    forecasts = ti.xcom_pull(task_ids='generate_advanced_forecasts')
    trading_signals = ti.xcom_pull(task_ids='generate_trading_signals')
    
    try:
        hook = create_snowflake_connection()
        conn = hook.get_conn()
        cursor = conn.cursor()
        
        current_time = datetime.now()
        
        # Create forecasts table if not exists
        create_forecasts_table = """
        CREATE TABLE IF NOT EXISTS stock_forecasts (
            symbol VARCHAR(50),
            forecast_date DATE,
            forecast_price FLOAT,
            confidence_lower FLOAT,
            confidence_upper FLOAT,
            generated_at TIMESTAMP_NTZ,
            PRIMARY KEY (symbol, forecast_date, generated_at)
        )
        """
        cursor.execute(create_forecasts_table)
        
        # Create trading signals table
        create_signals_table = """
        CREATE TABLE IF NOT EXISTS trading_signals (
            symbol VARCHAR(50),
            company_name VARCHAR(200),
            signal VARCHAR(20),
            confidence VARCHAR(20),
            risk VARCHAR(20),
            current_price FLOAT,
            next_day_change_pct FLOAT,
            seven_day_change_pct FLOAT,
            trend VARCHAR(10),
            reasoning VARCHAR(500),
            generated_at TIMESTAMP_NTZ,
            PRIMARY KEY (symbol, generated_at)
        )
        """
        cursor.execute(create_signals_table)
        
        # Insert forecasts
        forecast_count = 0
        for symbol, forecast_data in forecasts.items():
            for i, date_str in enumerate(forecast_data['forecast_dates']):
                insert_sql = """
                INSERT INTO stock_forecasts 
                (symbol, forecast_date, forecast_price, confidence_lower, confidence_upper, generated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    symbol,
                    date_str,
                    forecast_data['forecast_prices'][i],
                    forecast_data['confidence_lower'][i],
                    forecast_data['confidence_upper'][i],
                    current_time
                ))
                forecast_count += 1
        
        # Insert trading signals
        signal_count = 0
        for signal in trading_signals:
            insert_sql = """
            INSERT INTO trading_signals 
            (symbol, company_name, signal, confidence, risk, current_price, 
             next_day_change_pct, seven_day_change_pct, trend, reasoning, generated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                signal['symbol'],
                signal['company'],
                signal['signal'],
                signal['confidence'],
                signal['risk'],
                signal['current_price'],
                signal['next_day_change_pct'],
                signal['seven_day_change_pct'],
                signal['trend'],
                signal['reasoning'],
                signal['generated_at']
            ))
            signal_count += 1
        
        conn.commit()
        print(f"✅ Saved {forecast_count} forecast records and {signal_count} trading signals to Snowflake")
        
    except Exception as e:
        print(f"❌ Error saving to Snowflake: {str(e)}")
        conn.rollback()
        raise
    
    finally:
        cursor.close()
        conn.close()

def generate_daily_summary(**context):
    """Generate daily summary report"""
    ti = context['ti']
    trading_signals = ti.xcom_pull(task_ids='generate_trading_signals')
    forecasts = ti.xcom_pull(task_ids='generate_advanced_forecasts')
    
    # Calculate summary statistics
    strong_buys = len([s for s in trading_signals if s['signal'] == 'STRONG_BUY'])
    buys = len([s for s in trading_signals if s['signal'] == 'BUY'])
    strong_sells = len([s for s in trading_signals if s['signal'] == 'STRONG_SELL'])
    sells = len([s for s in trading_signals if s['signal'] == 'SELL'])
    holds = len([s for s in trading_signals if s['signal'] == 'HOLD'])
    
    bullish_count = len([f for f in forecasts.values() if f['trend'] == 'BULLISH'])
    bearish_count = len([f for f in forecasts.values() if f['trend'] == 'BEARISH'])
    avg_change = np.mean([f['expected_change_pct'] for f in forecasts.values()])
    
    summary = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_stocks_analyzed': len(forecasts),
        'market_sentiment': 'BULLISH' if bullish_count > bearish_count else 'BEARISH',
        'bullish_stocks': bullish_count,
        'bearish_stocks': bearish_count,
        'average_expected_change': round(avg_change, 2),
        'trading_signals_summary': {
            'strong_buy': strong_buys,
            'buy': buys,
            'strong_sell': strong_sells,
            'sell': sells,
            'hold': holds
        },
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print("\n" + "="*80)
    print("📊 DAILY FORECASTING SUMMARY")
    print("="*80)
    print(f"📅 Date: {summary['date']}")
    print(f"📈 Market Sentiment: {summary['market_sentiment']}")
    print(f"🎯 Trading Signals: {strong_buys} Strong Buy, {buys} Buy, {strong_sells} Strong Sell, {sells} Sell, {holds} Hold")
    print(f"📊 Stock Trends: {bullish_count} Bullish, {bearish_count} Bearish")
    print(f"📉 Average Expected Change: {avg_change:+.2f}%")
    print("="*80)
    
    return summary

# Define the DAG
with DAG(
    'daily_stock_forecast_pipeline',
    default_args=default_args,
    description='Daily UK Stock Forecasting Pipeline - Advanced Statistical Methods',
    schedule_interval='0 0 * * *',  # Run daily at midnight
    catchup=False,
    max_active_runs=1,
    tags=['stocks', 'forecasting', 'trading', 'analytics']
) as dag:
    
    extract_task = PythonOperator(
        task_id='extract_stock_data',
        python_callable=extract_stock_data
    )
    
    forecast_task = PythonOperator(
        task_id='generate_advanced_forecasts',
        python_callable=generate_advanced_forecasts
    )
    
    signals_task = PythonOperator(
        task_id='generate_trading_signals',
        python_callable=generate_trading_signals
    )
    
    save_task = PythonOperator(
        task_id='save_results_to_snowflake',
        python_callable=save_results_to_snowflake
    )
    
    summary_task = PythonOperator(
        task_id='generate_daily_summary',
        python_callable=generate_daily_summary
    )
    
    # Define workflow
    extract_task >> forecast_task >> signals_task >> save_task >> summary_task