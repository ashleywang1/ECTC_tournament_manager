from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse

from . import forms
from . import models

from collections import defaultdict
import re
import datetime

def index(request):
    context = {'tournaments' : models.Tournament.objects.order_by('-date')}
    return render(request, 'tmdb/index.html', context)

def settings(request):
    return render(request, 'tmdb/settings.html')

def tournament_create(request):
    if request.method == 'POST':
        edit_form = forms.TournamentEditForm(request.POST)
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        today = datetime.date.today()
        edit_form = forms.TournamentEditForm(initial={'date': today})
    context = {'edit_form': edit_form}
    return render(request, 'tmdb/tournament_edit.html', context)

def tournament_edit(request, tournament_slug):
    instance = get_object_or_404(models.Tournament, slug=tournament_slug)
    context = {}
    if request.method == 'POST':
        edit_form = forms.TournamentEditForm(request.POST, instance=instance)
        if edit_form.is_valid():
            tournament = edit_form.save()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        edit_form = forms.TournamentEditForm(instance=instance)
        import_form = forms.TournamentImportForm(instance=instance)
        context['import_form'] = import_form
        delete_form = forms.TournamentDeleteForm(instance=instance)
        context['delete_form'] = delete_form
    context['edit_form'] = edit_form
    return render(request, 'tmdb/tournament_edit.html', context)

def tournament_delete(request, tournament_slug):
    instance = get_object_or_404(models.Tournament, slug=tournament_slug)
    if request.method == 'POST':
        delete_form = forms.TournamentDeleteForm(request.POST,
                instance=instance)
        if delete_form.is_valid():
            instance.delete()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        delete_form = forms.TournamentDeleteForm(instance=instance)
    context = {'delete_form': delete_form, 'tournament': instance}
    return render(request, 'tmdb/tournament_delete.html', context)

def tournament_import(request, tournament_slug):
    instance = models.Tournament.objects.filter(slug=tournament_slug).first()
    if request.method == "POST":
        instance.import_tournament_organizations()
    return HttpResponseRedirect(reverse('tmdb:index'))

def tournament_dashboard(request, tournament_slug, division_slug=None):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug) 
    organizations = models.TournamentOrganization.objects.filter(
            tournament=tournament).order_by('organization__name')

    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament=tournament)
    if division_slug is not None:
        tournament_divisions = tournament_divisions.filter(
                division__slug=division_slug)

    matches = []
    for division in tournament_divisions:
        team_matches = models.TeamMatch.objects.filter(
                division=division).order_by('number')
        for team_match in team_matches:
            team_match.form = forms.MatchForm(instance=team_match)
            match_teams = []
            if team_match.blue_team is not None:
                match_teams.append(team_match.blue_team.pk)
            if team_match.red_team is not None:
                match_teams.append(team_match.red_team.pk)
            team_match.form.fields['winning_team'].queryset = \
                    models.TeamRegistration.objects.filter(pk__in=match_teams)
        matches.append((division, team_matches))

    # Information about the matches by ring.
    if 'all_matches' not in request.GET: all_matches=False
    else:
        try:
            all_matches = int(request.GET['all_matches']) > 0
        except ValueError:
            all_matches = False
    matches_by_ring = defaultdict(list)
    for match in models.TeamMatch.objects.filter(ring_number__isnull=False,
            division__tournament=tournament):
        if all_matches or match.winning_team is None:
            matches_by_ring[str(match.ring_number)].append(match)

    # Add all to the context.
    context = {
        'tournament': tournament,
        'tournament_divisions': tournament_divisions,
        'organizations': organizations,
        'matches_by_ring':sorted(matches_by_ring.items()),
        'team_matches': matches
    }
    return render(request, 'tmdb/tournament_dashboard.html', context)

def tournament_school(request, tournament_slug, school_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    organization = get_object_or_404(models.Organization, slug=school_slug)
    tournament_organization = get_object_or_404(models.TournamentOrganization,
            tournament=tournament, organization=organization)
    competitors = models.Competitor.objects.filter(
            registration=tournament_organization).order_by('name')
    team_registrations = models.TeamRegistration.objects.filter(
            tournament_division__tournament=tournament,
            team__school=organization).order_by(
                    'tournament_division__division', 'team__number')
    context = {
        'tournament_organization': tournament_organization,
        'competitors': competitors,
        'team_registrations': team_registrations,
    }
    return render(request, 'tmdb/tournament_school_competitors.html', context)

def tournament_schools(request, tournament_slug):
    context = {}
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    context['tournament'] = tournament
    if request.method == "POST":
        form = forms.SchoolRegistrationImportForm(request.POST)
        if form.is_valid():
            school_registration = models.TournamentOrganization.objects.get(
                    pk=form.cleaned_data['school_registration'])
            school_registration.import_competitors_and_teams()
            return HttpResponseRedirect(reverse('tmdb:tournament_schools',
                    args=(tournament.slug,)))
        if 'school_registration' in request.POST:
            school_registration = models.TournamentOrganization.objects.get(
                    pk=request.POST['school_registration'])
            school_registration.import_form = form
            context['organizations'] = [school_registration]
    else:
        if 'organizations' not in context:
            organizations = models.TournamentOrganization.objects.filter(
                tournament=tournament).order_by('organization__name')
            for org in organizations:
                org.import_form = forms.SchoolRegistrationImportForm(
                        initial={'school_registration': org.pk})
            context['organizations'] = organizations
    return render(request, 'tmdb/tournament_schools.html', context)

def match_list(request, tournament_slug, division_slug=None):
    if request.method == 'POST':
        match = models.TeamMatch.objects.get(pk=request.POST['team_match_id'])
        form = forms.MatchForm(request.POST, instance=match)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path)

    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament__slug=tournament_slug)
    if division_slug is not None:
        tournament_divisions = tournament_divisions.filter(
                division__slug=division_slug)

    matches = []
    for division in tournament_divisions:
        team_matches = models.TeamMatch.objects.filter(
                division=division).order_by('number')
        for team_match in team_matches:
            team_match.form = forms.MatchForm(instance=team_match)
            match_teams = []
            if team_match.blue_team is not None:
                match_teams.append(team_match.blue_team.pk)
            if team_match.red_team is not None:
                match_teams.append(team_match.red_team.pk)
            team_match.form.fields['winning_team'].queryset = \
                    models.TeamRegistration.objects.filter(pk__in=match_teams)
        matches.append((division, team_matches))
    context = {'team_matches' : matches}
    return render(request, 'tmdb/match_list.html', context)

def team_list(request, tournament_slug, division_slug=None):
    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament__slug=tournament_slug)
    if division_slug is not None:
        tournament_divisions = tournament_divisions.filter(
                division__slug=division_slug)

    division_teams = []
    for tournament_division in tournament_divisions:
        teams = models.TeamRegistration.objects.filter(
                tournament_division=tournament_division).order_by(
                        'organization').order_by('team__number')
        division_teams.append((tournament_division, teams))

    context = { 'division_teams' : division_teams }
    return render(request, 'tmdb/team_list.html', context)

seedings_form_re = re.compile('(?P<team_reg_id>[0-9]+)-seed$')
def seedings(request, tournament_slug, division_slug):
    if request.method == 'POST':
        seed_forms = []
        tournament_division_pk = request.POST["tournament_division_pk"]
        tournament_division = get_object_or_404(models.TournamentDivision,
                pk=tournament_division_pk)
        for post_field in request.POST:
            re_match = seedings_form_re.match(post_field)
            if not re_match: continue
            team_reg_id = re_match.group('team_reg_id')
            seed_form = forms.SeedingForm(request.POST, prefix=str(team_reg_id),
                    instance=models.TeamRegistration.objects.get(
                            pk=int(team_reg_id)))
            seed_forms.append(seed_form)

        if all(map(forms.SeedingForm.is_valid, seed_forms)):

            tournament_division = forms.SeedingForm.all_seeds_valid(seed_forms)

            for team in forms.SeedingForm.modified_teams(seed_forms):
                team = models.TeamRegistration.objects.get(pk=team.pk)
                team.seed = None
                team.save()

            for form in seed_forms:
                form.save()
            models.TeamMatch.create_matches_from_seeds(tournament_division)
            return HttpResponseRedirect(reverse('tmdb:tournament_dashboard',
                    args=(tournament_division.tournament.slug,)))

    else:
        tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
        tournament_division = get_object_or_404(models.TournamentDivision,
                tournament=tournament, division__slug=division_slug)
        teams = models.TeamRegistration.objects.filter(
                tournament_division=tournament_division)
        seed_forms = []
        for team in teams:
            seed_form = forms.SeedingForm(prefix=str(team.id), instance=team)
            seed_form.name = str(team)
            seed_forms.append(seed_form)

    context = {
            'seed_forms': seed_forms,
            'tournament_division': tournament_division,
            }
    return render(request, 'tmdb/seedings.html', context)

def rings(request):
    if 'all_matches' not in request.GET: all_matches=False
    else:
        try:
            all_matches = int(request.GET['all_matches']) > 0
        except ValueError:
            all_matches = False
    matches_by_ring = defaultdict(list)
    for match in models.TeamMatch.objects.filter(ring_number__isnull=False):
        if all_matches or match.winning_team is None:
            matches_by_ring[str(match.ring_number)].append(match)
    context = {'matches_by_ring' : sorted(matches_by_ring.items())}
    return render(request, 'tmdb/rings.html', context)

def registration_credentials(request):
    setting_key = models.ConfigurationSetting.REGISTRATION_CREDENTIALS
    existing_value = models.ConfigurationSetting.objects.filter(
            key=setting_key).first()
    if request.method == 'POST':
        form = forms.ConfigurationSetting(request.POST,
                instance=existing_value)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        if existing_value is not None:
            value = existing_value.value
        else:
            value = None
        form = forms.ConfigurationSetting(initial={'key': setting_key,
                'value': value})
    context = {
            "setting_name": "Registration Import Credentials",
            "form": form
    }
    return render(request, 'tmdb/configuration_setting.html', context)
