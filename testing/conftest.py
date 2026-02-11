"""
Shared pytest configuration for the testing/ directory.
Suppresses noisy deprecation warnings from third-party libraries.
"""
import warnings

# Suppress deprecation warnings from dependencies (not our code)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*class-based.*config.*")         # Pydantic V2 migration
warnings.filterwarnings("ignore", message=".*declarative_base.*")            # SQLAlchemy 2.0
warnings.filterwarnings("ignore", message=".*datetime.datetime.utcnow.*")   # Python 3.12
warnings.filterwarnings("ignore", message=".*Call to deprecated close.*")    # Redis
warnings.filterwarnings("ignore", message=".*MovedIn20Warning.*")            # SQLAlchemy


def pytest_configure(config):
    """Register additional filterwarnings via pytest's ini system."""
    config.addinivalue_line("filterwarnings", "ignore::DeprecationWarning")
    config.addinivalue_line("filterwarnings", "ignore::PendingDeprecationWarning")
