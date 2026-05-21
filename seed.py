"""Seed script for development/demo use.

Usage:
    python seed.py           # create mock files and populate DB
    python seed.py --reset   # remove all socioeconomic submissions then seed
"""
from __future__ import annotations

import argparse
import os

from app import create_app
from app.extensions import db
from app.utils.seed_data import ensure_seed_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Clear socioeconomic_submissions before seeding")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.reset:
            # delete all submissions
            db.session.execute("DELETE FROM socioeconomic_submissions")
            db.session.commit()
            app.logger.info("Cleared socioeconomic_submissions table")

        ensure_seed_data(app)


if __name__ == "__main__":
    main()
