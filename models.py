import math

def haversine_distance_miles(lat1, lon1, lat2, lon2):
    """
    Calculate distance in miles between two latitude/longitude points.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0
    
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def evaluate_swap_fairness(user_item_score, target_item_score):
    """
    Evaluates value equivalence and barter fairness between two items.
    Returns:
    - fairness_pct: 0 to 100%
    - verdict: classification label
    - suggested_credit_diff: how many eco-credits to add to balance the trade
    - advice: helpful human-readable guidance
    """
    score_diff = user_item_score - target_item_score
    abs_diff = abs(score_diff)
    
    # Max reasonable difference is 40 points
    fairness_pct = max(0, min(100, round(100 - (abs_diff * 1.8))))
    
    if abs_diff <= 5:
        verdict = "Perfect Fair Barter"
        advice = "Both items hold virtually equivalent trade value. Ideal 1-to-1 swap!"
        suggested_credit = 0
    elif abs_diff <= 12:
        verdict = "Balanced Match"
        if score_diff > 0:
            advice = "Your item has slightly higher value. A direct swap is fair, or ask for 5-10 Eco-Credits."
            suggested_credit = 5
        else:
            advice = "Target item is slightly higher tier. Offering 5-10 Eco-Credits will increase acceptance!"
            suggested_credit = 8
    elif abs_diff <= 25:
        verdict = "Tier Gap - Credits Recommended"
        credit_sweetener = round(abs_diff * 1.2)
        if score_diff > 0:
            advice = f"Your item has noticeably higher value. Suggest asking the trader for {credit_sweetener} Eco-Credits or an accessory."
            suggested_credit = credit_sweetener
        else:
            advice = f"Target item has higher barter grade. Offer {credit_sweetener} Eco-Credits to bridge the gap."
            suggested_credit = credit_sweetener
    else:
        verdict = "Uneven Trade"
        advice = "Large difference in value grade. Consider a multi-item bundle or bundle with bonus Eco-Credits."
        suggested_credit = round(abs_diff * 1.5)

    return {
        'fairness_pct': fairness_pct,
        'verdict': verdict,
        'score_diff': round(score_diff, 1),
        'suggested_credit': suggested_credit,
        'advice': advice
    }

def get_eco_equivalencies(total_water_l, total_co2_kg, items_count):
    """
    Calculates tangible eco-impact real-world equivalencies.
    """
    showers_saved = round(total_water_l / 65)  # Average 8-minute shower is 65 liters
    car_miles_offset = round(total_co2_kg * 2.5)  # 1kg CO2 ~ 2.5 miles in typical petrol car
    trees_day_equivalent = round(total_co2_kg / 0.06) # 1 tree absorbs ~0.06 kg CO2/day
    
    return {
        'showers_saved': showers_saved,
        'car_miles_offset': car_miles_offset,
        'trees_day_equivalent': trees_day_equivalent,
        'landfill_kg': round(items_count * 0.75, 1) # Approx 0.75kg clothing diverted per item
    }
