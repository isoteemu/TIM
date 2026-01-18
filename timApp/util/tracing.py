"""
Sentry tracing setup module.
===========================

This module configures Sentry SDK integrations for a TIM,
allowing for error tracking, performance monitoring, and tracing across
web requests, background tasks (Celery), and database operations (SQLAlchemy).

Sentry is an open-source error tracking and performance monitoring platform
that helps developers identify, diagnose, and fix issues in their applications.

See https://sentry.io/welcome/ for more information.
"""
import os
import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from timApp.util.git_utils import is_dirty

def setup_flask_sentry(app: Flask) -> None:
    """
    Set up Sentry error tracking for the Flask app.

    This function configures Sentry SDK with Flask, Celery, and SQLAlchemy
    integrations. It collects configuration from the Flask app's config
    and determines the appropriate environment based on debug/testing mode
    and git repository state.

    Configurable parameters in app.config:
    - SENTRY_DSN: The Sentry Data Source Name (DSN) for the
        Sentry project.
    - SENTRY_ENVIRONMENT: (Optional) The environment name
        (e.g., development, production). If not set, it is
        determined based on debug/testing mode and git state.
    - SENTRY_TRACES_SAMPLE_RATE: (Optional) The sample rate for
        performance tracing (default is 0.0, meaning no tracing).

    :param app: The Flask application instance.

    Example usage:
    >>> app = Flask(__name__)
    >>> app.config["SENTRY_DSN"] = "https://examplePublicKey@o0.ingest.sentry.io/0"
    >>> setup_flask_sentry(app)
    """
 
    # Collect Sentry configuration from app config
    SENTRY_DSN = app.config.get("SENTRY_DSN")
    SENTRY_TRACES_SAMPLE_RATE = app.config.get("SENTRY_TRACES_SAMPLE_RATE", 0.0)

    # Determine release version. Prefer SENTRY_RELEASE, fallback to GIT_COMMIT_SHA
    # If GIT_COMMIT_SHA is not set, release will be None, and Sentry will handle
    # try to infer it automatically from git metadata (if available).
    SENTRY_RELEASE = os.getenv("SENTRY_RELEASE", os.getenv("GIT_COMMIT_SHA", None))

    # Determine environment if not set
    # - If in debug or testing mode, set to development or testing
    # - If the git repo is dirty, set to development
    # - Otherwise, set to production
    SENTRY_ENVIRONMENT = app.config.get("SENTRY_ENVIRONMENT", None)
    if SENTRY_ENVIRONMENT is None:
        if app.config.get("DEBUG", False):
            SENTRY_ENVIRONMENT = "dev"
        elif app.config.get("TESTING", False):
            SENTRY_ENVIRONMENT = "test"
        elif is_dirty():
            SENTRY_ENVIRONMENT = "dev"
        else:
            SENTRY_ENVIRONMENT = "prod"

    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=SENTRY_ENVIRONMENT,

            # Default integrations include logging and others
            default_integrations=True,
            # Explicitly add Flask, Celery, and SQLAlchemy integrations
            integrations=[
                FlaskIntegration(), 
                CeleryIntegration(),
                SqlalchemyIntegration()
            ],

            traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,

            # Always disable sending PII to Sentry for privacy reasons
            send_default_pii=False,

            release=SENTRY_RELEASE,
        )

