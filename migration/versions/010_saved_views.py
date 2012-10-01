from datetime import datetime

from sqlalchemy import *
from migrate import *

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    Table('dataset', meta, autoload=True)
    Table('account', meta, autoload=True)

    view = Table('view', meta,
        Column('id', Integer, primary_key=True),
        Column('widget', Unicode(2000)),
        Column('name', Unicode(2000)),
        Column('label', Unicode(2000)),
        Column('description', Unicode(2000)),
        Column('state', Unicode(255)),
        Column('public', Boolean),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('dataset_id', Integer, ForeignKey('dataset.id')),
        Column('account_id', Integer, ForeignKey('account.id'),
            nullable=True)
        )
    view.create()


def downgrade(migrate_engine):
    raise NotImplementedError()
