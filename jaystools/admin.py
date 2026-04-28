"""Admin registrations for jaystools smart filters."""

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from .app_settings import fittings_installed
from .app_settings import memberaudit_installed
from .app_settings import securegroups_installed
from .models.smart_filters import JumpCloneConstellationFilter
from .models.smart_filters import JumpCloneRegionFilter
from .models.smart_filters import JumpCloneSolarSystemFilter
from .models.smart_filters import JumpCloneStationFilter
from .models.smart_filters import RecruitmentFilter

if memberaudit_installed():
    from .models.smart_filters import CharacterCloneImplantsFilter
    from .models.smart_filters import CharacterSkillPointFilter

_fittings_and_memberaudit = fittings_installed() and memberaudit_installed()
if _fittings_and_memberaudit:
    from .app_settings import get_fittings_fitting_model  # noqa: E402  pylint: disable=wrong-import-position
    from .models.smart_filters import FittingInHangarFilter  # noqa: E402  pylint: disable=wrong-import-position


class RecruitmentFilterAdmin(admin.ModelAdmin):
    """Admin configuration for recruitment-based smart filters."""

    list_display = (
        "name",
        "description",
        "days",
        "recruitments_needed"
    )

    select_related = True


class CharacterSkillPointFilterAdmin(admin.ModelAdmin):
    """Admin configuration for member-audit skillpoint filters."""

    list_display = (
        "name",
        "description",
        "sp_threshold",
        "ignore_alts"
    )

    select_related = True


def _build_clone_implants_admin():
    """Build and return the CharacterCloneImplantsFilter ModelAdmin class.

    Uses a dual-list multi-select widget populated from EveType implants,
    then stores selected IDs in the model's implant_ids TextField.
    """

    def _implant_queryset():
        from eveuniverse.models import EveType  # pylint: disable=import-error,import-outside-toplevel

        return (
            EveType.objects.filter(eve_group__eve_category__name="Implant")
            .exclude(eve_group__name__iexact="Booster")
            .select_related("eve_group")
            .order_by("name")
        )

    class _ImplantModelMultipleChoiceField(forms.ModelMultipleChoiceField):
        def label_from_instance(self, obj):
            group_name = obj.eve_group.name if obj.eve_group else ""
            if group_name:
                return f"{obj.name} [{obj.id}] - {group_name}"
            return f"{obj.name} [{obj.id}]"

    class _CharacterCloneImplantsFilterAdminForm(forms.ModelForm):
        selected_implants = _ImplantModelMultipleChoiceField(
            queryset=_implant_queryset().none(),
            required=False,
            label=_("Required implants"),
            widget=FilteredSelectMultiple(verbose_name=_("Implants"), is_stacked=False),
            help_text=_("Move implants to the right column to require them for this filter."),
        )

        class Meta:
            model = CharacterCloneImplantsFilter  # pylint: disable=possibly-used-before-assignment
            fields = ("name", "description", "selected_implants", "require_all", "include_alts")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            implants_qs = _implant_queryset()
            self.fields["selected_implants"].queryset = implants_qs

            if self.instance and self.instance.pk:
                selected_ids = self.instance._required_ids()  # pylint: disable=protected-access
                self.fields["selected_implants"].initial = implants_qs.filter(id__in=selected_ids)

        def save(self, commit=True):
            obj = super().save(commit=False)
            selected_ids = sorted(
                self.cleaned_data["selected_implants"].values_list("id", flat=True)
            )
            obj.implant_ids = "\n".join(str(type_id) for type_id in selected_ids)
            if commit:
                obj.save()
            return obj

    class _CharacterCloneImplantsFilterAdmin(admin.ModelAdmin):
        """Admin configuration for jump-clone implant smart filters."""

        form = _CharacterCloneImplantsFilterAdminForm
        list_display = (
            "name",
            "description",
            "require_all",
            "include_alts",
            "selected_implants_count",
        )

        @admin.display(description="Implants")
        def selected_implants_count(self, obj):
            """Return the number of implant IDs configured for this filter."""

            return len(obj._required_ids())  # pylint: disable=protected-access

    return _CharacterCloneImplantsFilterAdmin


class JumpCloneStationFilterAdmin(admin.ModelAdmin):
    """Admin configuration for jump clone station filters."""

    list_display = ("name", "description", "include_alts")


class JumpCloneSolarSystemFilterAdmin(admin.ModelAdmin):
    """Admin configuration for jump clone solar system filters."""

    list_display = ("name", "description", "include_alts")


class JumpCloneConstellationFilterAdmin(admin.ModelAdmin):
    """Admin configuration for jump clone constellation filters."""

    list_display = ("name", "description", "include_alts")


class JumpCloneRegionFilterAdmin(admin.ModelAdmin):
    """Admin configuration for jump clone region filters."""

    list_display = ("name", "description", "include_alts")


def _build_fitting_in_hangar_admin():
    """Build and return the FittingInHangarFilter ModelAdmin class.

    Constructed at runtime so the fittings Fitting model is available.
    """

    fitting_model = get_fittings_fitting_model()  # pylint: disable=possibly-used-before-assignment

    class _FittingAdminForm(forms.ModelForm):
        """Admin form that renders a dropdown for fitting selection."""

        fitting_id = forms.ModelChoiceField(
            queryset=fitting_model.objects.all().order_by("ship_type__name_en", "name"),
            label="Fitting",
            help_text="Select the fitting that pilots must have in their hangar.",
            to_field_name="id",
        )

        class Meta:
            model = FittingInHangarFilter  # pylint: disable=possibly-used-before-assignment
            fields = "__all__"

        def clean_fitting_id(self):
            """Convert ModelChoiceField result back to a plain PK integer."""

            fitting = self.cleaned_data.get("fitting_id")
            if fitting is None:
                raise forms.ValidationError("Please select a fitting.")
            return fitting.pk

    class _FittingInHangarFilterAdmin(admin.ModelAdmin):
        """Admin configuration for fitting-in-hangar smart filters."""

        form = _FittingAdminForm
        list_display = ("name", "description", "fitting_label", "ignore_cargo", "include_alts")

        @admin.display(description="Fitting")
        def fitting_label(self, obj):
            """Display the fitting name, falling back to the raw ID if not found."""

            fitting = obj._get_fitting()  # pylint: disable=protected-access
            return str(fitting) if fitting else f"#{obj.fitting_id} (not found)"

    return _FittingInHangarFilterAdmin


if securegroups_installed():
    admin.site.register(RecruitmentFilter, RecruitmentFilterAdmin)
    admin.site.register(JumpCloneStationFilter, JumpCloneStationFilterAdmin)
    admin.site.register(JumpCloneSolarSystemFilter, JumpCloneSolarSystemFilterAdmin)
    admin.site.register(JumpCloneConstellationFilter, JumpCloneConstellationFilterAdmin)
    admin.site.register(JumpCloneRegionFilter, JumpCloneRegionFilterAdmin)

    if memberaudit_installed():
        admin.site.register(CharacterSkillPointFilter, CharacterSkillPointFilterAdmin)
        admin.site.register(CharacterCloneImplantsFilter, _build_clone_implants_admin())

    if _fittings_and_memberaudit:
        admin.site.register(FittingInHangarFilter, _build_fitting_in_hangar_admin())
