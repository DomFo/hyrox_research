from typing import Optional

import click
from sqlalchemy import func

from db import init_db
from models import Season, Race, Division
from models.associations import race_divisions


# --- Assume these imports are correct based on your project structure ---


# ----------------------------------------------------------------------


# --- 1. Top-Level Group ---

@click.group()
def cli():
    """
    \b
    HYROX Data Management CLI (Click)
    ---------------------------------
    A tool for inspecting and managing the scraped HYROX data.
    """
    pass


# --- 2. Command: list-seasons ---

@cli.command('list-seasons')
def list_seasons_command():
    """Lists all seasons in the database, ordered by season number."""
    session = init_db()

    click.echo("\n🏆 All HYROX Seasons:")
    click.echo("-" * 25)

    seasons = session.query(Season).order_by(Season.number.asc()).all()

    if not seasons:
        click.echo("No seasons found in the database.")
        session.close()
        return

    for season in seasons:
        # Using the Season __repr__ for clean output
        click.echo(season)

    session.close()


# --- 3. Command: list-races ---

@cli.command('list-races')
@click.option(
    '--season',
    'season_number',
    type=int,
    default=None,
    help='Filter races by a specific season number (e.g., 8).'
)
def list_races_command(season_number: Optional[int]):
    """
    \b
    Lists all races, or filters by a specific season.
    Example:
      $ python db_cli.py list-races
      $ python db_cli.py list-races --season 8
    """
    session = init_db()

    # Handle specific season filtering
    if season_number is not None:
        season = session.query(Season).filter(Season.number == season_number).first()
        if not season:
            click.echo(f"❌ Error: No season found with number {season_number}.")
            session.close()
            return

        races = session.query(Race).filter(Race.season_id == season.id).order_by(Race.name.asc()).all()
        click.echo(f"\n🏙️ Races for Season {season.number}: {season.name}")
        click.echo("-" * 30)

        for race in races:
            click.echo(race)

    # Handle listing all races across all seasons
    else:
        seasons = session.query(Season).order_by(Season.number.asc()).all()

        for season in seasons:
            click.echo(f"\n🏙️ Races for Season {season.number}: {season.name}")
            click.echo("-" * 30)

            races = session.query(Race).filter(Race.season_id == season.id).order_by(Race.name.asc()).all()
            for race in races:
                click.echo(f"  {race}")

    session.close()


# --- 4. Command: rank-divisions ---

@cli.command('rank-divisions')
def rank_divisions_command():
    """
    \b
    Ranks divisions based on how many races they appear in.
    Useful for identifying the most common divisions.
    """
    session = init_db()

    click.echo("\n🥇 Ranking Divisions by Frequency:")
    click.echo("-" * 40)

    try:
        # This is your core SQLAlchemy query, adapted for a CLI function
        divisions = (
            session.query(Division)
            .outerjoin(race_divisions, Division.id == race_divisions.c.division_id)
            .group_by(Division.id)
            .order_by(func.count(race_divisions.c.race_id).desc())
            .all()
        )

        if not divisions:
            click.echo("No divisions found in the database.")
            session.close()
            return

        for d in divisions:
            click.echo(f"[{len(d.races):<3}] {d}")

    except Exception as e:
        click.echo(f"❌ An error occurred during ranking: {e}")

    session.close()


# --- Main Execution ---

if __name__ == '__main__':
    cli()
