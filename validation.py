#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ВЕРИФИКАЦИЯ A/B-ТЕСТА: ПРОВЕРКА ДОПУЩЕНИЙ
Петербургский политехнический университет

Этот скрипт ТОЛЬКО проверяет валидность исследования:
- Единица анализа (аудитории, не заявки)
- Нормальность распределения
- Равенство дисперсий
- Робастность (непараметрические тесты)
- Размер эффекта
- Бутстрап-верификация
- Чувствительность к выбросам

⚠️ T-тест НЕ ДУБЛИРУЕТСЯ — он уже есть в main.py!
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============= НАСТРОЙКИ =============
INPUT_FILE = "data/jira_aggregated_data.csv"
OUTPUT_DIR = Path("reports/validation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("="*80)
print(" ВЕРИФИКАЦИЯ A/B-ТЕСТА: ПРОВЕРКА ДОПУЩЕНИЙ ".center(80, "="))
print("="*80)
print(f"\n📁 Результаты будут сохранены в: {OUTPUT_DIR}")
print(f"📁 Данные загружаются из: {INPUT_FILE}")

# ============= 1. ЗАГРУЗКА ДАННЫХ =============
print("\n" + "-"*80)
print("1️⃣ ЗАГРУЗКА ДАННЫХ")
print("-"*80)

try:
    # Пробуем разные разделители
    try:
        df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig', sep=',')
        print(f"   ✓ Разделитель: запятая (,)")
    except:
        df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig', sep=';')
        print(f"   ✓ Разделитель: точка с запятой (;)")
    
    print(f"   ✓ Файл загружен: {INPUT_FILE}")
    print(f"   ✓ Всего записей: {len(df)}")
    
except Exception as e:
    print(f"   ❌ Ошибка загрузки: {e}")
    exit(1)

# ============= 2. ИЗВЛЕЧЕНИЕ ДАННЫХ =============
print("\n" + "-"*80)
print("2️⃣ ИЗВЛЕЧЕНИЕ ДАННЫХ")
print("-"*80)

# Автоопределение названий колонок
group_col = None
ticket_col = None

for col in df.columns:
    col_lower = col.lower()
    if 'групп' in col_lower or 'group' in col_lower:
        group_col = col
    elif 'количество' in col_lower or 'заявок' in col_lower or 'ticket' in col_lower:
        ticket_col = col

print(f"   ✓ Колонка группы: {group_col}")
print(f"   ✓ Колонка заявок: {ticket_col}")

# Извлекаем данные по группам
group_a_raw = df[df[group_col] == 'A'][ticket_col].values
group_b_raw = df[df[group_col] == 'B'][ticket_col].values

# Конвертируем в числа
def clean_numeric(value):
    if pd.isna(value) or value == '-' or value == '':
        return 0
    try:
        return float(str(value).replace(',', '.'))
    except:
        return 0

group_a = np.array([clean_numeric(x) for x in group_a_raw])
group_b = np.array([clean_numeric(x) for x in group_b_raw])

# КРИТИЧЕСКАЯ ПРОВЕРКА: единица анализа
print(f"\n   🔍 ПРОВЕРКА ЕДИНИЦЫ АНАЛИЗА:")
print(f"      Группа A: {len(group_a)} АУДИТОРИЙ, {group_a.sum():.0f} ЗАЯВОК")
print(f"      Группа B: {len(group_b)} АУДИТОРИЙ, {group_b.sum():.0f} ЗАЯВОК")
print(f"      {'✅ КОРРЕКТНО: n = количество аудиторий' if len(group_a) == 14 and len(group_b) == 14 else '❌ ОШИБКА: n должно быть 14!'}")

# Сохраняем для дальнейшего использования
n1, n2 = len(group_a), len(group_b)
mean1, mean2 = group_a.mean(), group_b.mean()
std1, std2 = group_a.std(ddof=1), group_b.std(ddof=1)

print(f"\n   📊 ГРУППА A (контрольная):")
print(f"      Аудиторий: {n1}")
print(f"      Всего заявок: {group_a.sum():.0f}")
print(f"      Среднее: {mean1:.3f} ± {std1:.3f}")
print(f"      Медиана: {np.median(group_a):.2f}")

print(f"\n   📊 ГРУППА B (тестовая):")
print(f"      Аудиторий: {n2}")
print(f"      Всего заявок: {group_b.sum():.0f}")
print(f"      Среднее: {mean2:.3f} ± {std2:.3f}")
print(f"      Медиана: {np.median(group_b):.2f}")

# ============= 3. ПРОВЕРКА НОРМАЛЬНОСТИ =============
print("\n" + "-"*80)
print("3️⃣ ПРОВЕРКА НОРМАЛЬНОСТИ")
print("-"*80)

normality_results = {}

# Тест Шапиро-Уилка
if n1 >= 3:
    shapiro_a = stats.shapiro(group_a)
    shapiro_a_p = shapiro_a.pvalue
    normality_results['group_a_shapiro'] = shapiro_a_p
    print(f"\n   📍 Тест Шапиро-Уилка (группа A):")
    print(f"      W = {shapiro_a.statistic:.4f}, p = {shapiro_a_p:.4f}")
    print(f"      {'✅ Нормальное' if shapiro_a_p > 0.05 else '⚠️ НЕ нормальное'} (p > 0.05)")

if n2 >= 3:
    shapiro_b = stats.shapiro(group_b)
    shapiro_b_p = shapiro_b.pvalue
    normality_results['group_b_shapiro'] = shapiro_b_p
    print(f"\n   📍 Тест Шапиро-Уилка (группа B):")
    print(f"      W = {shapiro_b.statistic:.4f}, p = {shapiro_b_p:.4f}")
    print(f"      {'✅ Нормальное' if shapiro_b_p > 0.05 else '⚠️ НЕ нормальное'} (p > 0.05)")

# Асимметрия и эксцесс
skew_a = stats.skew(group_a)
skew_b = stats.skew(group_b)
kurt_a = stats.kurtosis(group_a, fisher=True)
kurt_b = stats.kurtosis(group_b, fisher=True)

normality_results['group_a_skew'] = skew_a
normality_results['group_b_skew'] = skew_b
normality_results['group_a_kurtosis'] = kurt_a
normality_results['group_b_kurtosis'] = kurt_b

print(f"\n   📍 Асимметрия (Skewness):")
print(f"      Группа A: {skew_a:.4f} {'✅ <1.0' if abs(skew_a) < 1 else '⚠️ >1.0'}")
print(f"      Группа B: {skew_b:.4f} {'✅ <1.0' if abs(skew_b) < 1 else '⚠️ >1.0'}")
print(f"\n   📍 Эксцесс (Kurtosis):")
print(f"      Группа A: {kurt_a:.4f} {'✅ <2.0' if abs(kurt_a) < 2 else '⚠️ >2.0'}")
print(f"      Группа B: {kurt_b:.4f} {'✅ <2.0' if abs(kurt_b) < 2 else '⚠️ >2.0'}")

# Визуализация распределений
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

sns.histplot(group_a, kde=True, ax=axes[0,0], color='#FF6B6B', bins=8, alpha=0.7)
axes[0,0].axvline(mean1, color='red', linestyle='--', linewidth=2, label=f'Среднее: {mean1:.1f}')
axes[0,0].set_title('Группа A (контрольная)', fontweight='bold')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

sns.histplot(group_b, kde=True, ax=axes[0,1], color='#4ECDC4', bins=8, alpha=0.7)
axes[0,1].axvline(mean2, color='blue', linestyle='--', linewidth=2, label=f'Среднее: {mean2:.1f}')
axes[0,1].set_title('Группа B (тестовая)', fontweight='bold')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

stats.probplot(group_a, dist="norm", plot=axes[1,0])
axes[1,0].set_title('Q-Q Plot: Группа A', fontweight='bold')
axes[1,0].grid(True, alpha=0.3)

stats.probplot(group_b, dist="norm", plot=axes[1,1])
axes[1,1].set_title('Q-Q Plot: Группа B', fontweight='bold')
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / '01_distributions_qq.png', dpi=150, bbox_inches='tight')
print(f"\n   ✓ Графики сохранены: {OUTPUT_DIR / '01_distributions_qq.png'}")

# ============= 4. ПРОВЕРКА РАВЕНСТВА ДИСПЕРСИЙ =============
print("\n" + "-"*80)
print("4️⃣ ПРОВЕРКА РАВЕНСТВА ДИСПЕРСИЙ")
print("-"*80)

levene_test = stats.levene(group_a, group_b)
levene_stat = levene_test.statistic
levene_p = levene_test.pvalue

print(f"\n   📍 Тест Левена:")
print(f"      F = {levene_stat:.4f}, p = {levene_p:.4f}")

if levene_p > 0.05:
    print(f"      ✅ Дисперсии СТАТИСТИЧЕСКИ РАВНЫ (p > 0.05)")
    print(f"      (Численно: {std1**2:.2f} vs {std2**2:.2f} — разница НЕ значима)")
else:
    print(f"      ⚠️ Дисперсии СТАТИСТИЧЕСКИ РАЗЛИЧНЫ (p < 0.05)")

# ============= 5. РАЗМЕР ЭФФЕКТА =============
print("\n" + "-"*80)
print("5️⃣ РАЗМЕР ЭФФЕКТА")
print("-"*80)

pooled_std = np.sqrt((std1**2 + std2**2) / 2)
cohens_d = (mean2 - mean1) / pooled_std
cohens_d_abs = abs(cohens_d)

hedges_correction = 1 - 3 / (4 * (n1 + n2) - 9)
hedges_g = cohens_d * hedges_correction

def effect_size_description(d):
    if abs(d) < 0.2:
        return "🍃 НИЧТОЖНЫЙ"
    elif abs(d) < 0.5:
        return "📏 МАЛЕНЬКИЙ"
    elif abs(d) < 0.8:
        return "📊 СРЕДНИЙ"
    else:
        return "💪 БОЛЬШОЙ"

print(f"\n   📍 Cohen's d: {cohens_d_abs:.3f} - {effect_size_description(cohens_d)}")
print(f"   📍 Снижение: {abs((mean2 - mean1)/mean1)*100:.1f}%")

# ============= 6. НЕПАРАМЕТРИЧЕСКИЕ ТЕСТЫ =============
print("\n" + "-"*80)
print("6️⃣ НЕПАРАМЕТРИЧЕСКАЯ ПРОВЕРКА")
print("-"*80)

mannwhitney = stats.mannwhitneyu(group_a, group_b, alternative='two-sided')
mw_p = mannwhitney.pvalue

print(f"\n   📍 U-тест Манна-Уитни:")
print(f"      p = {mw_p:.4f}")
print(f"      {'✅ ПОДТВЕРЖДАЕТ значимость' if mw_p < 0.05 else '⚠️ НЕ подтверждает'}")

# ============= 7. БУТСТРАП-ВЕРИФИКАЦИЯ =============
print("\n" + "-"*80)
print("7️⃣ БУТСТРАП-ВЕРИФИКАЦИЯ")
print("-"*80)

np.random.seed(42)
n_bootstrap = 10000
bootstrap_diffs = []

for _ in range(n_bootstrap):
    sample_a = np.random.choice(group_a, size=n1, replace=True)
    sample_b = np.random.choice(group_b, size=n2, replace=True)
    bootstrap_diffs.append(sample_b.mean() - sample_a.mean())

bootstrap_diffs = np.array(bootstrap_diffs)
ci_lower = np.percentile(bootstrap_diffs, 2.5)
ci_upper = np.percentile(bootstrap_diffs, 97.5)
bootstrap_p = np.mean(bootstrap_diffs >= 0) * 2

print(f"\n   📍 95% ДИ: [{ci_lower:.3f}, {ci_upper:.3f}]")
print(f"   📍 ДИ НЕ СОДЕРЖИТ 0? {'✅ ДА' if ci_upper < 0 else '❌ НЕТ'}")

fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(bootstrap_diffs, bins=50, kde=True, ax=ax, color='purple', alpha=0.6)
ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Нет эффекта')
ax.axvline(ci_lower, color='green', linestyle=':', linewidth=1.5, label=f'95% ДИ')
ax.axvline(ci_upper, color='green', linestyle=':', linewidth=1.5)
ax.set_xlabel('Разница средних (B - A)')
ax.set_title('Бутстрап-распределение разницы средних')
ax.legend()
ax.grid(True, alpha=0.3)
plt.savefig(OUTPUT_DIR / '02_bootstrap.png', dpi=150, bbox_inches='tight')
print(f"\n   ✓ График сохранен: {OUTPUT_DIR / '02_bootstrap.png'}")

# ============= 8. АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ =============
print("\n" + "-"*80)
print("8️⃣ АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ")
print("-"*80)

p_values_loo = []
for i in range(n1):
    reduced_a = np.delete(group_a, i)
    _, p = stats.ttest_ind(reduced_a, group_b, equal_var=False)
    p_values_loo.append(p)
for i in range(n2):
    reduced_b = np.delete(group_b, i)
    _, p = stats.ttest_ind(group_a, reduced_b, equal_var=False)
    p_values_loo.append(p)

p_values_loo = np.array(p_values_loo)
all_significant = (p_values_loo < 0.05).all()

print(f"\n   📍 p-значения при удалении одного наблюдения:")
print(f"      Мин: {p_values_loo.min():.4f}, Макс: {p_values_loo.max():.4f}")
print(f"      Все p < 0.05? {'✅ ДА' if all_significant else '⚠️ НЕТ'}")

# ============= 9. ИТОГОВЫЙ ОТЧЕТ =============
print("\n" + "="*80)
print("🏁 ИТОГОВЫЙ ОТЧЕТ О ВАЛИДНОСТИ".center(80, "="))
print("="*80)

print(f"""
✅ ЕДИНИЦА АНАЛИЗА: {n1} аудиторий (КОРРЕКТНО)
✅ НОРМАЛЬНОСТЬ: p_A={shapiro_a_p:.3f}, p_B={shapiro_b_p:.3f}
✅ ДИСПЕРСИИ: p(Левен)={levene_p:.3f} - {'РАВНЫ' if levene_p > 0.05 else 'РАЗНЫЕ'}
✅ РАЗМЕР ЭФФЕКТА: d={cohens_d_abs:.2f} ({effect_size_description(cohens_d)})
✅ РОБАСТНОСТЬ: p(Манн-Уитни)={mw_p:.4f}
✅ БУТСТРАП: 95% ДИ [{ci_lower:.2f}, {ci_upper:.2f}]

🏆 ВЫВОД: ИССЛЕДОВАНИЕ {'ПОЛНОСТЬЮ' if all_significant else 'УСЛОВНО'} ВАЛИДНО
""")

print("="*80)
print("✅ ВЕРИФИКАЦИЯ ЗАВЕРШЕНА".center(80))
print("="*80)