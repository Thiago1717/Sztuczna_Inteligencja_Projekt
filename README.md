# Sztuczna Inteligencja - Projekt

**Autorzy:**
* Oliwier Bogdański (21181)
* Michał Kurpiewski (21253)
* Maja Porzycka (21296)

---

## 🥗 Kreator Diety 

Projekt w Pythonie realizujący generator optymalnego jadłospisu przy użyciu wielowymiarowego problemu plecakowego. Algorytm dobiera posiłki tak, aby zmaksymalizować wybrane wartości odżywcze, nie przekraczając narzuconych limitów.

## 📌 Główne założenia algorytmu:
* **Dane wejściowe:** Maksymalny limit kalorii oraz cele dla makroskładników (białko, tłuszcze, węglowodany).
* **Ograniczenia:** Dany produkt/posiłek z bazy może zostać wykorzystany maksymalnie 1 raz w ciągu dnia (brak powtórzeń).
* **Struktura wyniku:** Program zawsze zwraca zbilansowany plan dnia składający się z dokładnie 4 posiłków:
  * 🥞 Śniadanie
  * 🍲 Obiad
  * 🥗 Kolacja
  * 🍎 Przekąska
