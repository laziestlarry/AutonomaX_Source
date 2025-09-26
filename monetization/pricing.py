from typing import List, Dict, Any

def suggest_price(sales: List[Dict[str, Any]], current_price: float) -> Dict[str, Any]:
    # Simple heuristic: if conversion high, test higher; if low, test lower
    # Sales rows: {views:int, purchases:int, price:float}
    views = sum(int(r.get("views",0)) for r in sales) or 1
    purchases = sum(int(r.get("purchases",0)) for r in sales)
    conv = purchases / views
    proposed = current_price
    if conv > 0.05:
        proposed = round(current_price * 1.05, 2)
    elif conv < 0.01:
        proposed = round(max(0.1, current_price * 0.95), 2)
    return {"current_price": current_price, "suggested_price": proposed, "conversion": round(conv,4)}
