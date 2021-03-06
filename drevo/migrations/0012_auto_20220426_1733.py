# Generated by Django 3.2.4 on 2022-04-26 09:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('drevo', '0011_alter_author_updated_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='KnowledgeGradeScale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='Наименование оценки')),
                ('low_value', models.FloatField(verbose_name='Нижнее значение')),
                ('is_low_in_range', models.BooleanField(default=False, verbose_name='Диапазон включает нижнее значение')),
                ('high_value', models.FloatField(verbose_name='Верхнее значение')),
                ('is_high_in_range', models.BooleanField(default=False, verbose_name='Диапазон включает верхнее значение')),
            ],
            options={
                'verbose_name': 'Градация',
                'verbose_name_plural': 'Шкала оценок знаний',
                'ordering': ('-high_value',),
            },
        ),
        migrations.CreateModel(
            name='RelationGradeScale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='Наименование оценки')),
                ('value', models.FloatField(verbose_name='Значение')),
            ],
            options={
                'verbose_name': 'Градация',
                'verbose_name_plural': 'Шкала оценок связей',
                'ordering': ('-value',),
            },
        ),
        migrations.AddField(
            model_name='tr',
            name='argument_type',
            field=models.BooleanField(choices=[(False, 'За'), (True, 'Против')], default=False, verbose_name='Тип довода'),
        ),
        migrations.AddField(
            model_name='tr',
            name='is_argument',
            field=models.BooleanField(default=False, verbose_name='Доказательная связь'),
        ),
        migrations.AddField(
            model_name='tz',
            name='can_be_rated',
            field=models.BooleanField(default=False, verbose_name='Возможна оценка знания'),
        ),
        migrations.CreateModel(
            name='RelationGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Дата создания')),
                ('grade', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='drevo.relationgradescale', verbose_name='Оценка связи')),
                ('relation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='drevo.relation', verbose_name='Связь')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Оценка связи',
                'verbose_name_plural': 'Оценки связей',
                'unique_together': {('user', 'relation')},
            },
        ),
        migrations.CreateModel(
            name='KnowledgeGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Дата создания')),
                ('grade', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='drevo.knowledgegradescale', verbose_name='Оценка знания')),
                ('knowledge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='drevo.znanie', verbose_name='Знание')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Оценка знания',
                'verbose_name_plural': 'Оценки знаний',
                'unique_together': {('user', 'knowledge')},
            },
        ),
    ]
