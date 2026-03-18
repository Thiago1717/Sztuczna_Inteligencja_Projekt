import csv
import os
import random

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

def calculate_fitness(plan, target_kcal, target_p, target_c, target_f):
    w = sum(m.kcal for m in plan)
    p = sum(m.protein for m in plan)
    c = sum(m.carbs for m in plan)
    f = sum(m.fat for m in plan)
    
    error = (abs(target_kcal - w) * 1 +
             abs(target_p - p) * 4 +
             abs(target_c - c) * 4 +
             abs(target_f - f) * 9)
    
    ids = [m.id for m in plan]
    if len(set(ids)) < len(ids):
        error += 50000  
        
    return error, (w, p, c, f)

def generate_diet_hs(meals, target_kcal, target_p, target_c, target_f):
    categories = ["Śniadanie", "Obiad", "Przekąska", "Kolacja"]
    meal_dict = {cat: [] for cat in categories}
    
    HMS = 30        
    HMCR = 0.85     
    PAR = 0.3       
    NI = 5000       
    
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
        for m in meals:
            if m.category == cat and (target_kcal * min_pct) <= m.kcal <= (target_kcal * max_pct):
                filtered_dict[cat].append(m)
                
        if not filtered_dict[cat]:
            return None, f"Brak posiłków w kategorii {cat} dla Twoich proporcji."
            
        filtered_dict[cat].sort(key=lambda x: x.kcal)

    HM = []
    for _ in range(HMS):
        random_plan = [random.choice(filtered_dict[cat]) for cat in categories]
        err, macros = calculate_fitness(random_plan, target_kcal, target_p, target_c, target_f)
        HM.append({'plan': random_plan, 'fitness': err, 'macros': macros})
        
    for t in range(NI):
        new_plan = []
        
        for cat_idx, cat in enumerate(categories):
            r1 = random.random()
            
            if r1 <= HMCR:
                random_harmony = random.choice(HM)
                chosen_meal = random_harmony['plan'][cat_idx]
                
                r2 = random.random()
                if r2 <= PAR:
                    current_idx = filtered_dict[cat].index(chosen_meal)
                    shift = random.choice([-1, 1])
                    new_idx = max(0, min(len(filtered_dict[cat]) - 1, current_idx + shift))
                    chosen_meal = filtered_dict[cat][new_idx]
                    
                new_plan.append(chosen_meal)
            else:
                new_plan.append(random.choice(filtered_dict[cat]))
                
        new_err, new_macros = calculate_fitness(new_plan, target_kcal, target_p, target_c, target_f)
        
        worst_harmony_idx = max(range(len(HM)), key=lambda i: HM[i]['fitness'])
        worst_err = HM[worst_harmony_idx]['fitness']
        
        if new_err < worst_err:
            HM[worst_harmony_idx] = {'plan': new_plan, 'fitness': new_err, 'macros': new_macros}

    best_harmony = min(HM, key=lambda x: x['fitness'])
    
    if best_harmony['fitness'] >= 50000:
        return None, "Algorytm nie zdołał znaleźć jadłospisu bez powtarzających się posiłków."
        
    return best_harmony['plan'], best_harmony['macros']

if __name__ == "__main__":
    filepath = "baza_posilkow.csv"
    
    if not os.path.exists(filepath):
        print(f"Brak pliku {filepath}!")
        exit(1)
        
    meals = load_db(filepath)
    
    # Dane wejściowe
    CEL_KCAL = 2200
    CEL_BIALKO = 120
    CEL_WEGLE = 30
    CEL_TLUSZCZE = 177
    
    print(f"--- Uruchamianie Algorytmu Harmonicznego (Metaheurystyka) ---")
    print(f"CEL DOCELOWY: {CEL_KCAL} kcal | {CEL_BIALKO}g Białka | {CEL_WEGLE}g Węgli | {CEL_TLUSZCZE}g Tłuszczu\n")
    
    plan, macros_or_error = generate_diet_hs(meals, CEL_KCAL, CEL_BIALKO, CEL_WEGLE, CEL_TLUSZCZE)
    
    if plan is None:
        print("BŁĄD:", macros_or_error)
    else:
        print("=== WYGENEROWANY JADŁOSPIS ===")
        for m in plan:
            print(f"- {m.category.ljust(10)}: {m.name} ({m.weight}g)")
            print(f"             [ {m.kcal} kcal | {m.protein}g B | {m.carbs}g W | {m.fat}g T ]")
            
        w, p, c, f = macros_or_error
        print("\n=== PODSUMOWANIE ===")
        print(f"WYNIK : {w} kcal | {p}g B | {c}g W | {f}g T")
        print(f"CEL   : {CEL_KCAL} kcal | {CEL_BIALKO}g B | {CEL_WEGLE}g W | {CEL_TLUSZCZE}g T")
        
        diff_kcal = w - CEL_KCAL
        diff_p = p - CEL_BIALKO
        diff_c = c - CEL_WEGLE
        diff_f = f - CEL_TLUSZCZE
        
        print(f"BŁĄD  : {diff_kcal:+d} kcal | {diff_p:+d}g B | {diff_c:+d}g W | {diff_f:+d}g T")