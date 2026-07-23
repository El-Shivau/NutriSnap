"""
Flask CLI Commands
==================

Custom commands that can be run from the terminal via the `flask` command.
Register these commands with the app in app.py.
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
from flask import current_app
from flask.cli import with_appcontext

from backend.extensions import db
from backend.models.food_log import FoodLog

logger = logging.getLogger(__name__)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """
    Creates all database tables based on the SQLAlchemy models.
    """
    click.echo("Initialising database tables...")
    import backend.models  # Ensure all models are registered
    try:
        db.create_all()
        click.echo("All tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        click.echo(f"Error creating tables: {e}", err=True)

@click.command("clean-old-images")
@with_appcontext
def clean_old_images_command():
    """
    Find FoodLog entries older than 30 days and delete their physical
    image files to save storage space. Sets image_filename to NULL in DB.
    """
    click.echo("Starting old images cleanup job...")

    # Calculate the cutoff date (30 days ago)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
    click.echo(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Query all food logs older than the cutoff that still have an image
    logs_to_clean = (
        db.session.query(FoodLog)
        .filter(
            FoodLog.logged_at < cutoff_date,
            FoodLog.image_filename != None  # noqa: E711
        )
        .all()
    )

    if not logs_to_clean:
        click.echo("No images older than 30 days found to clean up.")
        return

    uploads_dir = Path(current_app.root_path) / "uploads"
    deleted_count = 0
    missing_count = 0

    for log in logs_to_clean:
        if log.image_filename:
            file_path = uploads_dir / log.image_filename
            try:
                if file_path.exists():
                    os.remove(file_path)
                    deleted_count += 1
                else:
                    missing_count += 1

                # Update the database record to reflect that the image was deleted
                log.image_filename = None

            except Exception as e:
                logger.error(f"Failed to delete {file_path}: {e}")
                click.echo(f"Error deleting {log.image_filename}: {e}", err=True)

    # Commit all the image_filename = None updates
    try:
        db.session.commit()
        click.echo(
            f"Cleanup complete! Deleted {deleted_count} old images. "
            f"({missing_count} were already missing from disk)."
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to commit DB changes after cleanup: {e}")
        click.echo(f"Database commit failed: {e}", err=True)


def register_cli_commands(app):
    """Register all custom CLI commands with the Flask app."""
    app.cli.add_command(clean_old_images_command)
    app.cli.add_command(init_db_command)
