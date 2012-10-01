from sqlalchemy import *
from migrate import *

meta = MetaData()

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    dataset = Table('dataset', meta, autoload=True)

    entry_custom_html = Column('entry_custom_html', Unicode(2000))
    entry_custom_html.create(dataset) 
