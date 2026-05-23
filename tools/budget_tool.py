def  get_budget_estimate(
    flight_price,
    hotel_price_per_night,
    days,
    food_per_day=30,
    transport_per_day=10,
    activities=100
):

    hotel_total = hotel_price_per_night * days

    food_total = food_per_day * days

    transport_total = transport_per_day * days

    total = (
        flight_price
        + hotel_total
        + food_total
        + transport_total
        + activities
    )

    return {
        "flight_cost": flight_price,
        "hotel_cost": hotel_total,
        "food_cost": food_total,
        "transport_cost": transport_total,
        "activities_cost": activities,
        "total_budget": total
    }