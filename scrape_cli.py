from typing import Optional

import click

from db import init_db
from models import Season, Race
from web_scraping.divisions import scrape_divisions
from web_scraping.races import get_races, update_races_in_db
from web_scraping.seasons import scrape_hyrox_seasons, update_seasons_in_db


@click.group()
def cli():
    """
    \b
    Command-line interface for scraping HYROX data
    """
    pass


@cli.command('scrape-seasons')
@click.option(
    '--force',
    is_flag=True,
    default=False,
    help='Force re-scraping and updating all seasons, even if they already exist in the database.'
)
def scrape_seasons_command(force: Optional[bool]):
    """
    \b
    Scrape HYROX seasons and update the database.
    Example:
      $ python scrape_cli.py scrape-seasons
      $ python scrape_cli.py scrape-seasons --force
    """

    # 1. Initialize DB and get session
    session = init_db()

    # 2. Scrape the data
    scraped_seasons = scrape_hyrox_seasons()

    # 3. Update the database
    # Note: We pass the session to the update function, which closes it.
    update_seasons_in_db(session, scraped_seasons, overwrite_existing=force)


@cli.command('scrape-races')
@click.option(
    '--season',
    'season_number',
    required=True,
    type=int,
    default=None,
    help='Specify a season number to scrape races for.')
def scrape_races_command(season_number: int):
    """
    \b
    Scrape Hyrox races for a given season and update the database.
    """
    if not season_number:
        click.echo("❌ Error: --season option is required.")
        return
    # 1. Initialize DB and get session
    session = init_db()
    # 2. Get the season from the DB
    existing_season = session.query(Season).filter(Season.number == season_number).first()
    if not existing_season:
        click.echo(f"❌ Error: No season found with number {season_number}.")
        session.close()
        return
    # 3. Scrape the races for the season
    scraped_races = get_races(season_number=season_number)
    if len(scraped_races) == 0:
        click.echo(f"❌ Error: No races found for season {season_number}.")
        session.close()
        return
    click.echo(f"✅ Scraped {len(scraped_races)} races.")
    # 4. Update the database with the scraped
    update_races_in_db(session, existing_season, scraped_races)


@cli.command('scrape-divisions')
@click.option(
    '--race_name',
    required=True,
    type=str,
    default=None,
    help='Enter the race name to scrape divisions for (e.g. "HYROX Hamburg 2025").')
def scrape_divisions_command(race_name: str):
    """
    \b
    Scrape Hyrox divisions for a given race and update the database.
    """
    if not race_name:
        click.echo("❌ Error: --race_name option is required.")
        return
    # 1. Initialize DB and get session
    session = init_db()
    # 2. Get the race from the DB

    existing_race = session.query(Race).filter(Race.name == race_name).first()
    if not existing_race:
        click.echo(f"❌ Error: No race found with name '{race_name}'.")
        session.close()
        return
    # 3. Scrape the divisions for the race
    scraped_divisions = scrape_divisions(season_number=existing_race.season_number, race=existing_race)
    if len(scraped_divisions) == 0:
        click.echo(f"❌ Error: No divisions found for race '{race_name}'.")
        session.close()
        return



if __name__ == '__main__':
    cli()
