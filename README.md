# Listy
**Listy** — это минималистичное оффлайн-приложение для управления задачами. Создано как учебный проект для изучения Python и GUI-разработки.

<img width="1256" height="847" alt="Listy" src="https://github.com/user-attachments/assets/e5822bbe-67d5-4e86-85e7-8b351ca57fa1" />
<img width="1315" height="845" alt="Lipsy_dark" src="https://github.com/user-attachments/assets/d171632f-d91e-4337-83fc-5deb0ec79119" />

## Особенности (Features)
*   **Привязка к дате:** создавайте уникальный список дел для любого дня.
*   **Интерактивный календарь:** быстрая навигация и подсветка дней, на которые уже запланированы задачи.
*   **Полный контроль (CRUD):** добавляйте, редактируйте, отмечайте выполненные и удаляйте задачи.
*   **Персонализация:** поддержка темной и светлой тем для комфортной работы.
*   **Скорость:** поддержка горячих клавиш (hotkeys).
*   **Приватность:** все данные хранятся локально на вашем ПК (Offline-first).

## Технологии (Tech Stack)
*   **Язык:** Python 3.12.3
*   **Библиотека GUI:** Tkinter
*   **Хранение данных:** JSON

## Зависимости (Requirements)
*  babel==2.18.0
*  customtkinter==5.2.2
*  darkdetect==0.8.0
*  packaging==26.0
*  platformdirs==4.9.4
*  python-dateutil==2.9.0.post0
*  six==1.17.0


## 🚀 Запуск проекта
Для запуска вам понадобится установленный Python 3.12+.

1. Клонируйте репозиторий:

```bash
git clone https://github.com/breeze-git/Listy.git
```

2. Перейдите в папку проекта:

```bash
cd Listy
```

3. Создайте виртуальное окружение:

```bash
python3 -m venv listyvenv
```

4. Активируйте его:

```bash
source listyvenv/bin/activate
```

5. Установите зависимости:

```bash
pip install -r requirements.txt
```

6. Перейдите в папку app:

```bash
cd app
```

7. Запустите приложение:

```bash
python listy.py
```
