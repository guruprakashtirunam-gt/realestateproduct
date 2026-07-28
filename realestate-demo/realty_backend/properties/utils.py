"""Indian currency formatting helpers, ported 1:1 from the frontend's
formatRupee()/formatLakhCrore()/indianCommas() functions so the API returns
labels identical to what the original static site rendered."""


def indian_commas(num_str: str) -> str:
    """12345678 -> '1,23,45,678' (Indian digit grouping: last 3, then pairs of 2)."""
    s = num_str
    if len(s) <= 3:
        return s
    last_three = s[-3:]
    other = s[:-3]
    groups = []
    while len(other) > 2:
        groups.insert(0, other[-2:])
        other = other[:-2]
    if other:
        groups.insert(0, other)
    return ','.join(groups) + ',' + last_three


def format_rupee(amount) -> str:
    amount = round(float(amount))
    return '\u20b9' + indian_commas(str(amount))


def format_lakh_crore(amount) -> str:
    amount = float(amount)
    if amount >= 10_000_000:
        value = amount / 10_000_000
        decimals = 0 if amount % 10_000_000 == 0 else 2
        return f'\u20b9{value:.{decimals}f} Crore'
    elif amount >= 100_000:
        value = amount / 100_000
        decimals = 0 if amount % 100_000 == 0 else 2
        return f'\u20b9{value:.{decimals}f} Lakh'
    return format_rupee(amount)


def format_price_label(amount, status: str) -> str:
    """Rent listings show '₹32,000/mo'; sale/new listings show Lakh/Crore notation."""
    if status == 'rent':
        return f'{format_rupee(amount)}/mo'
    return format_lakh_crore(amount)
