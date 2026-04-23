import pandas as pd


def calculate_bias_metrics(df: pd.DataFrame, target_col: str, sensitive_col: str) -> dict:
    """Calculate fairness metrics for the selected columns."""
    if target_col not in df.columns or sensitive_col not in df.columns:
        raise ValueError("Selected columns were not found in the dataset.")

    # Ensure target is numeric
    df = df.copy()
    df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
    df = df.dropna(subset=[target_col, sensitive_col])

    # Selection rate per group
    selection_rates = df.groupby(sensitive_col)[target_col].mean().to_dict()
    selection_rates = {str(k): round(float(v), 4) for k, v in selection_rates.items()}

    values = list(selection_rates.values())

    # Demographic Parity Difference: max rate - min rate
    if len(values) >= 2:
        demographic_parity_difference = round(max(values) - min(values), 4)
    else:
        demographic_parity_difference = 0.0

    # Disparate Impact Ratio: min rate / max rate (1.0 = perfectly fair)
    if len(values) >= 2 and max(values) > 0:
        disparate_impact_ratio = round(min(values) / max(values), 4)
    else:
        disparate_impact_ratio = None

    return {
        "selection_rate": selection_rates,
        "demographic_parity_difference": demographic_parity_difference,
        "disparate_impact_ratio": disparate_impact_ratio,
    }