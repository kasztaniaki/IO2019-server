from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from main.models import Pool


class PoolModelView(ModelView):
    datamodel = SQLAInterface(Pool)

    list_columns = ['name', 'available', 'enabled', 'description', 'OS']

    show_fieldsets = [
        (
            'Summary',
            {'fields': ['name', 'available', 'description', 'OS']}
        ),
    ]
