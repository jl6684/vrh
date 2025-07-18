# Generated by Django 5.2.1 on 2025-06-20 15:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('biography', models.TextField(blank=True)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('formed_year', models.PositiveIntegerField(blank=True, null=True)),
                ('website', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('founded_year', models.PositiveIntegerField(blank=True, null=True)),
                ('website', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='VinylRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('release_year', models.PositiveIntegerField()),
                ('pressing_year', models.PositiveIntegerField(blank=True, null=True)),
                ('catalog_number', models.CharField(blank=True, max_length=100)),
                ('barcode', models.CharField(blank=True, max_length=50)),
                ('condition', models.CharField(choices=[('new', 'New'), ('near_mint', 'Near Mint'), ('very_good', 'Very Good'), ('good', 'Good'), ('fair', 'Fair')], default='new', max_length=20)),
                ('speed', models.CharField(choices=[('33', '33 1/3 RPM'), ('45', '45 RPM'), ('78', '78 RPM')], default='33', max_length=5)),
                ('size', models.CharField(choices=[('7', '7"'), ('10', '10"'), ('12', '12"')], default='12', max_length=5)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_quantity', models.PositiveIntegerField(default=0)),
                ('is_available', models.BooleanField(default=True)),
                ('cover_image', models.ImageField(blank=True, upload_to='vinyl_covers/')),
                ('audio_sample', models.FileField(blank=True, upload_to='audio_samples/')),
                ('description', models.TextField(blank=True)),
                ('slug', models.SlugField(blank=True, max_length=350, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('featured', models.BooleanField(default=False)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vinyl_records', to='vinyl.artist')),
                ('genre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vinyl.genre')),
                ('label', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vinyl.label')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='VinylImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='vinyl_covers/additional/')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('is_back_cover', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('vinyl_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_images', to='vinyl.vinylrecord')),
            ],
            options={
                'ordering': ['order', 'created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='vinylrecord',
            index=models.Index(fields=['artist', 'title'], name='vinyl_vinyl_artist__3a7782_idx'),
        ),
        migrations.AddIndex(
            model_name='vinylrecord',
            index=models.Index(fields=['genre'], name='vinyl_vinyl_genre_i_f0e58d_idx'),
        ),
        migrations.AddIndex(
            model_name='vinylrecord',
            index=models.Index(fields=['price'], name='vinyl_vinyl_price_d1bc76_idx'),
        ),
        migrations.AddIndex(
            model_name='vinylrecord',
            index=models.Index(fields=['release_year'], name='vinyl_vinyl_release_af17d5_idx'),
        ),
    ]
