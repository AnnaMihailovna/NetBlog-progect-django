from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        # Это абстрактная модель:
        abstract = True
