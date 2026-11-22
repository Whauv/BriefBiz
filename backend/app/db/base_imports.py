"""Import all ORM models so Alembic autogenerate sees the full metadata.

Importing ``app.models`` registers every model on ``Base.metadata`` as a side effect;
the star import also re-exports the model names. The canonical list lives in
``app.models.__all__`` so it is not duplicated here.
"""

from app.models import *  # noqa: F401, F403
