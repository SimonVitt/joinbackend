# Generated by Django 4.1.7 on 2023-03-30 21:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='assigned_users_group',
        ),
        migrations.AlterField(
            model_name='category',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='board.board'),
        ),
    ]