from django.db import migrations

SPECIES_DATA = [
    {'category_code': 'W',  'name': 'Elodea nuttallii',              'group_code': 'PL', 'taxon_key': 5329212},
    {'category_code': 'W',  'name': 'Heracleum mantegazzianum',      'group_code': 'PL', 'taxon_key': 3034825},
    {'category_code': 'W',  'name': 'Hydrocotyle ranunculoides',     'group_code': 'PL', 'taxon_key': 7978544},
    {'category_code': 'W',  'name': 'Ludwigia grandiflora',          'group_code': 'PL', 'taxon_key': 5421039},
    {'category_code': 'W',  'name': 'Impatiens glandulifera',        'group_code': 'PL', 'taxon_key': 2891770},
    {'category_code': 'W',  'name': 'Myriophyllum aquaticum',        'group_code': 'PL', 'taxon_key': 5361785},
    {'category_code': 'w',  'name': 'Orconectes limosus',            'group_code': 'CR', 'taxon_key': 2227000},
    {'category_code': 'W',  'name': 'Pacifastacus leniusculus',      'group_code': 'CR', 'taxon_key': 2226990},
    {'category_code': 'E',  'name': 'Lagarosiphon major',            'group_code': 'PL', 'taxon_key': 2865565},
    {'category_code': 'E',  'name': 'Lysichiton americanus',         'group_code': 'PL', 'taxon_key': 2869311},
    {'category_code': 'E',  'name': 'Myriophyllum heterophyllum',    'group_code': 'PL', 'taxon_key': 5361762},
    {'category_code': 'E',  'name': 'Procambarus clarkii',           'group_code': 'CR', 'taxon_key': 2227300},
    {'category_code': 'SA', 'name': 'Cabomba caroliniana',           'group_code': 'PL', 'taxon_key': 2882443},
    {'category_code': 'SA', 'name': 'Heracleum persicum',            'group_code': 'PL', 'taxon_key': 8000520},
    {'category_code': 'SA', 'name': 'Heracleum sosnowskyi',          'group_code': 'PL', 'taxon_key': 3642949},
    {'category_code': 'SA', 'name': 'Ludwigia peploides',            'group_code': 'PL', 'taxon_key': 5420991},
    {'category_code': 'SA', 'name': 'Orconectes virilis',            'group_code': 'CR', 'taxon_key': 2227064},
    {'category_code': 'SA', 'name': 'Procambarus fallax',            'group_code': 'CR', 'taxon_key': 8879526},
]


def create_species(apps, schema_editor):
    Species = apps.get_model('dashboard', 'species')

    for s in SPECIES_DATA:
        Species.objects.create(
            name=s['name'],
            gbif_taxon_key=s['taxon_key'],
            group=s['group_code'],
            category=s['category_code']
        )


def delete_species(apps, schema_editor):
    Species = apps.get_model('dashboard', 'species')

    for s in SPECIES_DATA:
        try:
            Species.objects.get(gbif_taxon_key=s['taxon_key']).delete()
        except Species.DoesNotExist:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_species, delete_species)
    ]
