# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RatpLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('network', models.CharField(max_length=10, choices=[(b'metro', 'Metro'), (b'rer', 'RER'), (b'bus', 'Bus')])),
                ('color', models.CharField(default=b'ffffff', max_length=6)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RatpLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('line', models.ForeignKey(related_name='links', to='ratp.RatpLine')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RatpStation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('osm_id', models.BigIntegerField(unique=True)),
                ('ratp_id', models.IntegerField(null=True, blank=True)),
                ('network', models.CharField(max_length=10, choices=[(b'metro', 'Metro'), (b'rer', 'RER'), (b'bus', 'Bus')])),
                ('name', models.CharField(max_length=255)),
                ('zone', models.IntegerField(default=1)),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('lines', models.ManyToManyField(related_name='stations', through='ratp.RatpLink', to='ratp.RatpLine')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ratplink',
            name='neighbors',
            field=models.ManyToManyField(to='ratp.RatpStation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ratplink',
            name='station',
            field=models.ForeignKey(related_name='links', to='ratp.RatpStation'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='ratpline',
            unique_together=set([('name', 'network')]),
        ),
    ]
