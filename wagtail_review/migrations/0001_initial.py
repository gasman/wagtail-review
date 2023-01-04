# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-26 13:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
from django.db.migrations.recorder import MigrationRecorder
import django.db.models.deletion
from wagtail import VERSION as WAGTAIL_VERSION


def get_run_before_and_revision_model():
    # Keep the existing behaviour for Wagtail pre-4.0.
    run_before = []
    revision_model = "wagtailcore.PageRevision"
    if WAGTAIL_VERSION >= (4, 0, 0):
        # The return value of this function is used in the Migration class
        # definition, so everything in this check happens at module load time
        # (i.e. at the start of the `migrate` command).

        # Changing the core migration dependency potentially breaks existing
        # users as it can cause an InconsistentMigrationHistory error.

        # Based on the dependencies, this migration can be run both before or
        # after the PageRevision model is renamed to Revision. As a result,
        # we cannot accurately determine the revision_model to use.

        # What we can do instead is keep pointing to the old PageRevision name,
        # but use run_before to make sure that this migration is run before the
        # core migration that renames the PageRevision model.
        run_before = [("wagtailcore", "0070_rename_pagerevision_revision")]

        try:
            if MigrationRecorder.Migration.objects.filter(
                app="wagtailcore", name="0070_rename_pagerevision_revision"
            ).exists():
                # However, if the core migration has already been applied in a
                # previous `migrate` run, we should unset run_before to avoid an
                # InconsistentMigrationHistory error.

                # This might be the case if the core migration was run
                # separately and an earlier version of wagtail-localize were
                # already installed where we did not ensure this migration was
                # run before the core migration.
                run_before = []

                # In any case, it should be safe to point to the new Revision
                # model name as the core migration has already been applied.
                revision_model = "wagtailcore.Revision"

        except (django.db.utils.OperationalError, django.db.utils.ProgrammingError):
            # Normally happens when running tests
            pass

    return run_before, revision_model


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0040_page_draft_title'),
        migrations.swappable_dependency(settings.WAGTAILREVIEW_REVIEW_MODEL),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    run_before, revision_model = get_run_before_and_revision_model()

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], default='open', editable=False, max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('page_revision', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=revision_model)),
                ('submitter', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'swappable': 'WAGTAILREVIEW_REVIEW_MODEL',
            },
        ),
        migrations.CreateModel(
            name='Reviewer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('response_token', models.CharField(editable=False, help_text='Secret token this user must supply to be allowed to respond to the review', max_length=32)),
                ('view_token', models.CharField(editable=False, help_text='Secret token this user must supply to be allowed to view the page revision being reviewed', max_length=32)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.WAGTAILREVIEW_REVIEW_MODEL, related_name='reviewers')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
