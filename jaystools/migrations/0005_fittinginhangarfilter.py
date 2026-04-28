from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jaystools", "0004_jump_clone_filters"),
    ]

    operations = [
        migrations.CreateModel(
            name="FittingInHangarFilter",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The filter name that is shown to the admin.",
                        max_length=500,
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        help_text="The filter description that is show to end users.",
                        max_length=500,
                    ),
                ),
                (
                    "fitting_id",
                    models.PositiveBigIntegerField(
                        help_text="ID of the fitting to check (from the Fittings plugin).",
                    ),
                ),
                (
                    "ignore_cargo",
                    models.BooleanField(
                        default=True,
                        verbose_name="Ignore cargo / ammo",
                        help_text=(
                            "When enabled, Cargo, DroneBay and FighterBay items are excluded from "
                            "the check. The ship hull and fitted modules still need to match, but "
                            "the hold contents are ignored. Recommended for doctrine compliance "
                            "checks where pilots will have consumed ammo or adjusted their drones."
                        ),
                    ),
                ),
                (
                    "include_alts",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "When enabled, alts are included in the asset check. "
                            "Disable to restrict to main characters only."
                        ),
                    ),
                ),
            ],
            options={
                "verbose_name": "Fitting in hangar filter",
                "verbose_name_plural": "Fitting in hangar filters",
                "default_permissions": (),
            },
        ),
    ]

