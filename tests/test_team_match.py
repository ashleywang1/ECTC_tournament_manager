from django.test import TestCase
import tmdb.models as mdls
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

class TeamMatchTestCase(TestCase):
    def setUp(self):
        mdls.BeltRank.create_tkd_belt_ranks()
        self.division = mdls.Division(name="test_division",
                sex=mdls.SexField.FEMALE_DB_VAL)
        self.division.clean()
        self.division.save()

        self.org1 = mdls.Organization(name="org1")
        self.org1.clean()
        self.org1.save()

        self.org2 = mdls.Organization(name="org2")
        self.org2.clean()
        self.org2.save()

        self.org3 = mdls.Organization(name="org3")
        self.org3.clean()
        self.org3.save()

        self.org1_team = mdls.Team(number=1, division=self.division,
                organization = self.org1)
        self.org1_team.clean()
        self.org1_team.save()

        self.org2_team = mdls.Team(number=1, division=self.division,
                organization = self.org2)
        self.org2_team.clean()
        self.org2_team.save()

        self.org3_team = mdls.Team(number=1, division=self.division,
                organization = self.org3)
        self.org3_team.clean()
        self.org3_team.save()

    def test_root_team_match_valid(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        self.assertTrue(root_match == root_match.get_root_match(),
                "root_match.get_root_match() should return root_match")

    def test_root_team_match_duplicate(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        self.assertTrue(root_match == root_match.get_root_match(),
                "root_match.get_root_match() should return root_match")
        root_match2 = mdls.TeamMatch(division=self.division, number=2,
                parent_side=0, root_match=True)
        try:
            root_match2.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating second root_match")

    def test_duplicate_match_number(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        self.assertTrue(root_match == root_match.get_root_match(),
                "root_match.get_root_match() should return root_match")
        match2 = mdls.TeamMatch(division=self.division, number=1,
                parent=root_match, parent_side=0, root_match=False)
        match2.clean()
        try:
            match2.save()
        except IntegrityError:
            pass
        else:
            self.fail("Creating a second match with number=1 should raise"
                    + " IntegrityError")

    def test_root_team_match_invalid_parent_side(self):
        team_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=1, root_match=True)
        try:
            team_match.clean()
        except ValidationError:
            pass
        else:
            self.fail("Creating root match with parent side != 0 should"
                    + " produce ValidationError")

    def test_nonroot_team_match_valid(self):
        root_match = mdls.TeamMatch(division=self.division,
                number=1, parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        match2 = mdls.TeamMatch(division=self.division, number=2,
                parent_side=0, parent=root_match, root_match=False)
        match2.clean()
        match2.save()
        match3 = mdls.TeamMatch(division=self.division, number=3,
                parent_side=1, parent=root_match, root_match=False)
        match3.clean()
        match3.save()

    def test_nonroot_team_match_invalid_null_parent(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        match2 = mdls.TeamMatch(division=self.division, number=2,
                parent_side=0, root_match=False)
        try:
            match2.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating non-root match with"
                    + " null parent")

    def test_nonroot_team_match_invalid_parent_side(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        match2 = mdls.TeamMatch(division=self.division, number=2,
                parent_side=2, parent=root_match, root_match=False)
        try:
            match2.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating match with"
                    + " parent_side not in {0, 1}")

    def test_duplicate_nonroot_team_match(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        match2 = mdls.TeamMatch(division=self.division, number=2,
                parent_side=0, parent=root_match, root_match=False)
        match2.clean()
        match2.save()
        match3 = mdls.TeamMatch(division=self.division, number=3,
                parent_side=0, parent=root_match, root_match=False)
        try:
            match3.save()
        except IntegrityError:
            pass
        else:
            self.fail("Expected IntegrityError creating match with same"
                    + " (parent, parent_side)")

    def test_same_blue_red_team(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()

        root_match.blue_team = self.org1_team
        root_match.clean()
        root_match.save()

        root_match.red_team = self.org1_team
        try:
            root_match.clean()
        except ValidationError:
            pass
        else:
            self.fail("Calling clean() on match where blue_team == red_team"
                    + " should raise ValidationError")

    def test_set_invalid_winning_team(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True, blue_team=self.org1_team,
                red_team=self.org2_team)
        root_match.clean()
        root_match.save()

        root_match.winning_team=self.org3_team
        try:
            root_match.clean()
        except ValidationError:
            pass
        else:
            self.fail("ValidationError expected when winning_team is not"
                    + " blue_team or red_team")

    def test_set_winning_team_updates_parent(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True, blue_team=self.org1_team)
        root_match.clean()
        root_match.save()

        child_match = mdls.TeamMatch(division=self.division, number=2,
                parent_side=1, parent=root_match, root_match=False,
                blue_team=self.org2_team, red_team=self.org3_team)
        child_match.clean()
        child_match.save()

        child_match.winning_team = self.org2_team
        child_match.clean()
        child_match.save()
        self.assertEqual(self.org2_team, root_match.red_team, "Updating winner"
                + " of child match should set blue_team/red_team of parent"
                + " match")

    def test_set_parent_match_with_blue_team_already_set(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True, blue_team=self.org1_team)
        root_match.clean()
        root_match.save()

        child_match = mdls.TeamMatch(division=self.division, number=2,
                parent_side=0, parent=root_match, root_match=False,
                blue_team=self.org2_team, red_team=self.org3_team)
        try:
            child_match.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating match whose"
                    + " parent.blue_team is already filled")

    def test_set_parent_match_with_same_blue_team(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True, blue_team=self.org1_team)
        root_match.clean()
        root_match.save()

        child_match = mdls.TeamMatch(division=self.division, number=2,
                parent_side=1, parent=root_match, root_match=False,
                blue_team=self.org1_team, red_team=self.org3_team,
                winning_team=self.org3_team)
        child_match.clean()
