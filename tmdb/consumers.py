from django.db.models.signals import post_save
from django.dispatch import receiver
from channels import Group
from channels.sessions import channel_session
from . import models

def match_updates_group_name(tournament_slug):
    return "match-updates-%s" %(tournament_slug,)

@receiver(post_save, sender=models.TeamMatch,
        dispatch_uid="update_team_matches")
def update_team_matches(sender, instance, **kwargs):
    tournament_slug = instance.division.tournament.slug
    group_name = match_updates_group_name(tournament_slug)
    message = {"text": "updated match %d" %(instance.pk,)}
    Group(group_name).send(message)

@channel_session
def match_updates_connect(message, tournament_slug):
    message.channel_session['tournament_slug'] = tournament_slug
    message.reply_channel.send({"accept": True})
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).add(message.reply_channel)

@channel_session
def match_updates_message(message, tournament_slug):
    message.channel_session['tournament_slug'] = tournament_slug
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).add(message.reply_channel)

@channel_session
def match_updates_disconnect(message):
    tournament_slug = message.channel_session['tournament_slug']
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).discard(message.reply_channel)