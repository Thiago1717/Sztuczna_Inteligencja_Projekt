import csv
import os

class Meal:
    def __init__(self, id, name, category, kcal, protein, carbs, fat, weight):
        self.id = int(id)
        self.name = name
        self.category = category
        self.kcal = int(kcal)
        self.protein = int(protein)
        self.carbs = int(carbs)
        self.fat = int(fat)
        self.weight = int(weight)

def load_db(filepath):
    meals = []
    try:
        f = open(filepath, mode='r', encoding='utf-8-sig')
        reader = csv.DictReader(f)
        for row in reader:
            m = Meal(row['id'], row['nazwa'], row['kategoria'], row['kalorie'],
                     row['bialko'], row['wegle'], row['tluszcze'], row['gramatura'])
            meals.append(m)
        f.close()
    except UnicodeDecodeError:
        f = open(filepath, mode='r', encoding='windows-1250')
        reader = csv.DictReader(f)
        for row in reader:
            m = Meal(row['id'], row['nazwa'], row['kategoria'], row['kalorie'],
                     row['bialko'], row['wegle'], row['tluszcze'], row['gramatura'])
            meals.append(m)
        f.close()
    return meals

def generate_diet(meals, target_kcal, target_p, target_c, target_f):
    categories = ["Śniadanie", "Obiad", "Przekąska", "Kolacja"]
    meal_dict = {cat: [] for cat in categories}
    
    for m in meals:
        if m.category in meal_dict:
            meal_dict[m.category].append(m)
            
    
    bounds = {
        "Śniadanie": (0.15, 0.40),
        "Obiad":     (0.25, 0.50),
        "Kolacja":   (0.15, 0.35),
        "Przekąska": (0.05, 0.20),
    }

    filtered_dict = {}
    for cat in categories:
        filtered_dict[cat] = []
        min_pct, max_pct = bounds[cat]
        for m in meal_dict[cat]:
            if (target_kcal * min_pct) <= m.kcal <= (target_kcal * max_pct):
                filtered_dict[cat].append(m)
                
        if not filtered_dict[cat]:
            return None, f"Zbyt restrykcyjne filtry. Brak posiłków w kategorii {cat} dla Twoich proporcji."

    
    dp = {0: (0, 0, 0, [], 0)}
    tolerance = int(target_kcal * 0.15)  
    
    
    target_proportions = (target_p / target_kcal, target_c / target_kcal, target_f / target_kcal)
    
    for stage, cat in enumerate(categories, 1):
        new_dp = {}
        for m in filtered_dict[cat]:
            for w, (p, c, f, plan, _) in dp.items():
                new_w = w + m.kcal
                if new_w > target_kcal + tolerance:
                    continue
                
                new_p = p + m.protein
                new_c = c + m.carbs
                new_f = f + m.fat
                
                err_heuristic = (
                    abs(new_p - new_w * target_proportions[0]) +
                    abs(new_c - new_w * target_proportions[1]) +
                    abs(new_f - new_w * target_proportions[2])
                )
                
                
                if new_w not in new_dp:
                    new_dp[new_w] = (new_p, new_c, new_f, plan + [m], err_heuristic)
                else:
                    if err_heuristic < new_dp[new_w][4]:
                        new_dp[new_w] = (new_p, new_c, new_f, plan + [m], err_heuristic)
        
        dp = new_dp
        if not dp:
            return None, f"Nie znaleziono ciągłości planu dla algorytmu po kategorii: {cat}. Zmień proporcje kaloryczne."
            
    best_plan = None
    min_error = float('inf')
    best_macros = None
    
    for w, (p, c, f, plan, _) in dp.items():
        if target_kcal - tolerance <= w <= target_kcal + tolerance:
            
            err = (
                abs(target_kcal - w) * 1 +
                abs(target_p - p) * 4 +
                abs(target_c - c) * 4 +
                abs(target_f - f) * 9
            )
            
            ids = [x.id for x in plan]
            if len(set(ids)) < 4:
                continue

            if err < min_error:
                min_error = err
                best_plan = plan
                best_macros = (w, p, c, f)
                
    if best_plan is None:
        return None, "Algorytm nie wygenerował planu w zadanej tolerancji na końcowym kroku."
        
    return best_plan, best_macros

if __name__ == "__main__":
    filepath = "baza_posilkow.csv"
    
    if not os.path.exists(filepath):
        print(f"Brak pliku {filepath}!")
        exit(1)
        
    meals = load_db(filepath)
    
    # dane wejsciowe
    CEL_KCAL = 2000
    CEL_BIALKO = 150
    CEL_WEGLE = 250
    CEL_TLUSZCZE = 50
    
    print(f"--- Uruchamianie algorytmu (Algorytm Plecakowy) ---")
    print(f"CEL DOCELOWY: {CEL_KCAL} kcal | {CEL_BIALKO}g Białka | {CEL_WEGLE}g Węgli | {CEL_TLUSZCZE}g Tłuszczu\n")
    
    plan, macros = generate_diet(meals, CEL_KCAL, CEL_BIALKO, CEL_WEGLE, CEL_TLUSZCZE)
    
    if plan is None:
        print("BŁĄD:", macros)
    else:
        print("=== WYGENEROWANY JADŁOSPIS ===")
        for m in plan:
            print(f"- {m.category.ljust(10)}: {m.name} ({m.weight}g)")
            print(f"             [ {m.kcal} kcal | {m.protein}g B | {m.carbs}g W | {m.fat}g T ]")
            
        w, p, c, f = macros
        print("\n=== PODSUMOWANIE ===")
        print(f"WYNIK : {w} kcal | {p}g B | {c}g W | {f}g T")
        print(f"CEL   : {CEL_KCAL} kcal | {CEL_BIALKO}g B | {CEL_WEGLE}g W | {CEL_TLUSZCZE}g T")
        
        diff_kcal = w - CEL_KCAL
        diff_p = p - CEL_BIALKO
        diff_c = c - CEL_WEGLE
        diff_f = f - CEL_TLUSZCZE
        
        
        print(f"BŁĄD  : {diff_kcal:+d} kcal | {diff_p:+d}g B | {diff_c:+d}g W | {diff_f:+d}g T")
