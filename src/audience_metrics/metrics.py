import statistics

def discount_price(price:float,discount:float)->float:
    final=price-discount
    return final

def first_item(items:list[str])->str:
    return items[0]

def normalize_name(name:str|None)->str:
    return name.strip()
