from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jaystools", "0003_characterskillpointfilter_ignore_alts"),
    ]

    operations = [
        migrations.CreateModel(
            name="JumpCloneStationFilter",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="The filter name that is shown to the admin.", max_length=500)),
                ("description", models.CharField(help_text="The filter description that is show to end users.", max_length=500)),
                ("include_alts", models.BooleanField(
                    default=True,
                    help_text="When enabled, the filter checks all characters including alts. Disable to restrict to main characters only.",
                )),
                ("location_ids", models.TextField(
                    help_text=(
                        "One station or structure ID per line (or comma-separated). "
                        "The filter passes if a character has a jump clone in any of these locations."
                    ),
                )),
            ],
            options={
                "verbose_name": "Smart Filter: Jump Clone in Station/Structure",
                "verbose_name_plural": "Smart Filter: Jump Clone in Station/Structure",
            },
        ),
        migrations.CreateModel(
            name="JumpCloneSolarSystemFilter",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="The filter name that is shown to the admin.", max_length=500)),
                ("description", models.CharField(help_text="The filter description that is show to end users.", max_length=500)),
                ("include_alts", models.BooleanField(
                    default=True,
                    help_text="When enabled, the filter checks all characters including alts. Disable to restrict to main characters only.",
                )),
                ("solar_system_ids", models.TextField(
                    help_text=(
                        "One solar system ID per line (or comma-separated). "
                        "The filter passes if a character has a jump clone in any of these solar systems."
                    ),
                )),
            ],
            options={
                "verbose_name": "Smart Filter: Jump Clone in Solar System",
                "verbose_name_plural": "Smart Filter: Jump Clone in Solar System",
            },
        ),
        migrations.CreateModel(
            name="JumpCloneConstellationFilter",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="The filter name that is shown to the admin.", max_length=500)),
                ("description", models.CharField(help_text="The filter description that is show to end users.", max_length=500)),
                ("include_alts", models.BooleanField(
                    default=True,
                    help_text="When enabled, the filter checks all characters including alts. Disable to restrict to main characters only.",
                )),
                ("constellation_ids", models.TextField(
                    help_text=(
                        "One constellation ID per line (or comma-separated). "
                        "The filter passes if a character has a jump clone anywhere in these constellations."
                    ),
                )),
            ],
            options={
                "verbose_name": "Smart Filter: Jump Clone in Constellation",
                "verbose_name_plural": "Smart Filter: Jump Clone in Constellation",
            },
        ),
        migrations.CreateModel(
            name="JumpCloneRegionFilter",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="The filter name that is shown to the admin.", max_length=500)),
                ("description", models.CharField(help_text="The filter description that is show to end users.", max_length=500)),
                ("include_alts", models.BooleanField(
                    default=True,
                    help_text="When enabled, the filter checks all characters including alts. Disable to restrict to main characters only.",
                )),
                ("region_ids", models.TextField(
                    help_text=(
                        "One region ID per line (or comma-separated). "
                        "The filter passes if a character has a jump clone anywhere in these regions."
                    ),
                )),
            ],
            options={
                "verbose_name": "Smart Filter: Jump Clone in Region",
                "verbose_name_plural": "Smart Filter: Jump Clone in Region",
            },
        ),
    ]

