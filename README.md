# libero-task-similarity

## Запуск SFT

Из корня репозитория укажите путь к стенду с окружением `dart/.venv`, весами `checkpoints/pi05_libero/` и демонстрациями `data/libero_90/`.

```bash
export VLA_WORKDIR=/path/to/stand
./run.sh prepare && ./run.sh train
```

Для каждой из пяти задач обучается отдельная модель от π0.5-LIBERO, по 50 демо и 1000 шагов. [Конфиг эксперимента](configs/five_task_sft.json).
