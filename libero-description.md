# Задачи LIBERO

Libero содержит **130 задач**: Spatial (10), Object (10), Goal (10) и LIBERO-100, разделённый на LIBERO-90 (90) и LIBERO-10 / Long (10).


## LIBERO-Spatial — 10 задач

Пространственные отношения: одна цель, разные положения целевой миски.

| ID | Сцена | Краткое описание | Текстовый промпт (EN) |
| --- | --- | --- | --- |
| 0 | — | Перенести чёрную миску между тарелкой и рамекином на тарелку. | `pick up the black bowl between the plate and the ramekin and place it on the plate` |
| 1 | — | Перенести чёрную миску рядом с рамекином на тарелку. | `pick up the black bowl next to the ramekin and place it on the plate` |
| 2 | — | Перенести чёрную миску из центра стола на тарелку. | `pick up the black bowl from table center and place it on the plate` |
| 3 | — | Перенести чёрную миску с коробки печенья на тарелку. | `pick up the black bowl on the cookie box and place it on the plate` |
| 4 | — | Перенести чёрную миску из верхнего ящика деревянного шкафчика на тарелку. | `pick up the black bowl in the top drawer of the wooden cabinet and place it on the plate` |
| 5 | — | Перенести чёрную миску с рамекина на тарелку. | `pick up the black bowl on the ramekin and place it on the plate` |
| 6 | — | Перенести чёрную миску рядом с коробкой печенья на тарелку. | `pick up the black bowl next to the cookie box and place it on the plate` |
| 7 | — | Перенести чёрную миску с плиты на тарелку. | `pick up the black bowl on the stove and place it on the plate` |
| 8 | — | Перенести чёрную миску рядом с тарелкой на тарелку. | `pick up the black bowl next to the plate and place it on the plate` |
| 9 | — | Перенести чёрную миску с деревянного шкафчика на тарелку. | `pick up the black bowl on the wooden cabinet and place it on the plate` |

## LIBERO-Object — 10 задач

Распознавание объектов: разные продукты нужно перенести в корзину.

| ID | Сцена | Краткое описание | Текстовый промпт (EN) |
| --- | --- | --- | --- |
| 0 | — | Положить суп с макаронами-буквами в корзину. | `pick up the alphabet soup and place it in the basket` |
| 1 | — | Положить сливочный сыр в корзину. | `pick up the cream cheese and place it in the basket` |
| 2 | — | Положить салатную заправку в корзину. | `pick up the salad dressing and place it in the basket` |
| 3 | — | Положить соус барбекю в корзину. | `pick up the bbq sauce and place it in the basket` |
| 4 | — | Положить кетчуп в корзину. | `pick up the ketchup and place it in the basket` |
| 5 | — | Положить томатный соус в корзину. | `pick up the tomato sauce and place it in the basket` |
| 6 | — | Положить сливочное масло в корзину. | `pick up the butter and place it in the basket` |
| 7 | — | Положить молоко в корзину. | `pick up the milk and place it in the basket` |
| 8 | — | Положить шоколадный пудинг в корзину. | `pick up the chocolate pudding and place it in the basket` |
| 9 | — | Положить апельсиновый сок в корзину. | `pick up the orange juice and place it in the basket` |

## LIBERO-Goal — 10 задач

Разные цели в сходном окружении: перемещение предметов, открытие ящиков, включение плиты.

| ID | Сцена | Краткое описание | Текстовый промпт (EN) |
| --- | --- | --- | --- |
| 0 | — | Открыть средний ящик шкафчика. | `open the middle drawer of the cabinet` |
| 1 | — | Поставить миску на плиту. | `put the bowl on the stove` |
| 2 | — | Поставить бутылку вина на шкафчик. | `put the wine bottle on top of the cabinet` |
| 3 | — | Открыть верхний ящик и положить в него миску. | `open the top drawer and put the bowl inside` |
| 4 | — | Поставить миску на шкафчик. | `put the bowl on top of the cabinet` |
| 5 | — | Подвинуть тарелку к передней стороне плиты. | `push the plate to the front of the stove` |
| 6 | — | Положить сливочный сыр в миску. | `put the cream cheese in the bowl` |
| 7 | — | Включить плиту. | `turn on the stove` |
| 8 | — | Поставить миску на тарелку. | `put the bowl on the plate` |
| 9 | — | Положить бутылку вина на подставку. | `put the wine bottle on the rack` |

## LIBERO-90 — 90 задач

90 задач для предобучения: манипуляции предметами в кухне, гостиной и кабинете.

| ID | Сцена | Краткое описание | Текстовый промпт (EN) |
| --- | --- | --- | --- |
| 0 | KITCHEN_SCENE10 | Закрыть верхний ящик шкафчика. | `close the top drawer of the cabinet` |
| 1 | KITCHEN_SCENE10 | Закрыть верхний ящик и поставить чёрную миску на шкафчик. | `close the top drawer of the cabinet and put the black bowl on top of it` |
| 2 | KITCHEN_SCENE10 | Положить чёрную миску в верхний ящик шкафчика. | `put the black bowl in the top drawer of the cabinet` |
| 3 | KITCHEN_SCENE10 | Положить заднюю упаковку масла в верхний ящик шкафчика и закрыть его. | `put the butter at the back in the top drawer of the cabinet and close it` |
| 4 | KITCHEN_SCENE10 | Положить переднюю упаковку масла в верхний ящик шкафчика и закрыть его. | `put the butter at the front in the top drawer of the cabinet and close it` |
| 5 | KITCHEN_SCENE10 | Положить шоколадный пудинг в верхний ящик шкафчика и закрыть его. | `put the chocolate pudding in the top drawer of the cabinet and close it` |
| 6 | KITCHEN_SCENE1 | Открыть нижний ящик шкафчика. | `open the bottom drawer of the cabinet` |
| 7 | KITCHEN_SCENE1 | Открыть верхний ящик шкафчика. | `open the top drawer of the cabinet` |
| 8 | KITCHEN_SCENE1 | Открыть верхний ящик шкафчика и положить в него миску. | `open the top drawer of the cabinet and put the bowl in it` |
| 9 | KITCHEN_SCENE1 | Поставить чёрную миску на тарелку. | `put the black bowl on the plate` |
| 10 | KITCHEN_SCENE1 | Поставить чёрную миску на шкафчик. | `put the black bowl on top of the cabinet` |
| 11 | KITCHEN_SCENE2 | Открыть верхний ящик шкафчика. | `open the top drawer of the cabinet` |
| 12 | KITCHEN_SCENE2 | Поставить заднюю чёрную миску на тарелку. | `put the black bowl at the back on the plate` |
| 13 | KITCHEN_SCENE2 | Поставить переднюю чёрную миску на тарелку. | `put the black bowl at the front on the plate` |
| 14 | KITCHEN_SCENE2 | Поставить среднюю чёрную миску на тарелку. | `put the middle black bowl on the plate` |
| 15 | KITCHEN_SCENE2 | Поставить среднюю чёрную миску на шкафчик. | `put the middle black bowl on top of the cabinet` |
| 16 | KITCHEN_SCENE2 | Поставить переднюю чёрную миску на среднюю чёрную миску. | `stack the black bowl at the front on the black bowl in the middle` |
| 17 | KITCHEN_SCENE2 | Поставить среднюю чёрную миску на заднюю чёрную миску. | `stack the middle black bowl on the back black bowl` |
| 18 | KITCHEN_SCENE3 | Поставить сковороду на плиту. | `put the frying pan on the stove` |
| 19 | KITCHEN_SCENE3 | Поставить гейзерную кофеварку на плиту. | `put the moka pot on the stove` |
| 20 | KITCHEN_SCENE3 | Включить плиту. | `turn on the stove` |
| 21 | KITCHEN_SCENE3 | Включить плиту и поставить на неё сковороду. | `turn on the stove and put the frying pan on it` |
| 22 | KITCHEN_SCENE4 | Закрыть нижний ящик шкафчика. | `close the bottom drawer of the cabinet` |
| 23 | KITCHEN_SCENE4 | Закрыть нижний ящик шкафчика и открыть верхний. | `close the bottom drawer of the cabinet and open the top drawer` |
| 24 | KITCHEN_SCENE4 | Положить чёрную миску в нижний ящик шкафчика. | `put the black bowl in the bottom drawer of the cabinet` |
| 25 | KITCHEN_SCENE4 | Поставить чёрную миску на шкафчик. | `put the black bowl on top of the cabinet` |
| 26 | KITCHEN_SCENE4 | Положить бутылку вина в нижний ящик шкафчика. | `put the wine bottle in the bottom drawer of the cabinet` |
| 27 | KITCHEN_SCENE4 | Положить бутылку вина на винную подставку. | `put the wine bottle on the wine rack` |
| 28 | KITCHEN_SCENE5 | Закрыть верхний ящик шкафчика. | `close the top drawer of the cabinet` |
| 29 | KITCHEN_SCENE5 | Положить чёрную миску в верхний ящик шкафчика. | `put the black bowl in the top drawer of the cabinet` |
| 30 | KITCHEN_SCENE5 | Поставить чёрную миску на тарелку. | `put the black bowl on the plate` |
| 31 | KITCHEN_SCENE5 | Поставить чёрную миску на шкафчик. | `put the black bowl on top of the cabinet` |
| 32 | KITCHEN_SCENE5 | Положить кетчуп в верхний ящик шкафчика. | `put the ketchup in the top drawer of the cabinet` |
| 33 | KITCHEN_SCENE6 | Закрыть микроволновку. | `close the microwave` |
| 34 | KITCHEN_SCENE6 | Поставить жёлто-белую кружку перед белой кружкой. | `put the yellow and white mug to the front of the white mug` |
| 35 | KITCHEN_SCENE7 | Открыть микроволновку. | `open the microwave` |
| 36 | KITCHEN_SCENE7 | Поставить белую миску на тарелку. | `put the white bowl on the plate` |
| 37 | KITCHEN_SCENE7 | Поставить белую миску справа от тарелки. | `put the white bowl to the right of the plate` |
| 38 | KITCHEN_SCENE8 | Поставить правую гейзерную кофеварку на плиту. | `put the right moka pot on the stove` |
| 39 | KITCHEN_SCENE8 | Выключить плиту. | `turn off the stove` |
| 40 | KITCHEN_SCENE9 | Положить сковороду на полку шкафчика. | `put the frying pan on the cabinet shelf` |
| 41 | KITCHEN_SCENE9 | Положить сковороду на шкафчик. | `put the frying pan on top of the cabinet` |
| 42 | KITCHEN_SCENE9 | Положить сковороду под полку шкафчика. | `put the frying pan under the cabinet shelf` |
| 43 | KITCHEN_SCENE9 | Поставить белую миску на шкафчик. | `put the white bowl on top of the cabinet` |
| 44 | KITCHEN_SCENE9 | Включить плиту. | `turn on the stove` |
| 45 | KITCHEN_SCENE9 | Включить плиту и поставить на неё сковороду. | `turn on the stove and put the frying pan on it` |
| 46 | LIVING_ROOM_SCENE1 | Положить суп с макаронами-буквами в корзину. | `pick up the alphabet soup and put it in the basket` |
| 47 | LIVING_ROOM_SCENE1 | Положить коробку сливочного сыра в корзину. | `pick up the cream cheese box and put it in the basket` |
| 48 | LIVING_ROOM_SCENE1 | Положить кетчуп в корзину. | `pick up the ketchup and put it in the basket` |
| 49 | LIVING_ROOM_SCENE1 | Положить томатный соус в корзину. | `pick up the tomato sauce and put it in the basket` |
| 50 | LIVING_ROOM_SCENE2 | Положить суп с макаронами-буквами в корзину. | `pick up the alphabet soup and put it in the basket` |
| 51 | LIVING_ROOM_SCENE2 | Положить сливочное масло в корзину. | `pick up the butter and put it in the basket` |
| 52 | LIVING_ROOM_SCENE2 | Положить молоко в корзину. | `pick up the milk and put it in the basket` |
| 53 | LIVING_ROOM_SCENE2 | Положить апельсиновый сок в корзину. | `pick up the orange juice and put it in the basket` |
| 54 | LIVING_ROOM_SCENE2 | Положить томатный соус в корзину. | `pick up the tomato sauce and put it in the basket` |
| 55 | LIVING_ROOM_SCENE3 | Положить суп с макаронами-буквами на поднос. | `pick up the alphabet soup and put it in the tray` |
| 56 | LIVING_ROOM_SCENE3 | Положить сливочное масло на поднос. | `pick up the butter and put it in the tray` |
| 57 | LIVING_ROOM_SCENE3 | Положить сливочный сыр на поднос. | `pick up the cream cheese and put it in the tray` |
| 58 | LIVING_ROOM_SCENE3 | Положить кетчуп на поднос. | `pick up the ketchup and put it in the tray` |
| 59 | LIVING_ROOM_SCENE3 | Положить томатный соус на поднос. | `pick up the tomato sauce and put it in the tray` |
| 60 | LIVING_ROOM_SCENE4 | Перенести левую чёрную миску на поднос. | `pick up the black bowl on the left and put it in the tray` |
| 61 | LIVING_ROOM_SCENE4 | Положить шоколадный пудинг на поднос. | `pick up the chocolate pudding and put it in the tray` |
| 62 | LIVING_ROOM_SCENE4 | Положить салатную заправку на поднос. | `pick up the salad dressing and put it in the tray` |
| 63 | LIVING_ROOM_SCENE4 | Поставить левую миску на правую и перенести обе на поднос. | `stack the left bowl on the right bowl and place them in the tray` |
| 64 | LIVING_ROOM_SCENE4 | Поставить правую миску на левую и перенести обе на поднос. | `stack the right bowl on the left bowl and place them in the tray` |
| 65 | LIVING_ROOM_SCENE5 | Поставить красную кружку на левую тарелку. | `put the red mug on the left plate` |
| 66 | LIVING_ROOM_SCENE5 | Поставить красную кружку на правую тарелку. | `put the red mug on the right plate` |
| 67 | LIVING_ROOM_SCENE5 | Поставить белую кружку на левую тарелку. | `put the white mug on the left plate` |
| 68 | LIVING_ROOM_SCENE5 | Поставить жёлто-белую кружку на правую тарелку. | `put the yellow and white mug on the right plate` |
| 69 | LIVING_ROOM_SCENE6 | Положить шоколадный пудинг слева от тарелки. | `put the chocolate pudding to the left of the plate` |
| 70 | LIVING_ROOM_SCENE6 | Положить шоколадный пудинг справа от тарелки. | `put the chocolate pudding to the right of the plate` |
| 71 | LIVING_ROOM_SCENE6 | Поставить красную кружку на тарелку. | `put the red mug on the plate` |
| 72 | LIVING_ROOM_SCENE6 | Поставить белую кружку на тарелку. | `put the white mug on the plate` |
| 73 | STUDY_SCENE1 | Положить книгу в передний отсек органайзера. | `pick up the book and place it in the front compartment of the caddy` |
| 74 | STUDY_SCENE1 | Положить книгу в левый отсек органайзера. | `pick up the book and place it in the left compartment of the caddy` |
| 75 | STUDY_SCENE1 | Положить книгу в правый отсек органайзера. | `pick up the book and place it in the right compartment of the caddy` |
| 76 | STUDY_SCENE1 | Поставить жёлто-белую кружку справа от органайзера. | `pick up the yellow and white mug and place it to the right of the caddy` |
| 77 | STUDY_SCENE2 | Положить книгу в задний отсек органайзера. | `pick up the book and place it in the back compartment of the caddy` |
| 78 | STUDY_SCENE2 | Положить книгу в передний отсек органайзера. | `pick up the book and place it in the front compartment of the caddy` |
| 79 | STUDY_SCENE2 | Положить книгу в левый отсек органайзера. | `pick up the book and place it in the left compartment of the caddy` |
| 80 | STUDY_SCENE2 | Положить книгу в правый отсек органайзера. | `pick up the book and place it in the right compartment of the caddy` |
| 81 | STUDY_SCENE3 | Положить книгу в передний отсек органайзера. | `pick up the book and place it in the front compartment of the caddy` |
| 82 | STUDY_SCENE3 | Положить книгу в левый отсек органайзера. | `pick up the book and place it in the left compartment of the caddy` |
| 83 | STUDY_SCENE3 | Положить книгу в правый отсек органайзера. | `pick up the book and place it in the right compartment of the caddy` |
| 84 | STUDY_SCENE3 | Поставить красную кружку справа от органайзера. | `pick up the red mug and place it to the right of the caddy` |
| 85 | STUDY_SCENE3 | Поставить белую кружку справа от органайзера. | `pick up the white mug and place it to the right of the caddy` |
| 86 | STUDY_SCENE4 | Положить среднюю книгу на полку шкафчика. | `pick up the book in the middle and place it on the cabinet shelf` |
| 87 | STUDY_SCENE4 | Положить левую книгу на верхнюю поверхность стеллажа. | `pick up the book on the left and place it on top of the shelf` |
| 88 | STUDY_SCENE4 | Положить правую книгу на полку шкафчика. | `pick up the book on the right and place it on the cabinet shelf` |
| 89 | STUDY_SCENE4 | Положить правую книгу под полку шкафчика. | `pick up the book on the right and place it under the cabinet shelf` |

## LIBERO-10 / LIBERO-Long — 10 задач

10 длинных задач для оценки переноса знаний; вместе с LIBERO-90 составляют LIBERO-100.

| ID | Сцена | Краткое описание | Текстовый промпт (EN) |
| --- | --- | --- | --- |
| 0 | LIVING_ROOM_SCENE2 | Положить суп с макаронами-буквами и томатный соус в корзину. | `put both the alphabet soup and the tomato sauce in the basket` |
| 1 | LIVING_ROOM_SCENE2 | Положить коробку сливочного сыра и сливочное масло в корзину. | `put both the cream cheese box and the butter in the basket` |
| 2 | KITCHEN_SCENE3 | Включить плиту и поставить на неё гейзерную кофеварку. | `turn on the stove and put the moka pot on it` |
| 3 | KITCHEN_SCENE4 | Положить чёрную миску в нижний ящик шкафчика и закрыть его. | `put the black bowl in the bottom drawer of the cabinet and close it` |
| 4 | LIVING_ROOM_SCENE5 | Поставить белую кружку на левую тарелку, а жёлто-белую — на правую. | `put the white mug on the left plate and put the yellow and white mug on the right plate` |
| 5 | STUDY_SCENE1 | Положить книгу в задний отсек органайзера. | `pick up the book and place it in the back compartment of the caddy` |
| 6 | LIVING_ROOM_SCENE6 | Поставить белую кружку на тарелку, а шоколадный пудинг — справа от тарелки. | `put the white mug on the plate and put the chocolate pudding to the right of the plate` |
| 7 | LIVING_ROOM_SCENE1 | Положить суп с макаронами-буквами и коробку сливочного сыра в корзину. | `put both the alphabet soup and the cream cheese box in the basket` |
| 8 | KITCHEN_SCENE8 | Поставить обе гейзерные кофеварки на плиту. | `put both moka pots on the stove` |
| 9 | KITCHEN_SCENE6 | Поставить жёлто-белую кружку в микроволновку и закрыть её. | `put the yellow and white mug in the microwave and close it` |

## Группы задач для подсчета similarity

### Группа 1. Сцены
| Сцена | ID задач | Всего задач суммарно |
| --- | --- | --- |
|KITCHEN_SCENE| [0-45] (libero-90) + [2-3, 8-9] (libero goal)| 50 |
|LIVING_ROOM_SCENE|[46-72] (libero-90) + [0-1, 4, 6-7] (libero goal)| 32 |
|STUDY_SCENE|[73-89] (libero-90) + [5] (libero goal)| 18 |


## Источники

1. [README LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/README.md) — назначение бенчмарка, 130 задач и разделение LIBERO-100 на 90 + 10.
2. [Полный список задач: libero_suite_task_map.py](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/libero/benchmark/libero_suite_task_map.py) — состав всех пяти наборов и исходный порядок задач.
3. [API бенчмарка: benchmark/__init__.py](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/libero/benchmark/__init__.py) — формирование `Task.language` и стандартный порядок задач.
4. [BDDL-файлы задач](https://github.com/Lifelong-Robot-Learning/LIBERO/tree/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/libero/bddl_files) — сцены, объекты, начальные состояния и условия выполнения задач.
5. [Официальная страница датасетов LIBERO](https://libero-project.github.io/datasets) — состав наборов и наличие языковых спецификаций.
