import math

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculate distance in Kilometers between two locations.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0
    
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def compare_swap_values(my_price_inr, target_price_inr):
    """
    Simple, intuitive comparison of two garments in Indian Rupees (₹).
    """
    diff = int(target_price_inr) - int(my_price_inr)
    abs_diff = abs(diff)
    max_price = max(int(my_price_inr), int(target_price_inr), 1)
    
    # Simple percentage match
    ratio = min(my_price_inr, target_price_inr) / max(my_price_inr, target_price_inr)
    match_pct = round(ratio * 100)

    if abs_diff <= 250:
        verdict = "⭐️ Perfect Fair 1-to-1 Swap!"
        advice = f"Both clothes are similar in value (₹{my_price_inr:,} vs ₹{target_price_inr:,}). No extra money needed!"
        suggested_extra_inr = 0
    elif diff > 0:
        verdict = f"Target item is ₹{abs_diff:,} higher"
        advice = f"Their garment (₹{target_price_inr:,}) is worth ₹{abs_diff:,} more than yours (₹{my_price_inr:,}). You can offer ₹{abs_diff:,} cash/UPI balance to make it a fair deal."
        suggested_extra_inr = abs_diff
    else:
        verdict = f"Your item is ₹{abs_diff:,} higher"
        advice = f"Your garment (₹{my_price_inr:,}) is worth ₹{abs_diff:,} more than theirs (₹{target_price_inr:,}). You can ask for a direct swap or request ₹{abs_diff:,} extra."
        suggested_extra_inr = 0

    return {
        'match_pct': match_pct,
        'difference_inr': abs_diff,
        'verdict': verdict,
        'advice': advice,
        'suggested_extra_inr': suggested_extra_inr
    }
