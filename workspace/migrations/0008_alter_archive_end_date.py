# Generated by Django 5.2 on 2025-05-04 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workspace", "0007_archive"),
    ]

    operations = [
        migrations.AlterField(
            model_name="archive",
            name="end_date",
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
