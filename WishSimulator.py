import random as rd
import numpy as np
from collections import defaultdict

class WishSimulator:
    def __init__(self):
        self.results = []
        
    def simulate_course(self, course_number):
        """Симулирует один курс (90 молитв)"""
        star3 = 0
        star4 = 0
        star5 = 0
        without4star = 0
        without5star = 0
        five_star_pulls = []
        five_star_types = []
        guaranteed_target = False
        
        course_stats = {
            'course': course_number,
            'total_wishes': 90,
            'star3': 0,
            'star4': 0,
            'star5': 0,
            'first_5star_type': None,
            'first_5star_wish': None,
            'all_5star_types': [],
            'wishes_per_5star': [],
            'pity_counters': []
        }
        
        for wish_number in range(1, 91):
            current_5star_chance = 0.6
            
            if without5star >= 70:
                progress = min(without5star - 69, 21)
                current_5star_chance = 0.6 + (99.4 * progress / 21)
            
            chance = rd.uniform(0, 100)
            item_type = None
            
            if chance > 5.1:
                star3 += 1
                without4star += 1
                without5star += 1
                item_type = "3★"
            elif current_5star_chance < chance <= 5.1:
                star4 += 1
                without4star = 0
                without5star += 1
                item_type = "4★"
            elif chance <= current_5star_chance:
                star5 += 1
                
                if guaranteed_target:
                    five_star_type = "Целевой"
                    guaranteed_target = False
                else:
                    if rd.random() < 0.5:
                        five_star_type = "Целевой"
                    else:
                        five_star_type = "Второстепенный"
                        guaranteed_target = True
                
                five_star_pulls.append(wish_number)
                five_star_types.append(five_star_type)
                
                if course_stats['first_5star_type'] is None:
                    course_stats['first_5star_type'] = five_star_type
                    course_stats['first_5star_wish'] = wish_number
                
                course_stats['all_5star_types'].append(five_star_type)
                course_stats['wishes_per_5star'].append(wish_number - (five_star_pulls[-2] if len(five_star_pulls) > 1 else 0))
                
                without5star = 0
                without4star += 1
            
            if without4star >= 10:
                star4 += 1
                without4star = 0
                without5star += 1
            
            if without5star >= 90:
                star5 += 1
                
                if guaranteed_target:
                    five_star_type = "Целевой"
                    guaranteed_target = False
                else:
                    if rd.random() < 0.5:
                        five_star_type = "Целевой"
                    else:
                        five_star_type = "Второстепенный"
                        guaranteed_target = True
                
                five_star_pulls.append(wish_number)
                five_star_types.append(five_star_type)
                
                if course_stats['first_5star_type'] is None:
                    course_stats['first_5star_type'] = five_star_type
                    course_stats['first_5star_wish'] = wish_number
                
                course_stats['all_5star_types'].append(five_star_type)
                course_stats['wishes_per_5star'].append(wish_number - (five_star_pulls[-2] if len(five_star_pulls) > 1 else 0))
                
                without5star = 0
                without4star += 1
            
            course_stats['pity_counters'].append({
                'wish': wish_number,
                'without_4star': without4star,
                'without_5star': without5star
            })
        
        course_stats.update({
            'star3': star3,
            'star4': star4,
            'star5': star5,
            'final_guaranteed': guaranteed_target,
            'final_pity_4star': without4star,
            'final_pity_5star': without5star
        })
        
        return course_stats
    
    def run_simulation(self, num_courses):
        """Запускает симуляцию указанного количества курсов"""
        print(f"\n{'='*80}")
        print(f"ЗАПУСК СИМУЛЯЦИИ {num_courses} КУРСОВ (90 молитв каждый)")
        print(f"{'='*80}")
        
        self.results = []
        for i in range(num_courses):
            if (i + 1) % 100 == 0:
                print(f"Обработано курсов: {i + 1}/{num_courses}")
            self.results.append(self.simulate_course(i + 1))
        
        self._calculate_statistics()
    
    def _calculate_statistics(self):
        """Вычисляет статистику по всем курсам"""
        if not self.results:
            return
        
        # Базовые статистики
        total_wishes = sum(course['total_wishes'] for course in self.results)
        total_star3 = sum(course['star3'] for course in self.results)
        total_star4 = sum(course['star4'] for course in self.results)
        total_star5 = sum(course['star5'] for course in self.results)
        
        # Статистика по первому 5★
        first_5star_types = [course['first_5star_type'] for course in self.results if course['first_5star_type']]
        target_first = sum(1 for t in first_5star_types if t == "Целевой")
        off_target_first = sum(1 for t in first_5star_types if t == "Второстепенный")
        
        # Собираем все интервалы между 5★
        all_wishes_per_5star = []
        for course in self.results:
            all_wishes_per_5star.extend(course['wishes_per_5star'])
        
        # Статистика по молитвам на предмет
        wishes_per_3star = total_wishes / total_star3 if total_star3 > 0 else float('inf')
        wishes_per_4star = total_wishes / total_star4 if total_star4 > 0 else float('inf')
        wishes_per_5star = total_wishes / total_star5 if total_star5 > 0 else float('inf')
        
        # Анализ выбросов и аномалий
        if all_wishes_per_5star:
            wishes_5star_array = np.array(all_wishes_per_5star)
            q1 = np.percentile(wishes_5star_array, 25)
            q3 = np.percentile(wishes_5star_array, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = wishes_5star_array[(wishes_5star_array < lower_bound) | (wishes_5star_array > upper_bound)]
        else:
            outliers = np.array([])
        
        # Вывод результатов
        print(f"\n{'='*80}")
        print(f"СТАТИСТИКА ПО {len(self.results)} КУРСАМ")
        print(f"{'='*80}")
        
        print(f"\nОБЩАЯ СТАТИСТИКА:")
        print(f"Всего молитв: {total_wishes:,}")
        print(f"3★ предметов: {total_star3:,} ({total_star3/total_wishes*100:.2f}%)")
        print(f"4★ предметов: {total_star4:,} ({total_star4/total_wishes*100:.2f}%)")
        print(f"5★ предметов: {total_star5:,} ({total_star5/total_wishes*100:.2f}%)")
        
        print(f"\nСРЕДНЕЕ КОЛИЧЕСТВО МОЛИТВ НА ПРЕДМЕТ:")
        print(f"На 3★: {wishes_per_3star:.2f} молитв")
        print(f"На 4★: {wishes_per_4star:.2f} молитв")
        print(f"На 5★: {wishes_per_5star:.2f} молитв")
        
        print(f"\nПЕРВЫЙ 5★ ПРЕДМЕТ В КУРСЕ:")
        print(f"Целевой: {target_first} курсов ({target_first/len(first_5star_types)*100:.1f}%)")
        print(f"Второстепенный: {off_target_first} курсов ({off_target_first/len(first_5star_types)*100:.1f}%)")
        print(f"Курсов без 5★: {len(self.results) - len(first_5star_types)}")
        
        if all_wishes_per_5star:
            print(f"\nСТАТИСТИКА ПО 5★ ПРЕДМЕТАМ:")
            print(f"Всего 5★: {len(all_wishes_per_5star)}")
            print(f"Средний интервал: {np.mean(all_wishes_per_5star):.2f} молитв")
            print(f"Медианный интервал: {np.median(all_wishes_per_5star):.2f} молитв")
            print(f"Минимальный интервал: {np.min(all_wishes_per_5star)} молитв")
            print(f"Максимальный интервал: {np.max(all_wishes_per_5star)} молитв")
            print(f"Стандартное отклонение: {np.std(all_wishes_per_5star):.2f} молитв")
            
            print(f"\nАНАЛИЗ ВЫБРОСОВ:")
            print(f"Выбросов (по методу IQR): {len(outliers)}")
            if len(outliers) > 0:
                print(f"Минимальный выброс: {np.min(outliers)} молитв")
                print(f"Максимальный выброс: {np.max(outliers)} молитв")
                print(f"Процент выбросов: {len(outliers)/len(all_wishes_per_5star)*100:.2f}%")
        
        # Дополнительная статистика
        courses_with_5star = sum(1 for course in self.results if course['star5'] > 0)
        courses_with_multiple_5star = sum(1 for course in self.results if course['star5'] > 1)
        
        print(f"\nДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА:")
        print(f"Курсов с хотя бы одним 5★: {courses_with_5star}/{len(self.results)} ({courses_with_5star/len(self.results)*100:.1f}%)")
        print(f"Курсов с несколькими 5★: {courses_with_multiple_5star}/{len(self.results)} ({courses_with_multiple_5star/len(self.results)*100:.1f}%)")
        
        # Распределение типов 5★
        all_5star_types = []
        for course in self.results:
            all_5star_types.extend(course['all_5star_types'])
        
        if all_5star_types:
            target_count = sum(1 for t in all_5star_types if t == "Целевой")
            off_target_count = sum(1 for t in all_5star_types if t == "Второстепенный")
            print(f"Общее соотношение 5★: Целевых {target_count/len(all_5star_types)*100:.1f}% vs Второстепенных {off_target_count/len(all_5star_types)*100:.1f}%")

def main():
    simulator = WishSimulator()
    
    print("СИМУЛЯТОР МОЛИТВ - СТАТИСТИЧЕСКИЙ АНАЛИЗ")
    print("Курс = 90 молитв")
    print("Введите количество курсов для симуляции:")
    
    while True:
        try:
            user_input = input(">> ").strip()
            
            if user_input.lower() in ['exit', 'quit', '0']:
                print("До свидания!")
                break
                
            num_courses = int(user_input)
            
            if num_courses <= 0:
                print("Пожалуйста, введите положительное число")
                continue
                
            simulator.run_simulation(num_courses)
            
            print(f"\nНажмите Enter для новой симуляции или 'exit' для выхода")
            
        except ValueError:
            print("Пожалуйста, введите корректное число")
        except KeyboardInterrupt:
            print("\nДо свидания!")
            break

if __name__ == "__main__":
    main()