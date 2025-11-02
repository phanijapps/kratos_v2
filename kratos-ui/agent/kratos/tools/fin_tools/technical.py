"""
Handlers for technical indicator tools using pandas-ta.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import pandas as pd

from .base import DataFrameLike, ToolExecutionError, ensure_symbol, format_response, history

try:  # pragma: no cover - optional dependency
    import pandas_ta as ta  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ta = None  # type: ignore[assignment]


def _prepare_indicator_history(symbol: str, interval: str = "1d", period: Optional[str] = "200d", start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
    return history(
        symbol,
        interval=interval,
        period=period,
        start=start,
        end=end,
        auto_adjust=True,
        include_actions=False,
    )


def _tech_indicator_context(data: pd.DataFrame) -> pd.DataFrame:
    opens = data["Open"].rename("open")
    highs = data["High"].rename("high")
    lows = data["Low"].rename("low")
    closes = data["Close"].rename("close")
    volumes = data["Volume"].rename("volume")
    return pd.concat([opens, highs, lows, closes, volumes], axis=1)


def _ensure_length(params: Dict[str, Any], default: int = 14) -> int:
    value = int(params.get("timeperiod", params.get("length", default)))
    if value <= 0:
        raise ToolExecutionError("timeperiod/length must be positive.")
    return value


def _series_indicator(func: Callable[[pd.Series, Dict[str, Any]], DataFrameLike]) -> Callable[..., DataFrameLike]:
    def _wrapped(context: pd.DataFrame, **params: Any) -> DataFrameLike:
        return func(context["close"], params)

    return _wrapped


def _calc_sma(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.sma(series, length=_ensure_length(params, 20))


def _calc_ema(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.ema(series, length=_ensure_length(params, 20))


def _calc_wma(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.wma(series, length=_ensure_length(params, 20))


def _calc_dema(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.dema(series, length=_ensure_length(params, 20))


def _calc_tema(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.tema(series, length=_ensure_length(params, 20))


def _calc_trima(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.trima(series, length=_ensure_length(params, 20))


def _calc_kama(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    fast = params.get("fast", 2)
    slow = params.get("slow", 30)
    length = _ensure_length(params, 10)
    return ta.kama(series, length=length, fast=fast, slow=slow)


def _calc_mama(context: pd.DataFrame, **params: Any) -> pd.DataFrame:
    return ta.mama(context["close"], fastlimit=params.get("fastlimit", 0.5), slowlimit=params.get("slowlimit", 0.05))


def _calc_vwap(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.vwap(high=context["high"], low=context["low"], close=context["close"], volume=context["volume"])


def _calc_t3(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    length = _ensure_length(params, 20)
    vfactor = float(params.get("vfactor", 0.7))
    return ta.t3(series, length=length, vfactor=vfactor)


def _calc_macd(context: pd.DataFrame, **params: Any) -> pd.DataFrame:
    return ta.macd(
        context["close"],
        fast=params.get("fastperiod", 12),
        slow=params.get("slowperiod", 26),
        signal=params.get("signalperiod", 9),
    )


def _calc_macdext(context: pd.DataFrame, **params: Any) -> pd.DataFrame:
    return ta.macd(
        context["close"],
        fast=params.get("fastperiod", 12),
        slow=params.get("slowperiod", 26),
        signal=params.get("signalperiod", 9),
        source=params.get("source", "close"),
    )


def _calc_stoch(context: pd.DataFrame, **params: Any) -> pd.DataFrame:
    return ta.stoch(
        high=context["high"],
        low=context["low"],
        close=context["close"],
        k=params.get("fastkperiod", 14),
        d=params.get("slowkperiod", 3),
        smooth_k=params.get("slowdperiod", 3),
    )


def _calc_stochf(context: pd.DataFrame, **params: Any) -> pd.DataFrame:
    return ta.stochf(
        high=context["high"],
        low=context["low"],
        close=context["close"],
        k=params.get("fastkperiod", 14),
        d=params.get("fastdperiod", 3),
    )


def _calc_rsi(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.rsi(series, length=_ensure_length(params, 14))


def _calc_stochrsi(series: pd.Series, params: Dict[str, Any]) -> pd.DataFrame:
    return ta.stochrsi(series, length=_ensure_length(params, 14))


def _calc_willr(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.willr(high=context["high"], low=context["low"], close=context["close"], length=_ensure_length(params, 14))


def _calc_adx(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.adx(high=context["high"], low=context["low"], close=context["close"], length=_ensure_length(params, 14))


def _calc_adxr(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.adxr(high=context["high"], low=context["low"], close=context["close"], length=_ensure_length(params, 14))


def _calc_apo(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.apo(series, fast=params.get("fastperiod", 12), slow=params.get("slowperiod", 26))


def _calc_ppo(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.ppo(
        series,
        fast=params.get("fastperiod", 12),
        slow=params.get("slowperiod", 26),
        signal=params.get("signalperiod", 9),
    )


def _calc_mom(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.mom(series, length=_ensure_length(params, 10))


def _calc_bop(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.bop(open_=context["open"], high=context["high"], low=context["low"], close=context["close"])


def _calc_cci(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.cci(high=context["high"], low=context["low"], close=context["close"], length=_ensure_length(params, 20))


def _calc_cmo(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.cmo(series, length=_ensure_length(params, 14))


def _calc_roc(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.roc(series, length=_ensure_length(params, 10))


def _calc_rocr(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.rocr(series, length=_ensure_length(params, 10))


def _calc_aroon(context: pd.DataFrame, **params: Any) -> pd.DataFrame:
    return ta.aroon(high=context["high"], low=context["low"], length=_ensure_length(params, 14))


def _calc_aroonosc(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.aroonosc(high=context["high"], low=context["low"], length=_ensure_length(params, 14))


def _calc_mfi(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.mfi(
        high=context["high"],
        low=context["low"],
        close=context["close"],
        volume=context["volume"],
        length=_ensure_length(params, 14),
    )


def _calc_trix(series: pd.Series, params: Dict[str, Any]) -> pd.Series:
    return ta.trix(series, length=_ensure_length(params, 15))


def _calc_ultosc(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.uo(high=context["high"], low=context["low"], close=context["close"])


def _calc_dx(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.dx(high=context["high"], low=context["low"], close=context["close"], length=_ensure_length(params, 14))


def _calc_minus_di(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.minus_di(high=context["high"], low=context["low"], close=context["close"], length=_ensure_length(params, 14))


def _calc_plus_di(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.plus_di(high=context["high"], low=context["low"], close=context["close"], length=_ensure_length(params, 14))


def _calc_minus_dm(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.minus_dm(high=context["high"], low=context["low"], length=_ensure_length(params, 14))


def _calc_plus_dm(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.plus_dm(high=context["high"], low=context["low"], length=_ensure_length(params, 14))


def _calc_bbands(context: pd.DataFrame, **params: Any) -> pd.DataFrame:
    length = _ensure_length(params, 20)
    std = int(params.get("nbdevup", params.get("nbdevdn", 2)))
    return ta.bbands(context["close"], length=length, std=std)


def _calc_midpoint(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.midpoint(context["close"], length=_ensure_length(params, 14))


def _calc_midprice(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.midprice(high=context["high"], low=context["low"], length=_ensure_length(params, 14))


def _calc_sar(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.psar(high=context["high"], low=context["low"], close=context["close"])


def _calc_trange(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.true_range(high=context["high"], low=context["low"], close=context["close"])


def _calc_atr(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.atr(high=context["high"], low=context["low"], close=context["close"], length=_ensure_length(params, 14))


def _calc_natr(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.natr(high=context["high"], low=context["low"], close=context["close"], length=_ensure_length(params, 14))


def _calc_ad(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.ad(high=context["high"], low=context["low"], close=context["close"], volume=context["volume"])


def _calc_adosc(context: pd.DataFrame, **params: Any) -> pd.Series:
    fast = params.get("fastperiod", 3)
    slow = params.get("slowperiod", 10)
    return ta.adosc(high=context["high"], low=context["low"], close=context["close"], volume=context["volume"], fast=fast, slow=slow)


def _calc_obv(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.obv(close=context["close"], volume=context["volume"])


def _calc_ht_trendline(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.ht_trendline(context["close"])


def _calc_ht_sine(context: pd.DataFrame, **params: Any) -> pd.DataFrame:
    return ta.ht_sine(context["close"])


def _calc_ht_trendmode(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.ht_trendmode(context["close"])


def _calc_ht_dcperiod(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.ht_dcperiod(context["close"])


def _calc_ht_dcphase(context: pd.DataFrame, **params: Any) -> pd.Series:
    return ta.ht_dcphase(context["close"])


def _calc_ht_phasor(context: pd.DataFrame, **params: Any) -> pd.DataFrame:
    return ta.ht_phasor(context["close"])


_TECHNICAL_DISPATCH: Dict[str, Callable[..., DataFrameLike]] = {
    "SMA": _series_indicator(_calc_sma),
    "EMA": _series_indicator(_calc_ema),
    "WMA": _series_indicator(_calc_wma),
    "DEMA": _series_indicator(_calc_dema),
    "TEMA": _series_indicator(_calc_tema),
    "TRIMA": _series_indicator(_calc_trima),
    "KAMA": _series_indicator(_calc_kama),
    "MAMA": _calc_mama,
    "VWAP": _calc_vwap,
    "T3": _series_indicator(_calc_t3),
    "MACD": _calc_macd,
    "MACDEXT": _calc_macdext,
    "STOCH": _calc_stoch,
    "STOCHF": _calc_stochf,
    "RSI": _series_indicator(_calc_rsi),
    "STOCHRSI": _series_indicator(_calc_stochrsi),
    "WILLR": _calc_willr,
    "ADX": _calc_adx,
    "ADXR": _calc_adxr,
    "APO": _series_indicator(_calc_apo),
    "PPO": _series_indicator(_calc_ppo),
    "MOM": _series_indicator(_calc_mom),
    "BOP": _calc_bop,
    "CCI": _calc_cci,
    "CMO": _series_indicator(_calc_cmo),
    "ROC": _series_indicator(_calc_roc),
    "ROCR": _series_indicator(_calc_rocr),
    "AROON": _calc_aroon,
    "AROONOSC": _calc_aroonosc,
    "MFI": _calc_mfi,
    "TRIX": _series_indicator(_calc_trix),
    "ULTOSC": _calc_ultosc,
    "DX": _calc_dx,
    "MINUS_DI": _calc_minus_di,
    "PLUS_DI": _calc_plus_di,
    "MINUS_DM": _calc_minus_dm,
    "PLUS_DM": _calc_plus_dm,
    "BBANDS": _calc_bbands,
    "MIDPOINT": _calc_midpoint,
    "MIDPRICE": _calc_midprice,
    "SAR": _calc_sar,
    "TRANGE": _calc_trange,
    "ATR": _calc_atr,
    "NATR": _calc_natr,
    "AD": _calc_ad,
    "ADOSC": _calc_adosc,
    "OBV": _calc_obv,
    "HT_TRENDLINE": _calc_ht_trendline,
    "HT_SINE": _calc_ht_sine,
    "HT_TRENDMODE": _calc_ht_trendmode,
    "HT_DCPERIOD": _calc_ht_dcperiod,
    "HT_DCPHASE": _calc_ht_dcphase,
    "HT_PHASOR": _calc_ht_phasor,
}


def calculate_technical_indicator(
    tool_name: str,
    *,
    symbol: str,
    interval: str = "1d",
    period: Optional[str] = "200d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    **params: Any,
) -> Dict[str, Any]:
    if ta is None:
        return format_response(
            tool_name,
            symbol=symbol,
            error="missing_dependency",
            message="Technical indicators require the pandas-ta package.",
            suggestion="Install pandas-ta to enable technical analysis tools: pip install pandas-ta"
        )
    
    symbol = ensure_symbol(symbol)
    
    # Try to get historical data
    try:
        history_df = _prepare_indicator_history(symbol, interval=interval, period=period, start=start, end=end)
    except ToolExecutionError as exc:
        return format_response(
            tool_name,
            symbol=symbol,
            interval=interval,
            period=period,
            error="data_unavailable",
            message=f"Could not retrieve historical data for {symbol}: {exc}",
            suggestion="Try a different symbol, time period, or check if the symbol exists and has trading data."
        )
    
    # Check if we have enough data
    if len(history_df) < 50:  # Most indicators need at least 20-50 data points
        return format_response(
            tool_name,
            symbol=symbol,
            interval=interval,
            period=period,
            error="insufficient_data",
            message=f"Insufficient historical data for {tool_name} calculation. Got {len(history_df)} data points, need at least 50.",
            suggestion="Try a longer time period (e.g., '1y' instead of '1mo') or a different interval to get more data points.",
            available_data_points=len(history_df),
            recommended_period="1y"
        )
    
    context = _tech_indicator_context(history_df)
    calculator = _TECHNICAL_DISPATCH.get(tool_name)
    if calculator is None:
        return format_response(
            tool_name,
            symbol=symbol,
            error="unsupported_indicator",
            message=f"Technical indicator {tool_name} is not supported.",
            suggestion="Use one of the supported technical indicators.",
            supported_indicators=list(_TECHNICAL_DISPATCH.keys())[:10]  # Show first 10
        )
    
    try:
        result = calculator(context, **params)
    except Exception as exc:
        return format_response(
            tool_name,
            symbol=symbol,
            interval=interval,
            period=period,
            error="calculation_failed",
            message=f"Failed to calculate {tool_name} for {symbol}: {exc}",
            suggestion="Try different parameters, a longer time period, or check if the symbol has sufficient trading data.",
            parameters_used=params
        )
    
    # Check if calculation returned valid data
    if result is None:
        return format_response(
            tool_name,
            symbol=symbol,
            interval=interval,
            period=period,
            error="no_data_returned",
            message=f"{tool_name} calculation returned no data.",
            suggestion="This may be due to insufficient data or invalid parameters. Try a longer time period or different parameters.",
            data_points_available=len(history_df),
            recommended_period="1y"
        )
    
    if isinstance(result, pd.DataFrame) and result.empty:
        return format_response(
            tool_name,
            symbol=symbol,
            interval=interval,
            period=period,
            error="empty_result",
            message=f"{tool_name} calculation returned empty results.",
            suggestion="Try a longer time period or different parameters to get meaningful results.",
            recommended_period="1y"
        )
    
    if isinstance(result, pd.Series) and result.empty:
        return format_response(
            tool_name,
            symbol=symbol,
            interval=interval,
            period=period,
            error="empty_result",
            message=f"{tool_name} calculation returned empty results.",
            suggestion="Try a longer time period or different parameters to get meaningful results.",
            recommended_period="1y"
        )
    
    return format_response(
        tool_name,
        symbol=symbol,
        interval=interval,
        period=period,
        data=result,
    )


HANDLERS: Dict[str, Callable[..., Dict[str, Any]]] = {
    name: (lambda tool=name: (lambda **kwargs: calculate_technical_indicator(
        tool,
        symbol=kwargs["symbol"],
        interval=kwargs.get("interval", "1d"),
        period=kwargs.get("period", "200d"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        **{k: v for k, v in kwargs.items() if k not in {"symbol", "interval", "period", "start", "end"}}
    )))()
    for name in _TECHNICAL_DISPATCH
}


__all__ = ["HANDLERS"]
