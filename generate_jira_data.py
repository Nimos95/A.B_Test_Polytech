"""
Генератор данных JIRA для A/B-тестирования инструкций мультимедийных систем
Автор: [Ваше имя], Петербургский политех
Дата: 2024
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import List, Dict
import argparse
import sys
import os

class JiraDataGenerator:
    """Генератор реалистичных данных JIRA для A/B-теста"""
    
    def __init__(self, seed: int = 42):
        """Инициализация генератора"""
        np.random.seed(seed)
        random.seed(seed)
        
        # Конфигурация теста
        self.start_date = datetime(2025, 10, 1)
        self.end_date = datetime(2025, 10, 30)
        
        # Списки для реалистичности
        self.teachers = self._generate_teachers()
        self.departments = [
            'Кафедра информатики и вычислительной техники',
            'Кафедра высшей математики',
            'Кафедра общей физики',
            'Кафедра органической химии',
            'Кафедра инженерной графики',
            'Кафедра иностранных языков',
            'Кафедра экономики и менеджмента',
            'Кафедра философии и социологии',
            'Кафедра истории России',
            'Кафедра безопасности информационных систем'
        ]
        
        # JIRA поля
        self.priorities = ['Highest', 'High', 'Medium', 'Low']
        self.statuses = ['Открыта', 'В работе', 'Решена', 'Закрыта', 'Отклонена']
        self.issue_types = ['Инцидент', 'Запрос на обслуживание', 'Проблема']
        self.components = ['Проектор', 'Акустика', 'Компьютер', 'Сетевое оборудование', 'ПО', 'Другое оборудование']
        self.impact_levels = ['Критичное', 'Высокое', 'Среднее', 'Низкое']
        
        # Аудитории для теста (30 аудиторий)
        self.classrooms = self._generate_classrooms()
        
        # Распределение проблем по группам
        self.problems_config = {
            'A': {  # Контрольная группа (старая инструкция)
                'Не могу включить проектор': 0.25,
                'Нет изображения на экране': 0.20,
                'Нет звука в аудиосистеме': 0.15,
                'Не подключается ноутбук через HDMI': 0.10,
                'Не запускается мультимедийное ПО': 0.10,
                'Требуется инструкция по использованию': 0.10,
                'Другая проблема': 0.10
            },
            'B': {  # Тестовая группа (новая инструкция)
                'Не могу включить проектор': 0.10,
                'Нет изображения на экране': 0.15,
                'Нет звука в аудиосистеме': 0.10,
                'Не подключается ноутбук через HDMI': 0.08,
                'Не запускается мультимедийное ПО': 0.12,
                'Требуется инструкция по использованию': 0.05,
                'Сложность с настройкой источников': 0.20,
                'Проблема с переключением режимов': 0.10,
                'Другая проблема': 0.10
            }
        }
        
        # Имена для генерации
        self.tech_support_names = [
            'Иванов А.С.', 'Петрова М.В.', 'Сидоров Д.К.', 'Кузнецова Е.П.',
            'Васильев И.Н.', 'Смирнова О.Л.', 'Попов Р.М.', 'Федорова Т.С.'
        ]
        
    def _generate_teachers(self) -> List[str]:
        """Генерация списка преподавателей"""
        surnames = ['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Васильев', 
                   'Смирнов', 'Попов', 'Федоров', 'Морозов', 'Волков']
        initials = ['А.А.', 'Б.Б.', 'В.В.', 'Г.Г.', 'Д.Д.', 'Е.Е.', 'М.М.', 'Н.Н.', 'О.О.', 'П.П.']
        
        teachers = []
        for surname in surnames:
            for initial in initials[:3]:  # 3 варианта на фамилию
                teachers.append(f"{surname} {initial}")
        return teachers
    
    def _generate_classrooms(self) -> Dict[str, List[str]]:
        """Генерация списка аудиторий по группам"""
        classrooms_a = [f"Гл-{i:03d}" for i in range(101, 116)]  # 15 аудиторий
        classrooms_b = [f"Гл-{i:03d}" for i in range(201, 216)]  # 15 аудиторий
        
        return {
            'A': classrooms_a,
            'B': classrooms_b
        }
    
    def _generate_summary(self, problem: str, classroom: str) -> str:
        """Генерация заголовка заявки"""
        summaries = [
            f"{problem} в аудитории {classroom}",
            f"Проблема: {problem} (аудитория {classroom})",
            f"Аудитория {classroom}: {problem}",
            f"{problem}. Аудитория: {classroom}",
            f"Неисправность оборудования в {classroom}: {problem}"
        ]
        return random.choice(summaries)
    
    def _generate_description(self, problem: str, classroom: str, teacher: str, department: str) -> str:
        """Генерация детального описания проблемы"""
        templates = [
            f"""Преподаватель: {teacher}
Подразделение: {department}
Аудитория: {classroom}
Дата возникновения проблемы: {{datetime}}

Описание проблемы:
{problem}

Предпринятые действия:
{{actions}}

Контактный телефон: +7 (9{{phone}}) {{phone2}}-{{phone3}}-{{phone4}}""",

            f"""СООБЩЕНИЕ О ПРОБЛЕМЕ
------------------
Аудитория: {classroom}
Оборудование: Мультимедийный комплекс
Преподаватель: {teacher}
Кафедра: {department}

ПРОБЛЕМА:
{problem}

ВРЕМЯ ВОЗНИКНОВЕНИЯ:
{{datetime}}

ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:
{{additional_info}}

СТАТУС: Требуется вмешательство специалиста""",

            f"""ЗАЯВКА В ТЕХПОДДЕРЖКУ

1. Общие сведения:
   - Аудитория: {classroom}
   - Преподаватель: {teacher}
   - Подразделение: {department}
   - Дата/время: {{datetime}}

2. Суть проблемы:
   {problem}

3. Симптомы:
   {{symptoms}}

4. Влияние на учебный процесс:
   {{impact}}

Контакт для обратной связи: {teacher}"""
        ]
        
        template = random.choice(templates)
        phone = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        
        # Заполняем шаблон
        description = template.format(
            datetime=f"{random.randint(1, 28):02d}.03.2024 {random.randint(8, 18):02d}:{random.randint(0, 59):02d}",
            actions=random.choice([
                "Проверил подключение питания, перезагрузил оборудование",
                "Попытался использовать запасные кабели, проблема сохраняется",
                "Переключил источники сигнала, безрезультатно",
                "Проверил настройки ПО, проблема не решена"
            ]),
            phone=phone[:2],
            phone2=phone[2:5],
            phone3=phone[5:7],
            phone4=phone[7:9],
            additional_info=random.choice([
                "Проблема возникает при каждом использовании",
                "Иногда работает нормально, иногда нет",
                "Проблема появилась после обновления ПО",
                "Ранее подобных проблем не наблюдалось"
            ]),
            symptoms=random.choice([
                "Оборудование не реагирует на команды",
                "Изображение/звук появляются и пропадают",
                "Система зависает при определенных действиях",
                "Посторонние шумы в акустике"
            ]),
            impact=random.choice([
                "Занятие отменено",
                "Занятие проведено без мультимедийного оборудования",
                "Перенесено в другую аудиторию",
                "Проведено с ограничениями"
            ])
        )
        
        return description
    
    def _generate_comment(self) -> str:
        """Генерация комментариев к заявке"""
        comments = [
            "Проверил оборудование. Замена кабеля HDMI решает проблему.",
            "Требуется настройка проектора. Выполнена калибровка.",
            "Проблема в драйверах. Обновлено программное обеспечение.",
            "Оборудование исправно. Проведен инструктаж пользователя.",
            "Выявлена аппаратная неисправность. Запланирован ремонт.",
            "Временное решение применено. Заказана запасная часть.",
            "Проведена диагностика. Оборудование работает в штатном режиме.",
            "Проблема решена удаленно через систему управления.",
            "Требуется замена блока питания. Оборудование снято с эксплуатации.",
            "Настроены параметры отображения. Проблема устранена."
        ]
        return random.choice(comments)
    
    def generate_ticket(self, ticket_id: int, group: str) -> Dict:
        """Генерация одной заявки JIRA"""
        
        # Выбор аудитории
        classroom = random.choice(self.classrooms[group])
        
        # Временные метки
        created_date = self.start_date + timedelta(
            days=random.randint(0, (self.end_date - self.start_date).days),
            hours=random.randint(8, 18),
            minutes=random.randint(0, 59)
        )
        
        # Статус и время решения
        status_weights = [0.1, 0.15, 0.5, 0.2, 0.05]  # Вероятности статусов
        status = random.choices(self.statuses, weights=status_weights)[0]
        
        if status in ['Решена', 'Закрыта']:
            resolved_date = created_date + timedelta(
                hours=random.randint(1, 48),
                minutes=random.randint(0, 59)
            )
            resolution = 'Решено'
            time_to_resolve = round((resolved_date - created_date).total_seconds() / 3600, 1)
            resolved_str = resolved_date.strftime('%d/%m/%Y %H:%M')
        else:
            resolved_date = None
            resolution = ''
            time_to_resolve = None  # Используем None вместо пустой строки
            resolved_str = ''
        
        updated_date = resolved_date or created_date + timedelta(hours=random.randint(1, 72))
        
        # Выбор проблемы
        problems = list(self.problems_config[group].keys())
        weights = list(self.problems_config[group].values())
        problem = random.choices(problems, weights=weights)[0]
        
        # Генерация остальных данных
        teacher = random.choice(self.teachers)
        department = random.choice(self.departments)
        
        ticket = {
            # Стандартные поля JIRA
            'Issue Key': f"MMC-{ticket_id:04d}",
            'Issue Type': random.choice(self.issue_types),
            'Summary': self._generate_summary(problem, classroom),
            'Description': self._generate_description(problem, classroom, teacher, department),
            'Status': status,
            'Priority': random.choices(self.priorities, weights=[0.05, 0.15, 0.6, 0.2])[0],
            'Resolution': resolution,
            'Created': created_date.strftime('%d/%m/%Y %H:%M'),
            'Updated': updated_date.strftime('%d/%m/%Y %H:%M'),
            'Resolved': resolved_str,
            
            # Кастомные поля
            'Component/s': random.choice(self.components),
            'Affects Version/s': f"MMC v{random.randint(1, 3)}.{random.randint(0, 9)}",
            'Fix Version/s': f"MMC v{random.randint(1, 4)}.{random.randint(0, 9)}" if resolved_date else '',
            'Reporter': teacher,
            'Assignee': random.choice(self.tech_support_names) if random.random() > 0.4 else '',
            'Votes': random.randint(0, 3),
            'Watchers': random.choice(['', 'support_team', 'multimedia_dept']),
            'Original Estimate': f"{random.randint(1, 4)}h" if random.random() > 0.7 else '',
            'Remaining Estimate': '',
            'Time Spent': f"{random.randint(1, 6)}h" if resolved_date else '',
            'Work Ratio': random.randint(100, 500) if resolved_date else '',
            
            # Данные для A/B теста
            'Аудитория': classroom,
            'Группа A/B теста': group,
            'Категория проблемы': problem,
            'Кафедра': department,
            'Влияние на процесс': random.choice(self.impact_levels),
            'Источник заявки': random.choice(['Телефон', 'Email', 'Портал самообслуживания', 'Личное обращение']),
            'Время решения (часы)': time_to_resolve,  # Теперь None для нерешенных
            
            # Комментарии
            'Комментарии': self._generate_comment() if random.random() > 0.5 else '',
            
            # Теги
            'Labels': random.choice(['multimedia', 'equipment', 'urgent', 'training_needed', 'hardware', 'software']),
            'Environment': f"Windows {random.randint(7, 11)} / {random.choice(['Intel', 'AMD'])} CPU",
            
            # Связи с другими задачами
            'Linked Issues': f"MMC-{random.randint(900, 999):04d}" if random.random() > 0.8 else '',
            
            # Даты в разных форматах
            'Created Date': created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Resolved Date': resolved_date.strftime('%Y-%m-%d %H:%M:%S') if resolved_date else '',
            'Due Date': (created_date + timedelta(days=random.randint(1, 7))).strftime('%d/%m/%Y') if random.random() > 0.6 else '',
            
            # Дополнительные метрики
            'Количество повторов': random.randint(0, 3),
            'Сложность решения': random.choice(['Низкая', 'Средняя', 'Высокая']),
            'Тип вмешательства': random.choice(['Удаленно', 'На месте', 'Консультация']),
        }
        
        return ticket
    
    def generate_dataset(self, num_tickets: int = 300) -> pd.DataFrame:
        """Генерация полного набора данных"""
        
        print(f"Генерация {num_tickets} заявок JIRA...")
        
        tickets = []
        ticket_id = 1001
        
        # Распределение по группам (60% в A, 40% в B)
        tickets_per_group = {
            'A': int(num_tickets * 0.6),
            'B': int(num_tickets * 0.4)
        }
        
        for group in ['A', 'B']:
            for _ in range(tickets_per_group[group]):
                ticket = self.generate_ticket(ticket_id, group)
                tickets.append(ticket)
                ticket_id += 1
        
        # Создаем DataFrame
        df = pd.DataFrame(tickets)
        
        # Преобразуем 'Created' в datetime для сортировки
        df['Created_dt'] = pd.to_datetime(df['Created'], format='%d/%m/%Y %H:%M')
        df = df.sort_values('Created_dt')
        df = df.drop('Created_dt', axis=1)
        
        return df
    
    def export_formats(self, df: pd.DataFrame, output_dir: str = '.'):
        """Экспорт данных в различных форматах"""
        
        # Создаем директорию, если её нет
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 1. Полный экспорт (все поля)
        full_path = os.path.join(output_dir, 'jira_full_export.csv')
        df.to_csv(full_path, index=False, encoding='utf-8-sig', sep=',')
        
        # 2. Упрощенный экспорт для анализа
        simple_columns = [
            'Issue Key', 'Summary', 'Status', 'Priority', 'Created',
            'Аудитория', 'Группа A/B теста', 'Категория проблемы', 'Component/s',
            'Время решения (часы)', 'Кафедра', 'Влияние на процесс'
        ]
        simple_path = os.path.join(output_dir, 'jira_simple_export.csv')
        df[simple_columns].to_csv(simple_path, index=False, encoding='utf-8-sig')
        
        # 3. Агрегированные данные по аудиториям
        # Сначала создаем копию с числовыми значениями времени решения
        df_agg = df.copy()
        
        # Преобразуем 'Время решения (часы)' в числовой тип, ошибки преобразуем в NaN
        df_agg['Время решения (часы)'] = pd.to_numeric(df_agg['Время решения (часы)'], errors='coerce')
        
        # Группируем и агрегируем
        agg_data = df_agg.groupby(['Аудитория', 'Группа A/B теста']).agg({
            'Issue Key': 'count',
            'Время решения (часы)': 'mean'
        }).rename(columns={
            'Issue Key': 'Количество заявок',
            'Время решения (часы)': 'Среднее время решения'
        }).reset_index()
        
        # Округляем среднее время решения
        agg_data['Среднее время решения'] = agg_data['Среднее время решения'].round(1)
        # Заменяем NaN на прочерк
        agg_data['Среднее время решения'] = agg_data['Среднее время решения'].fillna('-')
        
        agg_path = os.path.join(output_dir, 'jira_aggregated_data.csv')
        agg_data.to_csv(agg_path, index=False, encoding='utf-8-sig')
        
        # 4. Ежедневная статистика
        df_daily = df.copy()
        df_daily['Дата'] = pd.to_datetime(df_daily['Created'], format='%d/%m/%Y %H:%M').dt.date
        daily_stats = df_daily.groupby(['Дата', 'Группа A/B теста']).size().unstack(fill_value=0).reset_index()
        daily_path = os.path.join(output_dir, 'jira_daily_stats.csv')
        daily_stats.to_csv(daily_path, index=False, encoding='utf-8-sig')
        
        return {
            'full': full_path,
            'simple': simple_path,
            'aggregated': agg_path,
            'daily': daily_path
        }

def main():
    """Основная функция скрипта"""
    
    parser = argparse.ArgumentParser(
        description='Генератор данных JIRA для A/B-тестирования инструкций мультимедийных систем',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python generate_jira_data.py --tickets 300 --output ./data
  python generate_jira_data.py --simple-only
  python generate_jira_data.py --seed 123
        """
    )
    
    parser.add_argument('--tickets', type=int, default=300,
                       help='Количество заявок для генерации (по умолчанию: 300)')
    parser.add_argument('--output', type=str, default='.',
                       help='Директория для сохранения файлов (по умолчанию: текущая)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Seed для воспроизводимости (по умолчанию: 42)')
    parser.add_argument('--simple-only', action='store_true',
                       help='Генерировать только упрощенный CSV')
    
    args = parser.parse_args()
    
    print("Генератор данных JIRA для A/B-теста")
    print("="*50)
    
    try:
        # Инициализация генератора
        generator = JiraDataGenerator(seed=args.seed)
        
        # Генерация данных
        df = generator.generate_dataset(args.tickets)
        
        # Экспорт
        if args.simple_only:
            simple_path = os.path.join(args.output, 'jira_export.csv')
            df[['Issue Key', 'Summary', 'Status', 'Priority', 'Created', 
                'Аудитория', 'Группа A/B теста', 'Категория проблемы']].to_csv(
                simple_path, index=False, encoding='utf-8-sig')
            print(f"\n✓ Данные сохранены в: {simple_path}")
        else:
            files = generator.export_formats(df, args.output)
            print("\n✓ Созданы файлы:")
            for name, path in files.items():
                print(f"  - {path}")
        
        print(f"\n✓ Всего сгенерировано {len(df)} заявок")
        print(f"✓ Период: {df['Created'].min()} - {df['Created'].max()}")
        
        # Вывод простой статистики
        print(f"\n📊 Краткая статистика:")
        print(f"   Группа A: {len(df[df['Группа A/B теста'] == 'A'])} заявок")
        print(f"   Группа B: {len(df[df['Группа A/B теста'] == 'B'])} заявок")
        print(f"   Аудиторий в тесте: {len(df['Аудитория'].unique())}")
        
        print("\n" + "="*50)
        print("✅ Генерация завершена успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()