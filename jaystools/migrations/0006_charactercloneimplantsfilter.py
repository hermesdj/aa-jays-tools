from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jaystools", "0005_fittinginhangarfilter"),
    ]

    operations = [
        migrations.CreateModel(
            name="CharacterCloneImplantsFilter",
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
                    "implant_ids",
                    models.TextField(
                        help_text=(
                            "Type IDs of the required implants, one per line or "
                            "comma-separated. Example: 9899, 9941 (you can look up "
                            "type IDs on EVE SDE sites such as evesde.tech or via "
                            "the in-game fitting/market browser)."
                        ),
                    ),
                ),
                (
                    "require_all",
                    models.BooleanField(
                        default=True,
                        verbose_name="Require all implants",
                        help_text=(
                            "When enabled, a clone must have ALL listed implants to "
                            "satisfy the filter. When disabled, having ANY one of the "
                            "listed implants is enough."
                        ),
                    ),
                ),
                (
                    "include_alts",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "When enabled, jump clones on all characters (including "
                            "alts) are checked. Disable to restrict to main characters "
                            "only."
                        ),
                    ),
                ),
            ],
            options={
                "verbose_name": "Character clone implants filter",
                "verbose_name_plural": "Character clone implants filters",
                "default_permissions": (),
            },
        ),
    ]

